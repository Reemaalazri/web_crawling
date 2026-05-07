"""
Command-line interface for COMP3011 Coursework 2.
"""

from __future__ import annotations

from pathlib import Path

from src.crawler import WebCrawler
from src.indexer import InvertedIndexer, tokenize
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

def print_index_entry(indexer: InvertedIndexer, word: str) -> None:
    """Print the inverted index entry for one cleaned word."""
    tokens = tokenize(word)

    if not tokens:
        print("Please provide a word to print.")
        return

    token = tokens[0]

    if token not in indexer.index:
        print(f"No index entry found for '{token}'.")
        return

    print(f"{token}: {indexer.index[token]}")

def find_query(indexer: InvertedIndexer, query: str) -> None:
    """Find pages matching a query."""
    search_engine = SearchEngine(indexer)
    response = search_engine.find(query)

    print(response["message"])

    if response["results"]:
        for result in response["results"]:
            doc_id = result[0]
            url = indexer.documents.get(doc_id, {}).get("url", "Unknown URL")
            print(f"- {url} | {result}")

    if response["suggestions"]:
        print("Suggestions:", ", ".join(response["suggestions"]))



def run_shell() -> None:
    """Run the interactive command-line shell."""
    indexer = InvertedIndexer()

    print("COMP3011 Search Engine Tool")
    print("Commands: build, load, print <word>, find <query>, exit")

    while True:
        command = input("> ").strip()

        if not command:
            print("Please enter a command.")
            continue

        if command == "exit":
            print("Goodbye.")
            break

        if command == "build":
            indexer = build_index()
            continue

        if command == "load":
            indexer = load_index()
            continue
        
        if command == "print":
            print_index_entry(indexer, "")
            continue

        if command.startswith("print "):
            word = command.removeprefix("print ").strip()
            print_index_entry(indexer, word)
            continue
        
        if command == "find":
            find_query(indexer, "")
            continue

        if command.startswith("find "):
            query = command.removeprefix("find ").strip()
            find_query(indexer, query)
            continue

        print("Unknown command. Use: build, load, print <word>, find <query>, exit")


if __name__ == "__main__":
    run_shell()