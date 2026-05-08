"""
Command-line interface for COMP3011 Coursework 2.
"""

from __future__ import annotations

from pathlib import Path

from src.crawler import WebCrawler
from src.indexer import InvertedIndexer, tokenize
from src.search import SearchEngine


# Website used for crawling and indexing.
START_URL = "https://quotes.toscrape.com/"

# Location where the generated index is stored.
INDEX_FILE = Path("data/index.json")


def build_index() -> InvertedIndexer:
    """
    Crawl the website, build the index, and save it.

    Returns:
        Fully populated InvertedIndexer instance.
    """
    crawler = WebCrawler(START_URL)
    pages = crawler.crawl()

    indexer = InvertedIndexer()

    # Assign sequential document IDs while indexing each crawled page.
    for doc_number, page in enumerate(pages, start=1):
        indexer.index_page(str(doc_number), page)

    indexer.save(INDEX_FILE)

    print(f"Built index for {len(pages)} pages.")
    print(f"Saved index to {INDEX_FILE}")

    return indexer


def load_index() -> InvertedIndexer:
    """
    Load the saved index from disk.

    Returns:
        Loaded InvertedIndexer instance.
    """
    indexer = InvertedIndexer()

    # Prevent loading from a missing index file.
    if not INDEX_FILE.exists():
        print("No saved index found. Run 'build' first.")
        return indexer

    indexer.load(INDEX_FILE)
    print(f"Loaded index from {INDEX_FILE}")

    return indexer

def print_index_entry(indexer: InvertedIndexer, word: str) -> None:
    """
    Print the inverted index entry for one cleaned word.

    Args:
        indexer: Loaded inverted index.
        word: Word entered by the user.
    """
    tokens = tokenize(word)

    if not tokens:
        print("Please provide a word to print.")
        return

    # Use the first cleaned token after normalisation.
    token = tokens[0]

    if token not in indexer.index:
        print(f"No index entry found for '{token}'.")
        return

    print(f"{token}: {indexer.index[token]}")

def find_query(indexer: InvertedIndexer, query: str) -> None:
    """
    Find pages matching a query and display ranked results.

    Args:
        indexer: Loaded inverted index.
        query: User search query.
    """
    search_engine = SearchEngine(indexer)
    response = search_engine.find(query)

    print(response["message"])

    # Display matching pages and associated ranking information.
    if response["results"]:
        for result in response["results"]:
            doc_id = result[0]
            value = result[1]

            document = indexer.documents.get(doc_id, {})
            url = document.get("url", "Unknown URL")
            snippet = document.get("snippet", "")

            print(f"- {url}")

            # Ranked results use floating-point TF-IDF scores.
            if isinstance(value, float):
                print(f"  Score: {value:.2f}")
            else:
                print(f"  Match: {value}")

            if snippet:
                print(f"  Snippet: {snippet}")

    # Show spelling suggestions if no results were found.
    if response["suggestions"]:
        print("Suggestions:", ", ".join(response["suggestions"]))

def run_shell() -> None:
    """
    Run the interactive command-line shell.

    Supports:
    - build
    - load
    - print <word>
    - find <query>
    - exit
    """
    indexer = InvertedIndexer()

    print("COMP3011 Search Engine Tool")
    print("Commands: build, load, print <word>, find <query>, exit")

    while True:
        command = input("> ").strip()

        # Reject empty commands early.
        if not command:
            print("Please enter a command.")
            continue

        if command == "exit":
            print("Goodbye.")
            break

        # Build and save a new index from the website.
        if command == "build":
            indexer = build_index()
            continue

        # Load an existing saved index.
        if command == "load":
            indexer = load_index()
            continue

        # Handle missing arguments for print command.
        if command == "print":
            print_index_entry(indexer, "")
            continue

        if command.startswith("print "):
            word = command.removeprefix("print ").strip()
            print_index_entry(indexer, word)
            continue
        
        # Handle missing arguments for find command.
        if command == "find":
            find_query(indexer, "")
            continue

        if command.startswith("find "):
            query = command.removeprefix("find ").strip()
            find_query(indexer, query)
            continue

        print("Unknown command. Use: build, load, print <word>, find <query>, exit")


# Start the interactive shell only when the file is run directly.
if __name__ == "__main__":
    run_shell()