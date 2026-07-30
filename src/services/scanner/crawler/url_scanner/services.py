import logging
from typing import TYPE_CHECKING, final, override

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, CrawlResult
from django.conf import settings

from apps.common.services.base import BaseService
from services.scanner.crawler.url_scanner.schemas import (
    PageCandidate,
)
from services.scanner.crawler.url_scanner.search_rules import (
    mentions_partner_or_director,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable

logger = logging.getLogger(__name__)


@final
class UrlScannerService(BaseService):
    """Fetch given URLs without an LLM and keep only keyword-matched pages."""

    def __init__(
        self,
        domain: str,
        on_page_scanned: Callable[[], Awaitable[object]] | None = None,
    ) -> None:
        """Prepare the fetch config for one site's already-collected URLs."""
        self.domain = domain
        self.on_page_scanned = on_page_scanned
        self.fetch_config = CrawlerRunConfig(
            excluded_tags=["script", "style", "nav", "header", "footer"],
            cache_mode=CacheMode.BYPASS,
            page_timeout=settings.CRAWLER_PAGE_TIMEOUT,  # type: ignore[misc]
            stream=True,
        )

    @override
    async def execute(  # type: ignore[override]  # async generator, not a plain coroutine
        self,
        crawler: AsyncWebCrawler,
        fetch_urls: list[str],
        hidden_urls: set[str],
    ) -> AsyncIterator[PageCandidate]:
        """Fetch each given URL once and yield keyword-matched pages."""
        if not fetch_urls:
            logger.info(msg=f"No URLs for {self.domain}; skipping")
            return

        results = await crawler.arun_many(
            urls=fetch_urls, config=self.fetch_config
        )

        fetched = 0
        kept_for_llm = 0
        async for result in results:
            fetched += 1
            if self.on_page_scanned is not None:
                await self.on_page_scanned()
            if not result.success:
                continue
            text = self._page_text(result=result)
            if mentions_partner_or_director(text):
                kept_for_llm += 1
                yield PageCandidate(
                    url=result.url,
                    title=(result.metadata or {}).get("title", ""),
                    text=text,
                    is_hidden=result.url in hidden_urls,
                )
        logger.info(
            msg=(
                f"Keyword gate {self.domain}: {fetched} fetched, "
                f"{kept_for_llm} kept for LLM"
            )
        )

    @staticmethod
    def _page_text(result: CrawlResult) -> str:
        """Return the best available markdown text for a crawl result."""
        markdown = result.markdown
        return (
            getattr(markdown, "fit_markdown", "")
            or getattr(markdown, "raw_markdown", "")
            or str(markdown or "")
        )
