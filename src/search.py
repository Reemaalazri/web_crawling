"""
Search module for COMP3011 Coursework 2.

Provides query processing and ranked retrieval using the
inverted index structure.
"""

from __future__ import annotations

from src.indexer import InvertedIndexer, tokenize

import math

class SearchEngine:
    """
    Search engine using an inverted index.
    """

    def __init__(self, indexer: InvertedIndexer) -> None:
        self.indexer = indexer

    def search_word(self, query: str) -> list[str]:
        """
        Retrieve documents containing a single word.

        Args:
            query: Search query.

        Returns:
            List of matching document IDs.
        """
        tokens = tokenize(query)

        if not tokens:
            return []

        token = tokens[0]

        if token not in self.indexer.index:
            return []

        return sorted(self.indexer.index[token].keys())

    def search_all_terms(self, query: str) -> list[str]:
        """
        Retrieve documents that contain all query terms.

        This follows conjunctive query processing, where every returned
        document must contain each token in the query.
        """
        tokens = tokenize(query)

        if not tokens:
            return []

        posting_sets = []

        for token in tokens:
            if token not in self.indexer.index:
                return []

            posting_sets.append(set(self.indexer.index[token].keys()))

        matching_docs = set.intersection(*posting_sets)

        return sorted(matching_docs)

    def calculate_tfidf_score(self, doc_id: str, tokens: list[str]) -> float:
        """
        Calculate a TF-IDF score for a document and query tokens.
        """
        total_documents = self.indexer.get_total_documents()

        if total_documents == 0:
            return 0.0

        score = 0.0

        for token in tokens:
            posting = self.indexer.index.get(token, {}).get(doc_id)

            if posting is None:
                continue

            term_frequency = posting["frequency"]
            document_frequency = self.indexer.get_document_frequency(token)

            if document_frequency == 0:
                continue
            
            inverse_document_frequency = math.log(
                (total_documents + 1) / (document_frequency + 1)
            ) + 1

            score += term_frequency * inverse_document_frequency

        return score