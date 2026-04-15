"""Sitemap-based website crawler."""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import requests

LOGGER = logging.getLogger(__name__)


class SitemapCrawler:
    """Fetch URLs from sitemap.xml and download page HTML."""

    def __init__(self, base_url: str, user_agent: str, timeout: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def discover_urls(self) -> list[str]:
        """Resolve URLs from a sitemap or sitemap index."""

        sitemap_url = urljoin(f"{self._base_url}/", "sitemap.xml")
        response = self._session.get(sitemap_url, timeout=self._timeout)
        response.raise_for_status()

        root = ElementTree.fromstring(response.text)
        namespace = self._extract_namespace(root.tag)
        discovered = self._parse_sitemap(root, namespace)
        unique_urls = sorted(set(discovered))
        LOGGER.info("Discovered %s sitemap URLs", len(unique_urls))
        return unique_urls

    def fetch_page(self, url: str) -> str:
        """Download raw HTML for a page."""

        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.text

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
            response = self._session.get(sitemap_url, timeout=self._timeout)
            response.raise_for_status()
            nested_root = ElementTree.fromstring(response.text)
            nested_urls.extend(
                self._parse_sitemap(nested_root, self._extract_namespace(nested_root.tag))
            )
        return nested_urls

    @staticmethod
    def _extract_namespace(tag: str) -> str:
        if tag.startswith("{"):
            return tag.split("}")[0] + "}"
        return ""
