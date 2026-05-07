"""
Tests for the indexer module.
"""

from src.indexer import tokenize
from src.indexer import InvertedIndexer
from src.crawler import CrawledPage

# -------------------------
# Tokenizer tests
# -------------------------

def test_tokenize_lowercases_words() -> None:
    tokens = tokenize("Good Friends")

    assert tokens == ["good", "friends"]


def test_tokenize_removes_punctuation() -> None:
    tokens = tokenize("Hello, world!")

    assert tokens == ["hello", "world"]


def test_tokenize_keeps_numbers() -> None:
    tokens = tokenize("Quote 123")

    assert tokens == ["quote", "123"]


def test_tokenize_handles_empty_text() -> None:
    tokens = tokenize("")

    assert tokens == []

# -------------------------
# Document registration tests
# -------------------------

def test_add_document_stores_metadata() -> None:
    indexer = InvertedIndexer()

    indexer.add_document(
        doc_id="1",
        url="https://quotes.toscrape.com/page/1",
    )

    assert indexer.documents["1"]["url"] == (
        "https://quotes.toscrape.com/page/1"
    )

# -------------------------
# Frequency indexing tests
# -------------------------

def test_index_document_counts_word_frequencies() -> None:
    indexer = InvertedIndexer()

    indexer.index_document(
        doc_id="1",
        text="good good friends",
    )

    assert indexer.index["good"]["1"]["frequency"] == 2
    assert indexer.index["friends"]["1"]["frequency"] == 1

# -------------------------
# Positional indexing tests
# -------------------------

def test_index_document_stores_word_positions() -> None:
    indexer = InvertedIndexer()

    indexer.index_document(
        doc_id="1",
        text="good friends are good",
    )

    assert indexer.index["good"]["1"]["positions"] == [0, 3]
    assert indexer.index["friends"]["1"]["positions"] == [1]
    assert indexer.index["are"]["1"]["positions"] == [2]

# -------------------------
# HTML page indexing tests
# -------------------------

def test_extract_text_removes_html_tags() -> None:
    html = """
    <html>
        <body>
            <h1>Hello</h1>
            <p>Good friends</p>
        </body>
    </html>
    """

    text = InvertedIndexer.extract_text(html)

    assert "Hello" in text
    assert "Good friends" in text


def test_index_page_indexes_html_content() -> None:
    indexer = InvertedIndexer()

    page = CrawledPage(
        url="https://quotes.toscrape.com/page/1",
        html="""
        <html>
            <body>
                <p>Good friends</p>
            </body>
        </html>
        """,
    )

    indexer.index_page("1", page)

    assert indexer.index["good"]["1"]["frequency"] == 1
    assert indexer.index["friends"]["1"]["frequency"] == 1

# -------------------------
# Index storage tests
# -------------------------

def test_save_and_load_index(tmp_path) -> None:
    indexer = InvertedIndexer()
    indexer.add_document("1", "https://quotes.toscrape.com/page/1")
    indexer.index_document("1", "good friends good")

    file_path = tmp_path / "index.json"
    indexer.save(file_path)

    loaded_indexer = InvertedIndexer()
    loaded_indexer.load(file_path)

    assert loaded_indexer.documents == indexer.documents
    assert loaded_indexer.index == indexer.index