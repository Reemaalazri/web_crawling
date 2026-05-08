# COMP3011 Coursework 2 — Web Crawler and Search Engine
## Overview

This project implements a small-scale web crawler and search engine in Python.
The system crawls pages from the Quotes to Scrape website, extracts meaningful textual content, builds a positional inverted index, and supports ranked information retrieval using TF-IDF scoring.

### The implementation demonstrates:

- Breadth-First Search (BFS) web crawling
- URL normalisation and filtering
- Positional inverted indexing
- Exact phrase matching
- Conjunctive multi-word queries
- TF-IDF ranked retrieval
- Query suggestions for misspellings
- Automated testing with pytest
- Mocked network testing
- Benchmarking and coverage analysis

## Features
### Web Crawling
The crawler:
- Uses BFS traversal
- Restricts crawling depth
- Avoids revisiting URLs
- Respects politeness delays
- Handles request failures safely
- Filters invalid and external links
- Extracts only meaningful quote content

### Inverted Index
The index stores:
- Document IDs
- Term frequencies
- Positional information
- Document metadata
- Search snippets

Example structure:

```json
{
  "love": {
    "1": {
      "frequency": 3,
      "positions": [4, 18, 25]
    }
  }
}
```

## Search Engine Functionality
### Single-word Search
Example:

```
find love
```

Returns documents containing the word.

### Multi-word Conjunctive Search
Example:

```
find love life
```

Returns documents containing all query terms.

### Exact Phrase Matching
The engine supports positional phrase search.

Example:

```
find good friends
```

This only matches documents where:

```
good friends
```

appear adjacently and in order.


### Ranked Retrieval
If no exact phrase match exists, the engine falls back to TF-IDF ranking.

Example:

```
find love opposite
```

Documents are ranked by relevance score.

The engine also generates contextual snippets centred around matching query terms.

### Query Suggestions
Misspelled terms are handled using approximate matching.

Example:
```
find frind
```

Suggested correction:

```
friends
```

## Project Structure
```bash
web_crawling/
│
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
│
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_search.py
│   ├── test_main.py
│   └── test_benchmark.py
│
├── benchmarks/
│   └── benchmark_search.py
│
├── data/
│   └── index.json
│
├── requirements.txt
├── pytest.ini
└── README.md
```

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd web_crawling
```

### Create Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the System
### Build the Index

```bash
python -m src.main
```

Then enter:

```bash
build
```

This crawls the website and creates the positional inverted index.

### Load Existing Index
```bash
load
```

Loads the saved JSON index from disk.

## Search Commands
### Find Documents

```bash
find love
find good friends
find love opposite
```

### Print Index Entry
```bash
print love
```

Displays posting list information including frequencies and positions.

### Exit program
```bash
exit
```

## Error Handling
The system safely handles:
- Empty queries
- Unknown commands
- Missing terms
- Invalid URLs
- Network failures
- Duplicate URLs
- Non-HTML content

Example:
```bash 
find
```

Output:
```bash 
Please provide a query to find.
```

## Automated Testing
The project uses pytest for automated testing.

Tests include:
- Crawling behaviour
- URL filtering
- Tokenisation
- Positional indexing
- Exact phrase matching
- Ranked retrieval
- Approximate query suggestions for misspelled terms
- Defensive edge cases
- Benchmark execution

## Running Tests
### Run All Tests
```bash
python -m pytest
```

### Run Coverage Report
```bash
python -m pytest --cov=src --cov-report=term-missing
```

Example result:

```bash
83 passed
96% total coverage
```

The final implementation includes 83 automated tests covering crawling, indexing, retrieval, CLI handling, benchmarking and edge-case behaviour.

## Mocking Strategy
Crawler network requests are mocked using:

```bash
from unittest.mock import Mock, patch
```

This allows tests to run without real network access and ensures deterministic behaviour.

Example:

```bash
with patch.object(crawler.session, "get", return_value=mock_response):
```

## Benchmarking
Benchmarking measures:
- Query execution time
- Vocabulary size
- Index size
- Retrieval performance

Run benchmark:

```bash 
python -m benchmarks.benchmark_search
```

Example output:

```bash
Documents: 171
Vocabulary size: 4227
Average query time: 0.001459s
```

## Technologies Used
- Python 3.12
- requests
- BeautifulSoup4
- pytest
- pytest-cov
- difflib
- JSON

## Architecture and Search Engine Design Rationale
The system follows a modular search engine architecture consisting of three main stages:
1. Crawling
2. Indexing
3. Retrieval

The crawler is responsible for discovering and downloading web pages using Breadth-First Search (BFS) traversal. BFS was selected because it prioritises shallow pages first and avoids rapidly traversing deeply nested links. URL filtering and duplicate detection are used to reduce redundant crawling and improve efficiency.

The indexing stage builds a positional inverted index. Inverted indexes are widely used in modern search engines because they provide efficient term-based retrieval while significantly reducing lookup complexity compared to sequential document scanning. Positional information is additionally stored to support exact phrase matching and adjacency checking.

For retrieval, the system combines conjunctive query processing with TF-IDF ranked retrieval. Conjunctive processing ensures that all query terms must appear within a result document, while TF-IDF ranking improves relevance by weighting rare and informative terms more heavily than common words.

The implementation also includes approximate term suggestion using edit-distance similarity through Python’s difflib library. This improves usability by handling misspelled queries gracefully.

Several defensive programming practices were incorporated throughout the implementation, including:

- request exception handling
- non-HTML content filtering
- duplicate URL prevention
- empty query handling
- invalid command validation

The project design prioritised modularity, readability, and testability. Crawling, indexing, and retrieval logic are separated into independent modules, enabling isolated testing and easier future extension.

## Design Decisions
### Why BFS Crawling?
BFS ensures shallow pages are crawled first and avoids deep traversal early.

### Why Positional Indexing?
Positional indexes enable:
- Exact phrase matching
- Adjacency checking
- Multi-word positional queries

### Why TF-IDF?
TF-IDF improves ranking quality by:
- Increasing importance of rare terms
- Reducing influence of common terms
- Producing more relevant retrieval results

### Limitations
Current limitations include:
- Small crawl scope
- No stemming or lemmatisation
- No PageRank scoring
- Snippets are simple text truncations
- In-memory indexing only

### Future Improvements
Possible future extensions:
- BM25 ranking
- Persistent database storage
- Parallel crawling
- Snippet highlighting
- Web interface
- Advanced query parsing
- Stop-word filtering
- Stemming and lemmatisation
- PageRank-based scoring
- Distributed indexing
- Query expansion
- Semantic retrieval using embeddings

## Author
Reema Alazri

University of Leeds

COMP3011 Coursework 2