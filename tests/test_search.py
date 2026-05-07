"""
Tests for the search module.
"""

from src.indexer import InvertedIndexer
from src.search import SearchEngine


# -------------------------
# Single-word search tests
# -------------------------

def test_search_word_returns_matching_documents() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good friends")
    indexer.index_document("2", "good people")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_word("good")

    assert results == ["1", "2"]


def test_search_word_returns_empty_for_missing_word() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_word("unknown")

    assert results == []


def test_search_word_handles_empty_query() -> None:
    indexer = InvertedIndexer()

    search_engine = SearchEngine(indexer)

    results = search_engine.search_word("")

    assert results == []