"""
Tests for the crawler module.
"""

from src.crawler import WebCrawler
from unittest.mock import Mock, patch

import requests

# -------------------------
# URL normalisation tests
# -------------------------

def test_normalise_url_removes_fragment() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    result = crawler._normalise_url(
        "https://quotes.toscrape.com/page/1/#comments"
    )

    assert result == "https://quotes.toscrape.com/page/1"


def test_normalise_url_removes_trailing_slash_except_root() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    page_url = crawler._normalise_url("https://quotes.toscrape.com/page/1/")
    root_url = crawler._normalise_url("https://quotes.toscrape.com/")

    assert page_url == "https://quotes.toscrape.com/page/1"
    assert root_url == "https://quotes.toscrape.com/"

# -------------------------
# Internal URL validation tests
# -------------------------

def test_is_internal_url_accepts_same_domain() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    assert crawler._is_internal_url("https://quotes.toscrape.com/page/1")

# -------------------------
# Link extraction tests
# -------------------------

def test_is_internal_url_rejects_external_domain() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    assert not crawler._is_internal_url("https://example.com/page/1")

# -------------------------
# Crawler safety tests
# -------------------------

def test_is_safe_to_crawl_rejects_trap_links() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    assert not crawler._is_safe_to_crawl(
        "https://quotes.toscrape.com/trap_unwanted_robots"
    )


def test_is_safe_to_crawl_rejects_login_links() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    assert not crawler._is_safe_to_crawl(
        "https://quotes.toscrape.com/login"
    )

def test_extract_links_returns_only_internal_links() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    html = """
    <html>
        <body>
            <a href="/page/2/">Next</a>
            <a href="https://quotes.toscrape.com/tag/life/">Life</a>
            <a href="https://example.com/">External</a>
        </body>
    </html>
    """

    links = crawler.extract_links(
        "https://quotes.toscrape.com/",
        html,
    )

    assert "https://quotes.toscrape.com/page/2" in links
    assert "https://quotes.toscrape.com/tag/life" in links
    assert "https://example.com" not in links

# -------------------------
# Page fetching tests
# -------------------------

# Successful HTML download
def test_fetch_page_returns_html_content() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    mock_response = Mock()
    mock_response.text = "<html><body>Hello</body></html>"
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.raise_for_status = Mock()

    with patch("src.crawler.requests.get", return_value=mock_response):
        html = crawler.fetch_page("https://quotes.toscrape.com/")

    assert html == "<html><body>Hello</body></html>"


# Crawler ignores PDFs/non-HTML files
def test_fetch_page_returns_none_for_non_html_content() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    mock_response = Mock()
    mock_response.headers = {"Content-Type": "application/pdf"}
    mock_response.raise_for_status = Mock()

    with patch("src.crawler.requests.get", return_value=mock_response):
        html = crawler.fetch_page("https://quotes.toscrape.com/file.pdf")

    assert html is None

# Crawler safely handles timeouts/network failures
def test_fetch_page_handles_request_exception() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    with patch(
        "src.crawler.requests.get",
        side_effect=requests.RequestException,
    ):
        html = crawler.fetch_page("https://quotes.toscrape.com/")

    assert html is None

# -------------------------
# BFS crawl behaviour tests
# -------------------------

def test_crawl_respects_max_pages() -> None:
    crawler = WebCrawler(
        "https://quotes.toscrape.com/",
        politeness_delay=0,
        max_pages=2,
    )

    fake_html = """
    <html>
        <body>
            <a href="/page/2/">Page 2</a>
            <a href="/page/3/">Page 3</a>
        </body>
    </html>
    """

    with patch.object(crawler, "fetch_page", return_value=fake_html):
        pages = crawler.crawl()

    assert len(pages) == 2

# Optimisation check
def test_crawl_avoids_duplicate_urls() -> None:
    crawler = WebCrawler(
        "https://quotes.toscrape.com/",
        politeness_delay=0,
        max_pages=10,
    )

    home_html = """
    <html>
        <body>
            <a href="/page/2/">Page 2</a>
            <a href="/page/2/#comments">Duplicate Page 2</a>
        </body>
    </html>
    """

    page_two_html = "<html><body>No more links</body></html>"

    def fake_fetch(url: str) -> str:
        if url == "https://quotes.toscrape.com/":
            return home_html
        return page_two_html

    with patch.object(crawler, "fetch_page", side_effect=fake_fetch):
        pages = crawler.crawl()

    crawled_urls = [page.url for page in pages]

    assert crawled_urls.count("https://quotes.toscrape.com/page/2") == 1