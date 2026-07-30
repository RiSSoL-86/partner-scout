import asyncio
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, final
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig
from django.conf import settings

from services.scanner.crawler.core.llm_extractor.service import (
    LlmExtractorService,
)
from services.scanner.crawler.core.site_scanner.service import (
    SiteScannerService,
)

if TYPE_CHECKING:
    from services.scanner.crawler.core.llm_extractor.schemas import (
        CrawledPage,
    )
    from services.scanner.crawler.core.site_scanner.schemas import (
        PageCandidate,
    )

logger = logging.getLogger(__name__)


@final
class CrawlEngine:
    """Scan a company site: cheap keyword pass first, LLM pass on the rest."""

    def __init__(self, url: str, company_name: str = "") -> None:
        """Wire the site scanner and the LLM extractor for one company."""
        self.domain = urlparse(url).netloc
        self.browser_config = BrowserConfig(
            headless=settings.CRAWLER_HEADLESS,  # type: ignore[misc]
            extra_args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        self.site_scanner_service = SiteScannerService(
            url=url, domain=self.domain
        )
        self.llm_extractor_service = LlmExtractorService(
            company_name=company_name, website=url
        )

    async def crawl(self) -> AsyncIterator[CrawledPage]:
        """Pipe keyword-matched pages straight into the LLM as they arrive."""
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                async for page in self._pipeline(crawler=crawler):
                    yield page
        finally:
            self.llm_extractor_service.log_usage(domain=self.domain)

    async def _pipeline(
        self, crawler: AsyncWebCrawler
    ) -> AsyncIterator[CrawledPage]:
        """Walk the sitemap once, yielding pages as the LLM clears them."""
        semaphore = asyncio.Semaphore(value=settings.CRAWLER_CONCURRENCY)  # type: ignore[misc]
        queue: asyncio.Queue[CrawledPage | None] = asyncio.Queue()

        async def gate(candidate: PageCandidate) -> None:
            async with semaphore:
                page = await self.llm_extractor_service.execute(
                    candidate=candidate
                )
            if page is not None:
                await queue.put(page)

        async def walk() -> None:
            tasks: list[asyncio.Task[None]] = []
            candidates = self.site_scanner_service.execute(crawler=crawler)
            try:
                async for candidate in candidates:
                    tasks.append(
                        asyncio.create_task(gate(candidate=candidate))
                    )
                if tasks:
                    await asyncio.gather(*tasks)
            finally:
                await queue.put(None)  # sentinel: crawl + LLM both done

        walker = asyncio.create_task(walk())
        while (page := await queue.get()) is not None:
            yield page
        await walker
