import json
import logging
from collections.abc import AsyncIterator
from typing import final
from urllib.parse import urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMConfig,
    LLMExtractionStrategy,
)
from crawl4ai.deep_crawling import (
    BestFirstCrawlingStrategy,
    DomainFilter,
    FilterChain,
    KeywordRelevanceScorer,
    URLPatternFilter,
)
from django.conf import settings
from pydantic import ValidationError

from services.scanner.crawler.core.rules import (
    GATE_INSTRUCTION,
    RELEVANCE_KEYWORDS,
    URL_EXCLUDE,
    URL_INCLUDE,
)
from services.scanner.crawler.schemas import CrawledPage, PageExtraction

logger = logging.getLogger(__name__)


@final
class CrawlEngine:
    """Crawl a company site and stream candidate pages with a verdict."""

    def __init__(self, url: str) -> None:
        """Prepare the browser and run config for one company site."""
        self.url = url
        self.browser_config = BrowserConfig(
            headless=settings.CRAWLER_HEADLESS,  # type: ignore[misc]
            extra_args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        self.crawler_run_config = CrawlerRunConfig(
            deep_crawl_strategy=BestFirstCrawlingStrategy(
                max_depth=settings.CRAWLER_MAX_DEPTH,  # type: ignore[misc]
                max_pages=settings.CRAWLER_MAX_PAGES,  # type: ignore[misc]
                include_external=False,  # don't leave the work site
                filter_chain=FilterChain(
                    [
                        DomainFilter(allowed_domains=urlparse(url).netloc),
                        URLPatternFilter(
                            patterns=[
                                f"*{fragment}*" for fragment in URL_EXCLUDE
                            ],
                            reverse=True,
                        ),
                    ]
                ),
                url_scorer=KeywordRelevanceScorer(
                    keywords=[*URL_INCLUDE, *RELEVANCE_KEYWORDS],
                ),
                score_threshold=settings.CRAWLER_SCORE_THRESHOLD,  # type: ignore[misc]
            ),
            extraction_strategy=LLMExtractionStrategy(
                llm_config=LLMConfig(
                    provider=settings.CRAWLER_LLM_MODEL,  # type: ignore[misc]
                    api_token=settings.OPENAI_API_KEY,  # type: ignore[misc]
                    temperature=settings.CRAWLER_LLM_TEMPERATURE,  # type: ignore[misc]
                ),
                instruction=GATE_INSTRUCTION,
                schema=PageExtraction.model_json_schema(),
                extraction_type="schema",
                input_format="markdown",
                apply_chunking=False,
            ),
            excluded_tags=["script", "style", "nav", "header", "footer"],
            cache_mode=CacheMode.BYPASS,
            page_timeout=settings.CRAWLER_PAGE_TIMEOUT,  # type: ignore[misc]
            stream=True,
        )

    async def crawl(self) -> AsyncIterator[CrawledPage]:
        """Yield relevance-gated pages discovered from the seed URL."""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            async for result in await crawler.arun(
                url=self.url, config=self.crawler_run_config
            ):
                extracted_content = result.extracted_content
                if not result.success or not extracted_content:
                    continue

                try:
                    data = json.loads(extracted_content)
                except json.JSONDecodeError:
                    logger.warning(msg="Gate returned non-JSON payload")
                    continue

                if isinstance(data, list):
                    data = data[0] if data else {}

                try:
                    extraction = PageExtraction.model_validate(data)
                except ValidationError:
                    logger.warning(
                        msg="Gate payload did not match the page schema"
                    )
                    continue

                markdown = result.markdown
                text = (
                    getattr(markdown, "fit_markdown", "")
                    or getattr(markdown, "raw_markdown", "")
                    or str(markdown or "")
                )

                yield CrawledPage(
                    url=result.url,
                    title=(result.metadata or {}).get("title", ""),
                    content=text[: settings.CRAWLER_MAX_CONTENT_CHARS],  # type: ignore[misc]
                    extraction=extraction,
                )
