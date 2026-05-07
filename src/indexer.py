"""
Indexer module for COMP3011 Coursework 2.

This module converts page text into tokens and later builds an
inverted index containing frequency and positional information.
"""

from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup
from src.crawler import CrawledPage

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

        for position, token in enumerate(tokens):
            if token not in self.index:
                self.index[token] = {}

            if doc_id not in self.index[token]:
                self.index[token][doc_id] = {
                    "frequency": 0,
                    "positions": [],
                }

            self.index[token][doc_id]["frequency"] += 1
            self.index[token][doc_id]["positions"].append(position)

    def index_page(
        self,
        doc_id: str,
        page: CrawledPage,
    ) -> None:
        """
        Index a crawled web page.

        Args:
            doc_id: Unique document identifier.
            page: CrawledPage object containing URL and HTML.
        """
        self.add_document(doc_id, page.url)

        text = self.extract_text(page.html)

        self.index_document(doc_id, text)

    @staticmethod
    def extract_text(html: str) -> str:
        """
        Extract visible text from HTML.

        Args:
            html: Raw HTML content.

        Returns:
            Extracted plain text.
        """

        soup = BeautifulSoup(html, "html.parser")

        return soup.get_text(separator=" ", strip=True)

    def save(self, file_path: str | Path) -> None:
        """
        Save the index and document metadata to a JSON file.
        """
        data = {
            "index": self.index,
            "documents": self.documents,
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load(self, file_path: str | Path) -> None:
        """
        Load the index and document metadata from a JSON file.
        """
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.index = data.get("index", {})
        self.documents = data.get("documents", {})