"""
Simple benchmark script for the search engine.

Measures index size, vocabulary size, and average query time.
"""

from __future__ import annotations

import time
from pathlib import Path

from src.indexer import InvertedIndexer
from src.search import SearchEngine


INDEX_FILE = Path("data/index.json")


def main() -> None:
    """Run simple search benchmarks."""
    indexer = InvertedIndexer()
    indexer.load(INDEX_FILE)

    search_engine = SearchEngine(indexer)

    queries = [
        "love",
        "life",
        "good friends",
        "opposite of love",
        "indifference",
        "frind",
    ]

    print("Benchmark results")
    print("-----------------")
    print(f"Documents: {indexer.get_total_documents()}")
    print(f"Vocabulary size: {len(indexer.index)}")
    print(f"Index file size: {INDEX_FILE.stat().st_size / 1024:.2f} KB")

    total_time = 0.0

    for query in queries:
        start = time.perf_counter()
        result = search_engine.find(query)
        end = time.perf_counter()

        elapsed = end - start
        total_time += elapsed

        print(
            f"Query: {query!r} | "
            f"Time: {elapsed:.6f}s | "
            f"Results: {len(result['results'])}"
        )

    average_time = total_time / len(queries)
    print(f"Average query time: {average_time:.6f}s")


if __name__ == "__main__":
    main()