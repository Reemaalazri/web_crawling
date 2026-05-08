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

# Used to separate quote text, author names, and tags before tokenisation.
BOUNDARY_TOKEN = "BOUNDARYTOKEN"


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

    # Keep only letters and numbers, then normalise everything to lowercase.
    return re.findall(r"[a-zA-Z0-9]+", text.lower())

class InvertedIndexer:
    """
    Builds an inverted index from crawled pages.

    The index maps each token to the documents where it appears.
    """

    def __init__(self) -> None:
        
        # token -> doc_id -> {"frequency": count, "positions": [word positions]}
        self.index: dict[str, dict[str, dict[str, list[int] | int]]] = {}

        # doc_id -> metadata used when displaying search results.
        self.documents: dict[str, dict[str, str]] = {}
        
        self.document_texts: dict[str,str] = {}


    def add_document(
        self,
        doc_id: str,
        url: str,
        snippet: str = "",
    ) -> None:
        """
        Store document metadata.

        Args:
            doc_id: Unique document identifier.
            url: Original page URL.
            snippet: Short text preview for search results.
        """
        self.documents[doc_id] = {
            "url": url,
            "snippet": snippet,
        }

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
        self.document_texts.setdefault(doc_id, text)
        
        # Store both frequency and positions for each token occurrence.
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
        text = self.extract_text(page.html)

        self.document_texts[doc_id] = text
        
        # Create a short preview without artificial boundary markers.
        snippet = text.replace(BOUNDARY_TOKEN, "").strip()[:250]

        self.add_document(doc_id, page.url, snippet)
        self.index_document(doc_id, text)

    @staticmethod
    def extract_text(html: str) -> str:
        """
        Extract meaningful quote content from HTML.

        Only quote blocks are indexed, avoiding navigation, sidebar,
        footer text, and repeated top-tag content.
        """
        soup = BeautifulSoup(html, "html.parser")
        quote_blocks = soup.select(".quote")

        # Fallback for pages that do not use the expected quote structure.
        if not quote_blocks:
            return soup.get_text(separator=" ", strip=True)

        extracted_parts = []

        for quote in quote_blocks:
            quote_text = quote.select_one(".text")
            author = quote.select_one(".author")
            tags = quote.select(".tag")

            # Add boundary markers so phrase matching does not cross fields.
            if quote_text:
                extracted_parts.append(quote_text.get_text(" ", strip=True))
                extracted_parts.append(BOUNDARY_TOKEN)

            if author:
                extracted_parts.append(author.get_text(" ", strip=True))
                extracted_parts.append(BOUNDARY_TOKEN)

            for tag in tags:
                extracted_parts.append(tag.get_text(" ", strip=True))
                extracted_parts.append(BOUNDARY_TOKEN)

        return " ".join(extracted_parts)

    def save(self, file_path: str | Path) -> None:
        """
        Save the index and document metadata to a JSON file.
        """
        data = {
            "index": self.index,
            "documents": self.documents,
            "document_texts": self.document_texts,
        }

        path = Path(file_path)
        
        # Create the output folder automatically if it does not exist.
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

        # Default to empty dictionaries if the file is missing expected keys.
        self.index = data.get("index", {})
        self.documents = data.get("documents", {})
        self.document_texts = data.get("document_texts", {})

    def get_document_frequency(self, token: str) -> int:
        """
        Get the number of documents containing a token.
        """
        if token not in self.index:
            return 0

        return len(self.index[token])

    def get_total_documents(self) -> int:
        """
        Get the total number of indexed documents.
        """
        return len(self.documents)