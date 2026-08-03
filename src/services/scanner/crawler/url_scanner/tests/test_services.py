from collections.abc import AsyncIterator
from types import SimpleNamespace
from unittest.mock import AsyncMock

from services.scanner.crawler.url_scanner.services import UrlScannerService


def make_result(
    url: str, text: str, *, success: bool = True, title: str = ""
) -> SimpleNamespace:
    """Build a crawl-result stand-in exposing the fields the scanner reads."""
    return SimpleNamespace(
        url=url,
        success=success,
        metadata={"title": title},
        markdown=SimpleNamespace(fit_markdown=text, raw_markdown=text),
    )


async def as_async_iter(items: list[object]) -> AsyncIterator[object]:
    """Yield the given items as an async iterator."""
    for item in items:
        yield item


def make_crawler(results: list[object]) -> AsyncMock:
    """Build a crawler whose arun_many streams the given results."""
    crawler = AsyncMock()
    crawler.arun_many.return_value = as_async_iter(results)
    return crawler


async def collect(scanner: UrlScannerService, crawler, urls: list[str]):
    """Drain the scanner's async generator into a list of candidates."""
    return [
        candidate
        async for candidate in scanner.execute(
            crawler=crawler,
            fetch_urls=urls,
            hidden_urls={"https://example.com/secret"},
        )
    ]


async def test_keeps_only_keyword_matched_pages() -> None:
    """Yield candidates only for pages that mention a target position."""
    crawler = make_crawler(
        [
            make_result(
                "https://example.com/team", "Иван Петров, партнёр практики"
            ),
            make_result(
                "https://example.com/news", "Company opened an office"
            ),
        ]
    )
    scanner = UrlScannerService(domain="example.com")

    candidates = await collect(scanner, crawler, ["https://example.com/team"])

    assert [candidate.url for candidate in candidates] == [
        "https://example.com/team"
    ]


async def test_flags_hidden_candidates() -> None:
    """Mark a candidate hidden when its URL is in the hidden set."""
    crawler = make_crawler(
        [make_result("https://example.com/secret", "директор аудита")]
    )
    scanner = UrlScannerService(domain="example.com")

    candidates = await collect(
        scanner, crawler, ["https://example.com/secret"]
    )

    assert candidates[0].is_hidden is True


async def test_reports_every_fetched_page_including_failures() -> None:
    """Signal a scanned page for each fetch, even failed ones."""
    on_page_scanned = AsyncMock()
    crawler = make_crawler(
        [
            make_result("https://example.com/team", "партнёр"),
            make_result("https://example.com/down", "", success=False),
        ]
    )
    scanner = UrlScannerService(
        domain="example.com", on_page_scanned=on_page_scanned
    )

    await collect(scanner, crawler, ["https://example.com/team"])

    assert on_page_scanned.await_count == 2


async def test_yields_nothing_without_urls_to_fetch() -> None:
    """Skip fetching entirely when there are no URLs to scan."""
    crawler = AsyncMock()
    scanner = UrlScannerService(domain="example.com")

    candidates = await collect(scanner, crawler, [])

    assert candidates == []
    crawler.arun_many.assert_not_called()
