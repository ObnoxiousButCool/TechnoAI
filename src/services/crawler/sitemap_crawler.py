"""Sitemap-based website crawler."""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import requests

LOGGER = logging.getLogger(__name__)


class SitemapCrawler:
    """Fetch URLs from sitemap.xml and download page HTML."""

    def __init__(
        self,
        base_url: str,
        user_agent: str,
        timeout: int,
        manual_urls: str = "",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._manual_urls = manual_urls
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def discover_urls(self) -> list[str]:
        """Resolve URLs from a sitemap or sitemap index."""

        sitemap_urls = self._discover_sitemap_urls()
        if sitemap_urls:
            LOGGER.info(
                "URL discovery mode: sitemap; discovered %s URLs",
                len(sitemap_urls),
            )
            return sitemap_urls

        manual_urls = self._discover_manual_urls()
        if manual_urls:
            LOGGER.info(
                "URL discovery mode: manual_fallback; discovered %s URLs",
                len(manual_urls),
            )
            return manual_urls

        raise ValueError(
            "No valid sitemap URLs found and WEBSITE_URLS is not configured."
        )

    def fetch_page(self, url: str) -> str:
        """Download raw HTML for a page."""

        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.text

    def _discover_sitemap_urls(self) -> list[str]:
        sitemap_url = urljoin(f"{self._base_url}/", "sitemap.xml")
        try:
            response = self._session.get(sitemap_url, timeout=self._timeout)
            response.raise_for_status()
            root = ElementTree.fromstring(response.text)
        except (ElementTree.ParseError, requests.RequestException) as exc:
            LOGGER.warning("Sitemap URL discovery failed: %s", exc)
            return []

        namespace = self._extract_namespace(root.tag)
        discovered = self._parse_sitemap(root, namespace)
        return self._deduplicate_urls(discovered)

    def _discover_manual_urls(self) -> list[str]:
        if not self._manual_urls.strip():
            return []

        urls = []
        for raw_url in self._manual_urls.split(","):
            url = raw_url.strip()
            if not url:
                continue

            urls.append(self._to_absolute_url(url))

        return self._deduplicate_urls(urls)

    def _parse_sitemap(self, root: ElementTree.Element, namespace: str) -> list[str]:
        url_tag = f".//{namespace}url/{namespace}loc"
        sitemap_tag = f".//{namespace}sitemap/{namespace}loc"

        urls = [node.text.strip() for node in root.findall(url_tag) if node.text]
        nested_sitemaps = [
            node.text.strip()
            for node in root.findall(sitemap_tag)
            if node.text
        ]

        if urls:
            domain = urlparse(self._base_url).netloc
            return [url for url in urls if urlparse(url).netloc == domain]

        nested_urls: list[str] = []
        for sitemap_url in nested_sitemaps:
            try:
                response = self._session.get(sitemap_url, timeout=self._timeout)
                response.raise_for_status()
                nested_root = ElementTree.fromstring(response.text)
            except (ElementTree.ParseError, requests.RequestException) as exc:
                LOGGER.warning("Nested sitemap URL discovery failed: %s", exc)
                continue

            nested_namespace = self._extract_namespace(nested_root.tag)
            nested_urls.extend(
                self._parse_sitemap(nested_root, nested_namespace)
            )
        return nested_urls

    def _to_absolute_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return url

        return urljoin(f"{self._base_url}/", url)

    @staticmethod
    def _deduplicate_urls(urls: list[str]) -> list[str]:
        return sorted(set(urls))

    @staticmethod
    def _extract_namespace(tag: str) -> str:
        if tag.startswith("{"):
            return tag.split("}")[0] + "}"
        return ""
