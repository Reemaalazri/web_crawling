"""
Tests for the indexer module.
"""

from src.indexer import tokenize


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
