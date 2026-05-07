"""
Search module for COMP3011 Coursework 2.

Provides query processing and ranked retrieval using the
inverted index structure.
"""

from __future__ import annotations

from src.indexer import InvertedIndexer, tokenize


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