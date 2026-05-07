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

# -------------------------
# Multi-word conjunctive search tests
# -------------------------

def test_search_all_terms_returns_documents_containing_all_terms() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good friends")
    indexer.index_document("2", "good people")
    indexer.index_document("3", "bad friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_all_terms("good friends")

    assert results == ["1"]


def test_search_all_terms_returns_empty_if_one_term_is_missing() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_all_terms("good unknown")

    assert results == []


def test_search_all_terms_handles_special_characters() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_all_terms("good!!! friends???")

    assert results == ["1"]

# -------------------------
# TF-IDF ranking tests
# -------------------------

def test_calculate_tfidf_score_prefers_higher_term_frequency() -> None:
    indexer = InvertedIndexer()

    indexer.add_document("1", "url1")
    indexer.add_document("2", "url2")
    indexer.index_document("1", "rare rare")
    indexer.index_document("2", "rare")

    search_engine = SearchEngine(indexer)

    score_1 = search_engine.calculate_tfidf_score("1", ["rare"])
    score_2 = search_engine.calculate_tfidf_score("2", ["rare"])

    assert score_1 > score_2


def test_calculate_tfidf_score_returns_zero_for_empty_index() -> None:
    indexer = InvertedIndexer()
    search_engine = SearchEngine(indexer)

    score = search_engine.calculate_tfidf_score("1", ["good"])

    assert score == 0.0

# -------------------------
# Ranked retrieval tests
# -------------------------

def test_search_ranked_orders_documents_by_score() -> None:
    indexer = InvertedIndexer()

    indexer.add_document("1", "url1")
    indexer.add_document("2", "url2")

    indexer.index_document("1", "good good good friends")
    indexer.index_document("2", "good friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_ranked("good")

    assert results[0][0] == "1"
    assert results[0][1] > results[1][1]


def test_search_ranked_returns_empty_for_unknown_query() -> None:
    indexer = InvertedIndexer()

    search_engine = SearchEngine(indexer)

    results = search_engine.search_ranked("unknown")

    assert results == []
