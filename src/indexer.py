"""
Indexer module for COMP3011 Coursework 2.

This module converts page text into tokens and later builds an
inverted index containing frequency and positional information.
"""

from __future__ import annotations

import re


def tokenize(text: str) -> list[str]:
    """
    Convert raw text into lowercase alphanumeric tokens.

    Args:
        text: Raw text extracted from a web page.

    Returns:
        A list of cleaned lowercase tokens.
    """
    if not text:
        return []

    return re.findall(r"[a-zA-Z0-9]+", text.lower())

class InvertedIndexer:
    """
    Builds an inverted index from crawled pages.

    The index maps each token to the documents where it appears.
    """

    def __init__(self) -> None:
        self.index: dict[str, dict[str, dict[str, list[int] | int]]] = {}
        self.documents: dict[str, dict[str, str]] = {}

    def add_document(self, doc_id: str, url: str) -> None:
        """
        Store document metadata.

        Args:
            doc_id: Unique document identifier.
            url: Original page URL.
        """
        self.documents[doc_id] = {"url": url}

    def index_document(
        self,
        doc_id: str,
        text: str,
    ) -> None:
        """
        Index all tokens in a document.

        Args:
            doc_id: Unique document identifier.
            text: Raw document text.
        """
        tokens = tokenize(text)

        for token in tokens:
            if token not in self.index:
                self.index[token] = {}

            if doc_id not in self.index[token]:
                self.index[token][doc_id] = {
                    "frequency": 0,
                    "positions": [],
                }

            self.index[token][doc_id]["frequency"] += 1