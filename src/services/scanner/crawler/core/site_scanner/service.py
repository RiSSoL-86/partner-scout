import logging
from typing import TYPE_CHECKING, final, override
from urllib.parse import urljoin, urlparse

import httpx
from crawl4ai import (
    AsyncUrlSeeder,
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    CrawlResult,
    SeedingConfig,
)
from django.conf import settings

from apps.common.services.base import BaseService
from services.scanner.crawler.core.site_scanner.schemas import PageCandidate
from services.scanner.crawler.core.site_scanner.search_rules import (
    mentions_partner_or_director,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


@final
class SiteScannerService(BaseService):
    """Fetch a site without an LLM and keep only keyword-matched pages."""

    def __init__(self, url: str, domain: str) -> None:
        """Prepare the sitemap seeding and fetch config for one site."""
        self.url = url
        self.domain = domain
        self.seeding_config = SeedingConfig(
            source="sitemap",
            max_urls=settings.CRAWLER_MAX_PAGES,  # type: ignore[misc]
            filter_nonsense_urls=True,
        )
        self.fetch_config = CrawlerRunConfig(
            excluded_tags=["script", "style", "nav", "header", "footer"],
            cache_mode=CacheMode.BYPASS,
            page_timeout=settings.CRAWLER_PAGE_TIMEOUT,  # type: ignore[misc]
            stream=True,
        )

    @override
    async def execute(  # type: ignore[override]  # async generator, not a plain coroutine
        self, crawler: AsyncWebCrawler
    ) -> AsyncIterator[PageCandidate]:
        """Fetch each sitemap seed once and yield keyword-matched pages."""
        seed_urls, hidden_urls = await self._seed_urls()
        if not seed_urls:
            logger.info(msg=f"No sitemap URLs for {self.domain}; skipping")
            return

        results = await crawler.arun_many(
            urls=seed_urls, config=self.fetch_config
        )

        fetched = 0
        kept = 0
        async for result in results:
            fetched += 1
            if not result.success:
                continue
            text = self._page_text(result=result)
            if mentions_partner_or_director(text):
                kept += 1
                yield PageCandidate(
                    url=result.url,
                    title=(result.metadata or {}).get("title", ""),
                    text=text,
                    is_hidden=result.url in hidden_urls,
                )
        logger.info(
            msg=(
                f"Keyword gate {self.domain}: {fetched} fetched, "
                f"{kept} kept for LLM"
            )
        )

    async def _seed_urls(self) -> tuple[list[str], set[str]]:
        """Return in-scope URLs to fetch plus the robots-hidden subset."""
        sitemap_urls = await self._sitemap_urls()
        robots_urls = await self._robots_urls()
        sitemap_set = set(sitemap_urls)

        seen: set[str] = set()
        merged: list[str] = []
        for url in (*sitemap_urls, *robots_urls):
            if url not in seen:
                seen.add(url)
                merged.append(url)

        max_pages = settings.CRAWLER_MAX_PAGES  # type: ignore[misc]
        kept = merged[:max_pages]
        hidden = {url for url in kept if url not in sitemap_set}
        logger.info(
            msg=(
                f"Seeded {self.domain}: {len(sitemap_urls)} sitemap, "
                f"{len(robots_urls)} robots-hidden, {len(merged)} merged, "
                f"{len(kept)} kept ({len(hidden)} hidden, limit {max_pages})"
            )
        )
        return kept, hidden

    async def _sitemap_urls(self) -> list[str]:
        """Return every in-scope URL the site advertises in its sitemap."""
        try:
            async with AsyncUrlSeeder() as seeder:
                seeds = await seeder.urls(self.domain, self.seeding_config)
        except Exception:
            logger.exception(msg=f"Sitemap seeding failed for {self.domain}")
            return []
        return [
            seed["url"] for seed in seeds if self._is_in_scope(url=seed["url"])
        ]

    async def _robots_urls(self) -> list[str]:
        """Return in-scope URLs hidden behind robots.txt Disallow rules."""
        robots_url = f"https://{self.domain}/robots.txt"
        timeout = settings.CRAWLER_PAGE_TIMEOUT / 1000  # type: ignore[misc]
        try:
            async with httpx.AsyncClient(
                timeout=timeout, follow_redirects=True
            ) as client:
                response = await client.get(robots_url)
                response.raise_for_status()
        except Exception:
            logger.exception(msg=f"robots.txt fetch failed for {self.domain}")
            return []

        urls: list[str] = []
        applies = False
        for raw_line in response.text.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key == "user-agent":
                applies = value == "*"
            elif key == "disallow" and applies and value:
                if "*" in value or "$" in value:
                    continue
                url = urljoin(f"https://{self.domain}", value)
                if self._is_in_scope(url=url):
                    urls.append(url)
        return urls

    def _is_in_scope(self, url: str) -> bool:
        """Tell whether a URL stays on the company's own domain."""
        netloc = urlparse(url).netloc.removeprefix("www.")
        return netloc == self.domain.removeprefix("www.")

    @staticmethod
    def _page_text(result: CrawlResult) -> str:
        """Return the best available markdown text for a crawl result."""
        markdown = result.markdown
        return (
            getattr(markdown, "fit_markdown", "")
            or getattr(markdown, "raw_markdown", "")
            or str(markdown or "")
        )
