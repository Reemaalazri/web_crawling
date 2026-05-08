"""
Tests for the command-line interface helper functions in main.py.
"""

from unittest.mock import Mock, patch

from src.crawler import CrawledPage
from src.indexer import InvertedIndexer
from src import main


def test_print_index_entry_handles_empty_query(capsys):
    indexer = InvertedIndexer()

    main.print_index_entry(indexer, "")

    output = capsys.readouterr().out
    assert "Please provide a word or phrase to print." in output


def test_print_index_entry_prints_single_word(capsys):
    indexer = InvertedIndexer()
    indexer.index_document("1", "love love life")

    main.print_index_entry(indexer, "love")

    output = capsys.readouterr().out
    assert "love:" in output
    assert "frequency" in output


def test_print_index_entry_handles_missing_word(capsys):
    indexer = InvertedIndexer()
    indexer.index_document("1", "love life")

    main.print_index_entry(indexer, "unknown")

    output = capsys.readouterr().out
    assert "No index entry found for 'unknown'." in output


def test_print_index_entry_prints_phrase_match(capsys):
    indexer = InvertedIndexer()
    indexer.add_document("1", "https://example.com")
    indexer.index_document("1", "good friends are here")

    main.print_index_entry(indexer, "good friends")

    output = capsys.readouterr().out
    assert "Exact phrase index matches found." in output
    assert "https://example.com" in output


def test_print_index_entry_rejects_wrong_phrase_order(capsys):
    indexer = InvertedIndexer()
    indexer.add_document("1", "https://example.com")
    indexer.index_document("1", "good friends are here")

    main.print_index_entry(indexer, "friends good")

    output = capsys.readouterr().out
    assert "No exact phrase index match found" in output


def test_find_query_handles_empty_query(capsys):
    indexer = InvertedIndexer()

    main.find_query(indexer, "")

    output = capsys.readouterr().out
    assert "Please provide a query to find." in output


def test_find_query_prints_ranked_results(capsys):
    indexer = InvertedIndexer()
    indexer.add_document("1", "https://example.com", "love life snippet")
    indexer.index_document("1", "love life")

    main.find_query(indexer, "love")

    output = capsys.readouterr().out
    assert "Ranked results found." in output
    assert "https://example.com" in output
    assert "Score:" in output


def test_find_query_prints_suggestions(capsys):
    indexer = InvertedIndexer()
    indexer.index_document("1", "friends forever")

    main.find_query(indexer, "frinds")

    output = capsys.readouterr().out
    assert "No results found." in output
    assert "Suggestions:" in output
    assert "friends" in output


def test_make_query_snippet_centres_query():
    text = (
        "This is some text before. "
        "Good friends are important. This is after."
    )

    snippet = main.make_query_snippet(text, "good friends")

    assert "Good friends" in snippet


def test_load_index_handles_missing_file(capsys, tmp_path):
    fake_index = tmp_path / "missing.json"

    with patch.object(main, "INDEX_FILE", fake_index):
        indexer = main.load_index()

    output = capsys.readouterr().out
    assert "No saved index found. Run 'build' first." in output
    assert indexer.get_total_documents() == 0


def test_build_index_saves_crawled_pages(capsys, tmp_path):
    fake_index = tmp_path / "index.json"
    fake_pages = [
        CrawledPage(
            url="https://example.com",
            html=(
                '<div class="quote"><span class="text">Good friends</span>'
                '<small class="author">Mark Twain</small></div>'
            ),
        )
    ]

    mock_crawler = Mock()
    mock_crawler.crawl.return_value = fake_pages

    with patch.object(main, "INDEX_FILE", fake_index), patch.object(
        main,
        "WebCrawler",
        return_value=mock_crawler
    ):
        indexer = main.build_index()

    output = capsys.readouterr().out
    assert "Built index for 1 pages." in output
    assert fake_index.exists()
    assert indexer.get_total_documents() == 1


def test_run_shell_exit(capsys):
    with patch("builtins.input", side_effect=["exit"]):
        main.run_shell()

    output = capsys.readouterr().out
    assert "COMP3011 Search Engine Tool" in output
    assert "Goodbye." in output


def test_run_shell_unknown_command(capsys):
    with patch("builtins.input", side_effect=["hello", "exit"]):
        main.run_shell()

    output = capsys.readouterr().out
    assert "Unknown command." in output
    assert "Goodbye." in output


def test_run_shell_build_command(capsys):
    with patch("builtins.input", side_effect=["build", "exit"]):
        with patch("src.main.build_index"):
            main.run_shell()

    output = capsys.readouterr().out
    assert "COMP3011 Search Engine Tool" in output


def test_run_shell_load_command(capsys):
    with patch("builtins.input", side_effect=["load", "exit"]):
        with patch("src.main.load_index"):
            main.run_shell()

    output = capsys.readouterr().out
    assert "Goodbye." in output


def test_run_shell_print_command(capsys):
    with patch("builtins.input", side_effect=["print love", "exit"]):
        with patch("src.main.print_index_entry"):
            main.run_shell()

    output = capsys.readouterr().out
    assert "Goodbye." in output


def test_run_shell_find_command(capsys):
    with patch("builtins.input", side_effect=["find love", "exit"]):
        with patch("src.main.find_query"):
            main.run_shell()

    output = capsys.readouterr().out
    assert "Goodbye." in output


def test_run_shell_empty_command(capsys):
    with patch("builtins.input", side_effect=["", "exit"]):
        main.run_shell()

    output = capsys.readouterr().out
    assert "Please enter a command." in output
