import logging
from typing import final, override
from urllib.parse import urljoin

import httpx
from crawl4ai import AsyncUrlSeeder, SeedingConfig
from django.conf import settings

from apps.common.services.base import BaseService
from services.scanner.crawler.url_collector.utils import (
    is_in_scope,
)

logger = logging.getLogger(__name__)


@final
class UrlCollectorService(BaseService):
    """Merge sitemap and robots-hidden URLs into one capped fetch list."""

    def __init__(self, domain: str) -> None:
        """Wire the sitemap and robots seeders for one site."""
        self.domain = domain
        self.sitemap_seeder = SitemapSeederService(domain=domain)
        self.robots_seeder = RobotsSeederService(domain=domain)

    @override
    async def execute(self) -> tuple[list[str], set[str]]:
        """Return in-scope URLs to fetch plus the robots-hidden subset."""
        sitemap_urls = await self.sitemap_seeder.execute()
        robots_urls = await self.robots_seeder.execute()

        seen: set[str] = set()
        fetch_urls: list[str] = []
        for url in (*sitemap_urls, *robots_urls):
            if url not in seen:
                seen.add(url)
                fetch_urls.append(url)

        max_pages = settings.CRAWLER_MAX_PAGES  # type: ignore[misc]
        fetch_urls = fetch_urls[:max_pages]
        sitemap_set = set(sitemap_urls)
        hidden_urls = {url for url in fetch_urls if url not in sitemap_set}
        logger.info(
            msg=(
                f"Seeded {self.domain}: {len(sitemap_urls)} sitemap, "
                f"{len(robots_urls)} robots-hidden, "
                f"{len(fetch_urls)} to fetch "
                f"({len(hidden_urls)} hidden, limit {max_pages})"
            )
        )
        return fetch_urls, hidden_urls


@final
class SitemapSeederService(BaseService):
    """Collect every in-scope URL a site advertises in its sitemap."""

    def __init__(self, domain: str) -> None:
        """Prepare the sitemap seeding config for one site."""
        self.domain = domain
        self.seeding_config = SeedingConfig(
            source="sitemap",
            max_urls=settings.CRAWLER_MAX_PAGES,  # type: ignore[misc]
            filter_nonsense_urls=True,
        )

    @override
    async def execute(self) -> list[str]:
        """Return every in-scope URL the site advertises in its sitemap."""
        try:
            async with AsyncUrlSeeder() as seeder:
                seeds = await seeder.urls(self.domain, self.seeding_config)
        except Exception:
            logger.exception(msg=f"Sitemap seeding failed for {self.domain}")
            return []
        return [
            seed["url"]
            for seed in seeds
            if is_in_scope(url=seed["url"], domain=self.domain)
        ]


@final
class RobotsSeederService(BaseService):
    """Collect in-scope URLs hidden behind robots.txt Disallow rules."""

    def __init__(self, domain: str) -> None:
        """Store the domain whose robots.txt should be inspected."""
        self.domain = domain

    @override
    async def execute(self) -> list[str]:
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
                if is_in_scope(url=url, domain=self.domain):
                    urls.append(url)
        return urls
