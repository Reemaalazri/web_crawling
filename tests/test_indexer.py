"""
Tests for the indexer module.
"""

from src.indexer import tokenize
from src.indexer import InvertedIndexer

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