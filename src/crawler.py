"""
Crawler module for COMP3011 Coursework 2.

This module crawls the quotes.toscrape.com website using a BFS-style
frontier queue. It respects the coursework politeness requirement by
waiting between requests and avoids revisiting URLs.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class CrawledPage:
    """Stores the URL and HTML content of one crawled page."""

    url: str
    html: str


class WebCrawler:
    """
    Breadth-first web crawler for a single target website.

    The crawler:
    - keeps a frontier queue of URLs to visit
    - tracks visited URLs to avoid duplicates
    - respects a politeness delay between requests
    - only follows links inside the same domain
    """

    def __init__(
        self,
        start_url: str,
        politeness_delay: float = 6.0,
        timeout: float = 10.0,
        max_pages: int | None = None,
    ) -> None:
        self.start_url = self._normalise_url(start_url)
        self.domain = urlparse(self.start_url).netloc
        self.politeness_delay = politeness_delay
        self.timeout = timeout
        self.max_pages = max_pages

        self.headers = {
            "User-Agent": "COMP3011-WebCrawler/1.0"
        }

    def crawl(self) -> list[CrawledPage]:
        """
        Crawl pages from the start URL using BFS traversal.

        Returns:
            A list of CrawledPage objects containing URLs and HTML.
        """
        frontier: Deque[str] = deque([self.start_url])
        visited: set[str] = set()
        crawled_pages: list[CrawledPage] = []

        while frontier:
            if self.max_pages is not None and len(crawled_pages) >= self.max_pages:
                break

            current_url = frontier.popleft()

            if current_url in visited:
                continue

            visited.add(current_url)

            html = self.fetch_page(current_url)
            if html is None:
                continue

            crawled_pages.append(CrawledPage(url=current_url, html=html))

            for link in self.extract_links(current_url, html):
                if link not in visited and link not in frontier:
                    frontier.append(link)

            if frontier:
                time.sleep(self.politeness_delay)

        return crawled_pages
    
    
    
    def _is_internal_url(self, url: str) -> bool:
        """
        Check whether a URL belongs to the target domain.

        Args:
            url: URL to check.

        Returns:
            True if URL is internal, otherwise False.
        """
        parsed_url = urlparse(url)

        return (
            parsed_url.scheme in {"http", "https"}
            and parsed_url.netloc == self.domain
        )

    @staticmethod
    def _normalise_url(url: str) -> str:
        """
        Normalise URLs to reduce duplicate crawling.

        Removes fragments and trailing slashes, except for root URLs.
        """
        parsed = urlparse(url)
        cleaned = parsed._replace(fragment="")
        normalised = cleaned.geturl()

        if normalised.endswith("/") and parsed.path != "/":
            normalised = normalised.rstrip("/")

        return normalised