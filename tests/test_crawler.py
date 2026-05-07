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

def test_fetch_page_returns_html_content() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    mock_response = Mock()
    mock_response.text = "<html><body>Hello</body></html>"
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.raise_for_status = Mock()

    with patch("src.crawler.requests.get", return_value=mock_response):
        html = crawler.fetch_page("https://quotes.toscrape.com/")

    assert html == "<html><body>Hello</body></html>"


def test_fetch_page_returns_none_for_non_html_content() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    mock_response = Mock()
    mock_response.headers = {"Content-Type": "application/pdf"}
    mock_response.raise_for_status = Mock()

    with patch("src.crawler.requests.get", return_value=mock_response):
        html = crawler.fetch_page("https://quotes.toscrape.com/file.pdf")

    assert html is None


def test_fetch_page_handles_request_exception() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    with patch(
        "src.crawler.requests.get",
        side_effect=requests.RequestException,
    ):
        html = crawler.fetch_page("https://quotes.toscrape.com/")

    assert html is None
