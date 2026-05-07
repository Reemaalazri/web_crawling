"""
Tests for the crawler module.
"""

from src.crawler import WebCrawler


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

def test_is_internal_url_accepts_same_domain() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    assert crawler._is_internal_url("https://quotes.toscrape.com/page/1")


def test_is_internal_url_rejects_external_domain() -> None:
    crawler = WebCrawler("https://quotes.toscrape.com/", politeness_delay=0)

    assert not crawler._is_internal_url("https://example.com/page/1")