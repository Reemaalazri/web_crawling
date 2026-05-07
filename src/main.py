"""
Command-line interface for COMP3011 Coursework 2.
"""

from __future__ import annotations

from pathlib import Path

from src.crawler import WebCrawler
from src.indexer import InvertedIndexer
from src.search import SearchEngine


START_URL = "https://quotes.toscrape.com/"
INDEX_FILE = Path("data/index.json")


def build_index() -> InvertedIndexer:
    """Crawl the website, build the index, and save it."""
    crawler = WebCrawler(START_URL)
    pages = crawler.crawl()

    indexer = InvertedIndexer()

    for doc_number, page in enumerate(pages, start=1):
        indexer.index_page(str(doc_number), page)

    indexer.save(INDEX_FILE)

    print(f"Built index for {len(pages)} pages.")
    print(f"Saved index to {INDEX_FILE}")

    return indexer


def load_index() -> InvertedIndexer:
    """Load the saved index from disk."""
    indexer = InvertedIndexer()

    if not INDEX_FILE.exists():
        print("No saved index found. Run 'build' first.")
        return indexer

    indexer.load(INDEX_FILE)
    print(f"Loaded index from {INDEX_FILE}")

    return indexer