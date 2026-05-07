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

