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

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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
        max_depth: int = 5,
    ) -> None:
        self.start_url = self._normalise_url(start_url)
        self.domain = urlparse(self.start_url).netloc
        self.politeness_delay = politeness_delay
        self.timeout = timeout
        self.max_pages = max_pages
        self.max_depth = max_depth

        self.blocked_path_keywords = {
            "trap",
            "logout",
            "login",
            "signin",
            "signup",
            "register",
            "followme",
        }
        self.headers = {
            "User-Agent": "COMP3011-WebCrawler/1.0"
        }

        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def crawl(self) -> list[CrawledPage]:
        """
        Crawl pages from the start URL using BFS traversal.

        Returns:
            A list of CrawledPage objects containing URLs and HTML.
        """
        frontier: Deque[tuple[str, int]] = deque([(self.start_url, 0)])
        queued: set[str] = {self.start_url}
        visited: set[str] = set()
        crawled_pages: list[CrawledPage] = []

        while frontier:
            if self.max_pages is not None and len(crawled_pages) >= self.max_pages:
                break

            current_url, depth = frontier.popleft()
            queued.discard(current_url)

            if current_url in visited:
                continue

            if depth > self.max_depth:
                continue

            visited.add(current_url)

            html = self.fetch_page(current_url)
            if html is None:
                continue

            crawled_pages.append(CrawledPage(url=current_url, html=html))

            for link in self.extract_links(current_url, html):
                if (
                    link not in visited
                    and link not in queued
                    and self._is_safe_to_crawl(link)
                ):
                    frontier.append((link, depth + 1))
                    queued.add(link)

            if frontier:
                time.sleep(self.politeness_delay)

        return crawled_pages

    def fetch_page(self, url: str) -> str | None:
        """
        Download a single web page.

        Args:
            url: Page URL to fetch.

        Returns:
            HTML text if successful, otherwise None.
        """
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None

            return response.text

        except requests.RequestException as error:
            print(f"[Crawler warning] Could not fetch {url}: {error}")
            return None

    def extract_links(self, base_url: str, html: str) -> list[str]:
        """
        Extract valid internal links from a page.

        Args:
            base_url: URL of the page being parsed.
            html: HTML content of the page.

        Returns:
            A sorted list of normalised internal URLs.
        """
        soup = BeautifulSoup(html, "html.parser")
        links: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            absolute_url = urljoin(base_url, anchor["href"])
            normalised_url = self._normalise_url(absolute_url)

            if self._is_internal_url(normalised_url):
                links.add(normalised_url)

        return sorted(links)

    def _is_safe_to_crawl(self, url: str) -> bool:
        """
        Check whether a URL should be crawled.

        This prevents the crawler from following login/logout pages,
        obvious trap paths, and infinite generated URL chains.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        if any(keyword in path for keyword in self.blocked_path_keywords):
            return False

        return self._is_internal_url(url)
    
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
        
        # Canonicalise first paginated tag pages because
        # /tag/name and /tag/name/page/1 contain duplicate content.
        if "/tag/" in normalised and normalised.endswith("/page/1"):
            normalised = normalised.removesuffix("/page/1")

        return normalised
