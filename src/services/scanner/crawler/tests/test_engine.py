from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from apps.sources.choices import PageType
from services.scanner.crawler.engine import CrawlEngine
from services.scanner.crawler.llm_extractor.schemas import (
    CrawledPage,
    PageExtraction,
)
from services.scanner.crawler.url_scanner.schemas import PageCandidate

MODULE = "services.scanner.crawler.engine"


def make_candidate(url: str) -> PageCandidate:
    """Build a keyword-matched candidate page for the given URL."""
    return PageCandidate(url=url, title="Team", text="партнёр")


def make_page(url: str) -> CrawledPage:
    """Build a gate-cleared page for the given URL."""
    return CrawledPage(
        url=url,
        title="Team",
        extraction=PageExtraction(
            is_relevant=True, page_type=PageType.TEAM, persons=[]
        ),
    )


async def stream(items: list[object]) -> AsyncIterator[object]:
    """Yield the given items as an async iterator."""
    for item in items:
        yield item


def build_engine(
    candidates: list[PageCandidate],
    gate: dict[str, CrawledPage | None],
) -> CrawlEngine:
    """Build an engine with its collector, scanner and gate LLM faked out."""
    engine = CrawlEngine(url="https://example.com", company_name="Acme")

    engine.url_collector_service = MagicMock()  # type: ignore[misc]
    engine.url_collector_service.execute = AsyncMock(
        return_value=(["https://example.com/team"], set())
    )

    engine.url_scanner_service = MagicMock()  # type: ignore[misc]
    engine.url_scanner_service.execute = Mock(return_value=stream(candidates))

    engine.llm_extractor_service = MagicMock()  # type: ignore[misc]
    engine.llm_extractor_service.execute = AsyncMock(
        side_effect=lambda candidate: gate[candidate.url]
    )
    return engine


async def drain(engine: CrawlEngine) -> list[CrawledPage]:
    """Run a crawl inside a patched browser and collect its pages."""
    crawler = MagicMock()
    browser = MagicMock()
    browser.__aenter__ = AsyncMock(return_value=crawler)
    browser.__aexit__ = AsyncMock(return_value=False)
    with patch(f"{MODULE}.AsyncWebCrawler", Mock(return_value=browser)):
        return [page async for page in engine.crawl()]


def test_init_derives_the_domain_from_the_url() -> None:
    """Take the scan domain from the seed URL's host."""
    engine = CrawlEngine(url="https://www.example.com/team")

    assert engine.domain == "www.example.com"


async def test_yields_only_pages_the_gate_clears() -> None:
    """Emit gate-cleared pages and drop the ones the gate rejects."""
    candidates = [
        make_candidate("https://example.com/a"),
        make_candidate("https://example.com/b"),
        make_candidate("https://example.com/c"),
    ]
    gate: dict[str, CrawledPage | None] = {
        "https://example.com/a": make_page("https://example.com/a"),
        "https://example.com/b": None,
        "https://example.com/c": make_page("https://example.com/c"),
    }
    engine = build_engine(candidates, gate)

    pages = await drain(engine)

    assert {page.url for page in pages} == {
        "https://example.com/a",
        "https://example.com/c",
    }


async def test_yields_nothing_when_no_candidates_match() -> None:
    """Emit nothing when the keyword scan kept no candidates."""
    engine = build_engine(candidates=[], gate={})

    pages = await drain(engine)

    assert pages == []


async def test_logs_gate_usage_after_the_crawl() -> None:
    """Log the gate LLM token spend once the crawl finishes."""
    engine = build_engine(candidates=[], gate={})

    await drain(engine)

    engine.llm_extractor_service.log_usage.assert_called_once_with(
        domain="example.com"
    )


async def test_logs_gate_usage_even_when_the_scan_fails() -> None:
    """Log the gate usage even if walking the site raises."""
    engine = build_engine(candidates=[], gate={})
    engine.url_collector_service.execute = AsyncMock(
        side_effect=RuntimeError("seeding boom")
    )

    try:
        await drain(engine)
    except RuntimeError:
        pass

    engine.llm_extractor_service.log_usage.assert_called_once_with(
        domain="example.com"
    )
