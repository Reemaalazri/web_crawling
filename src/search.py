"""
Search module for COMP3011 Coursework 2.

Provides query processing and ranked retrieval using the
inverted index structure.
"""

from __future__ import annotations

from src.indexer import InvertedIndexer, tokenize
import re
import math
import difflib


class SearchEngine:
    """
    Search engine using an inverted index.

    Supports:
    - single-word lookup
    - all-term matching
    - exact phrase matching
    - TF-IDF ranked retrieval
    - spelling suggestions for missed queries
    """

    def __init__(self, indexer: InvertedIndexer) -> None:
        """Initialise the search engine with an existing inverted index."""
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

        # For single-word search, only the first cleaned token is used.
        token = tokens[0]

        if token not in self.indexer.index:
            return []

        return sorted(self.indexer.index[token].keys())

    def search_all_terms(self, query: str) -> list[str]:
        """
        Retrieve documents that contain all query terms.

        This follows conjunctive query processing, where every returned
        document must contain each token in the query.

        Args:
            query: User query containing one or more terms.

        Returns:
            Sorted list of document IDs containing every query token.
        """
        tokens = tokenize(query)

        if not tokens:
            return []

        posting_sets = []

        # Build one posting set per token, then intersect them.
        for token in tokens:
            if token not in self.indexer.index:
                return []

            posting_sets.append(set(self.indexer.index[token].keys()))

        matching_docs = set.intersection(*posting_sets)

        return sorted(matching_docs)

    def calculate_tfidf_score(self, doc_id: str, tokens: list[str]) -> float:
        """
        Calculate a TF-IDF score for a document and query tokens.

        Args:
            doc_id: Document identifier being scored.
            tokens: Tokenised query terms.

        Returns:
            Numeric TF-IDF score for the document.
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

            # Smoothed IDF avoids division by zero
            # and keeps rare terms valuable.
            inverse_document_frequency = math.log(
                (total_documents + 1) / (document_frequency + 1)
            ) + 1

            score += term_frequency * inverse_document_frequency

        return score

    def search_ranked(self, query: str) -> list[tuple[str, float]]:
        """
        Perform ranked retrieval using TF-IDF scoring.

        Args:
            query: Search query.

        Returns:
            List of (document ID, score) tuples sorted by score.
        """
        tokens = tokenize(query)

        if not tokens:
            return []

        candidate_docs = set()

        # A document is a candidate if it contains at least one query token.
        for token in tokens:
            if token in self.indexer.index:
                candidate_docs.update(self.indexer.index[token].keys())

        scored_results = []

        # Score each candidate document against the full query.
        for doc_id in candidate_docs:
            score = self.calculate_tfidf_score(doc_id, tokens)

            if score > 0:
                scored_results.append((doc_id, score))

        # Highest-scoring pages should appear first.
        scored_results.sort(
            key=lambda result: result[1],
            reverse=True,
        )

        return scored_results

    def contains_exact_phrase(self, doc_id: str, tokens: list[str]) -> bool:
        """
        Check whether a document contains the exact query phrase.

        Example:
            tokens ["good", "friends"] match if "friends" appears
            immediately after "good" in the same document.

        Args:
            doc_id: Document identifier to check.
            tokens: Tokenised phrase query.

        Returns:
            True if the phrase appears in order and consecutively.
        """
        if not tokens:
            return False

        first_token = tokens[0]
        first_posting = self.indexer.index.get(first_token, {}).get(doc_id)

        if first_posting is None:
            return False

        first_positions = first_posting["positions"]

        # Try each occurrence of the first word as a possible phrase start.
        for start_position in first_positions:
            phrase_found = True

            for offset, token in enumerate(tokens[1:], start=1):
                posting = self.indexer.index.get(token, {}).get(doc_id)

                if posting is None:
                    phrase_found = False
                    break

                # The next token must appear exactly
                # one position after the previous.
                if start_position + offset not in posting["positions"]:
                    phrase_found = False
                    break

            if phrase_found:
                return True

        return False

    def search_phrase(self, query: str) -> list[str]:
        """
        Search for documents containing an exact phrase.

        Args:
            query: Phrase query.

        Returns:
            List of matching document IDs.
        """
        tokens = tokenize(query)

        if not tokens:
            return []

        # First reduce the search space to documents containing all terms.
        candidate_docs = self.search_all_terms(query)

        matching_docs = []

        for doc_id in candidate_docs:
            if (
                self.contains_exact_phrase(doc_id, tokens)
                and self.text_contains_exact_phrase(doc_id, tokens)
            ):
                matching_docs.append(doc_id)

        return matching_docs

    def suggest_terms(self, query: str, max_suggestions: int = 3) -> list[str]:
        """
        Suggest similar indexed terms for a misspelled query.

        Args:
            query: User query.
            max_suggestions: Maximum number of suggestions to return.

        Returns:
            A list of suggested terms from the index vocabulary.
        """
        tokens = tokenize(query)

        if not tokens:
            return []

        vocabulary = list(self.indexer.index.keys())
        suggestions: list[str] = []

        for token in tokens:

            # Do not suggest replacements for terms already in the index.
            if token in self.indexer.index:
                continue

            close_matches = difflib.get_close_matches(
                token,
                vocabulary,
                n=max_suggestions,
                cutoff=0.75,
            )

            suggestions.extend(close_matches)

        # Remove duplicates and keep the output deterministic.
        return sorted(set(suggestions))

    def find(self, query: str) -> dict[str, object]:
        """
        Process a full user search query.

        The method first checks for exact phrase matches. If no exact
        phrase is found, it falls back to TF-IDF ranked retrieval.

        Args:
            query: Raw query entered by the user.

        Returns:
            Dictionary containing results, suggestions, and a user message.
        """
        tokens = tokenize(query)

        if not tokens:
            return {
                "results": [],
                "suggestions": [],
                "message": "Please provide a query to find.",

            }

        # Multi-word queries are checked as exact phrases first.
        phrase_results = self.search_phrase(query) if len(tokens) > 1 else []

        if phrase_results:
            return {
                "results":
                    [(doc_id, "exact_phrase") for doc_id in phrase_results],
                "suggestions":
                    [],
                "message":
                    "Exact phrase matches found.",
            }

        # If no phrase match exists, return broader ranked results.
        ranked_results = self.search_ranked(query)

        if ranked_results:
            return {
                "results": ranked_results,
                "suggestions": [],
                "message": "Ranked results found.",
            }

        # If nothing matches, suggest similar words from the index.
        return {
            "results": [],
            "suggestions": self.suggest_terms(query),
            "message": "No results found.",
        }

    def text_contains_exact_phrase(
        self,
        doc_id: str,
        tokens: list[str]
    ) -> bool:
        """
        Check that phrase terms are separated only by spaces in original text.
        """
        text = self.indexer.document_texts.get(doc_id, "")

        if not text:
            return False

        # Do not allow phrase matching across artificial field boundaries.
        text = text.replace("BOUNDARYTOKEN", " BOUNDARYTOKEN ")

        pattern = (
            r"\b"
            + r"\s+".join(re.escape(token) for token in tokens)
            + r"\b"
        )

        return re.search(pattern, text, flags=re.IGNORECASE) is not None
