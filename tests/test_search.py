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

# -------------------------
# Exact phrase matching tests
# -------------------------

def test_contains_exact_phrase_returns_true_for_adjacent_terms() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends are here")

    search_engine = SearchEngine(indexer)

    assert search_engine.contains_exact_phrase("1", ["good", "friends"])


def test_contains_exact_phrase_returns_false_for_non_adjacent_terms() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good people are friends")

    search_engine = SearchEngine(indexer)

    assert not search_engine.contains_exact_phrase("1", ["good", "friends"])


def test_contains_exact_phrase_returns_false_for_empty_tokens() -> None:
    indexer = InvertedIndexer()
    search_engine = SearchEngine(indexer)

    assert not search_engine.contains_exact_phrase("1", [])

# -------------------------
# Phrase search tests
# -------------------------

def test_search_phrase_returns_matching_documents() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good friends are here")
    indexer.index_document("2", "good people are friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_phrase("good friends")

    assert results == ["1"]


def test_search_phrase_returns_empty_for_missing_phrase() -> None:
    indexer = InvertedIndexer()

    indexer.index_document("1", "good people are friends")

    search_engine = SearchEngine(indexer)

    results = search_engine.search_phrase("good friends")

    assert results == []


def test_search_phrase_handles_empty_query() -> None:
    indexer = InvertedIndexer()

    search_engine = SearchEngine(indexer)

    results = search_engine.search_phrase("")

    assert results == []

# -------------------------
# Query suggestion tests
# -------------------------

def test_suggest_terms_returns_close_match_for_misspelling() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends forever")

    search_engine = SearchEngine(indexer)

    suggestions = search_engine.suggest_terms("frinds")

    assert "friends" in suggestions


def test_suggest_terms_returns_empty_for_known_term() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    suggestions = search_engine.suggest_terms("friends")

    assert suggestions == []


def test_suggest_terms_handles_empty_query() -> None:
    indexer = InvertedIndexer()
    search_engine = SearchEngine(indexer)

    suggestions = search_engine.suggest_terms("")

    assert suggestions == []

# -------------------------
# Full find query tests
# -------------------------

def test_find_returns_exact_phrase_matches_first() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends are here")
    indexer.index_document("2", "good people are friends")

    search_engine = SearchEngine(indexer)

    response = search_engine.find("good friends")

    assert response["message"] == "Exact phrase matches found."
    assert response["results"] == [("1", "exact_phrase")]


def test_find_falls_back_to_ranked_results() -> None:
    indexer = InvertedIndexer()
    indexer.add_document("1", "url1")
    indexer.add_document("2", "url2")
    indexer.index_document("1", "good people are friends")
    indexer.index_document("2", "good people")

    search_engine = SearchEngine(indexer)

    response = search_engine.find("good friends")

    assert response["message"] == "Ranked results found."
    assert response["results"]


def test_find_returns_suggestions_when_no_results() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    response = search_engine.find("frinds")

    assert response["message"] == "No results found."
    assert "friends" in response["suggestions"]


def test_find_handles_empty_query() -> None:
    indexer = InvertedIndexer()
    search_engine = SearchEngine(indexer)

    response = search_engine.find("")

    assert response["message"] == "Please provide a query to find."
    assert response["results"] == []
def test_search_all_terms_handles_empty_query() -> None:
    indexer = InvertedIndexer()
    search_engine = SearchEngine(indexer)

    assert search_engine.search_all_terms("") == []


def test_calculate_tfidf_score_skips_token_with_zero_document_frequency() -> None:
    indexer = InvertedIndexer()
    indexer.add_document("1", "url1")

    search_engine = SearchEngine(indexer)

    score = search_engine.calculate_tfidf_score("1", ["missing"])

    assert score == 0.0


def test_search_ranked_handles_empty_query() -> None:
    indexer = InvertedIndexer()
    search_engine = SearchEngine(indexer)

    assert search_engine.search_ranked("") == []


def test_contains_exact_phrase_returns_false_when_first_token_missing() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    assert not search_engine.contains_exact_phrase("1", ["missing", "friends"])


def test_contains_exact_phrase_returns_false_when_later_token_missing() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends")

    search_engine = SearchEngine(indexer)

    assert not search_engine.contains_exact_phrase("1", ["good", "missing"])


def test_contains_exact_phrase_returns_false_when_later_token_not_in_document() -> None:
    indexer = InvertedIndexer()
    indexer.index_document("1", "good friends")
    indexer.index_document("2", "missing")

    search_engine = SearchEngine(indexer)

    assert not search_engine.contains_exact_phrase("1", ["good", "missing"])