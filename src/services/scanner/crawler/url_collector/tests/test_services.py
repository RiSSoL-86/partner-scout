from unittest.mock import AsyncMock, Mock, patch

from services.scanner.crawler.url_collector.services import (
    RobotsSeederService,
    SitemapSeederService,
    UrlCollectorService,
)

MODULE = "services.scanner.crawler.url_collector.services"


# --- UrlCollectorService ---------------------------------------------------


def make_collector(
    sitemap_urls: list[str], robots_urls: list[str]
) -> UrlCollectorService:
    """Build a collector whose two seeders return fixed URL lists."""
    collector = UrlCollectorService(domain="example.com")
    collector.sitemap_seeder = AsyncMock()  # type: ignore[misc]
    collector.sitemap_seeder.execute.return_value = sitemap_urls
    collector.robots_seeder = AsyncMock()  # type: ignore[misc]
    collector.robots_seeder.execute.return_value = robots_urls
    return collector


async def test_merges_sitemap_and_robots_dropping_duplicates() -> None:
    """Merge both sources, sitemap first, dropping duplicate URLs."""
    collector = make_collector(
        sitemap_urls=["https://example.com/a", "https://example.com/b"],
        robots_urls=["https://example.com/b", "https://example.com/secret"],
    )

    fetch_urls, hidden_urls = await collector.execute()

    assert fetch_urls == [
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/secret",
    ]


async def test_marks_robots_only_urls_as_hidden() -> None:
    """Flag URLs absent from the sitemap as robots-hidden."""
    collector = make_collector(
        sitemap_urls=["https://example.com/a"],
        robots_urls=["https://example.com/secret"],
    )

    _, hidden_urls = await collector.execute()

    assert hidden_urls == {"https://example.com/secret"}


async def test_caps_the_fetch_list_at_the_configured_limit(settings) -> None:
    """Never return more URLs than the crawler page limit allows."""
    settings.CRAWLER_MAX_PAGES = 2
    collector = make_collector(
        sitemap_urls=["https://example.com/a", "https://example.com/b"],
        robots_urls=["https://example.com/c"],
    )

    fetch_urls, _ = await collector.execute()

    assert fetch_urls == ["https://example.com/a", "https://example.com/b"]


# --- SitemapSeederService --------------------------------------------------


class FakeSeeder:
    """Async-context stand-in for crawl4ai's AsyncUrlSeeder."""

    def __init__(self, seeds: list[dict[str, str]] | None = None) -> None:
        """Store the seeds the fake should yield, or arm a failure."""
        self._seeds = seeds

    async def __aenter__(self) -> FakeSeeder:
        """Enter the async context, returning the seeder itself."""
        return self

    async def __aexit__(self, *args: object) -> bool:
        """Leave the async context without suppressing errors."""
        return False

    async def urls(self, domain: str, config: object) -> list[dict[str, str]]:
        """Return the configured seeds or raise when none were armed."""
        if self._seeds is None:
            raise RuntimeError("seeding boom")
        return self._seeds


async def test_sitemap_keeps_only_in_scope_urls() -> None:
    """Return only sitemap URLs that stay on the company domain."""
    seeds = [
        {"url": "https://example.com/team"},
        {"url": "https://other.com/team"},
        {"url": "https://example.com/about"},
    ]
    with patch(
        f"{MODULE}.AsyncUrlSeeder", Mock(return_value=FakeSeeder(seeds))
    ):
        urls = await SitemapSeederService(domain="example.com").execute()

    assert urls == [
        "https://example.com/team",
        "https://example.com/about",
    ]


async def test_sitemap_returns_empty_when_seeding_fails() -> None:
    """Return an empty list when sitemap seeding raises."""
    with patch(f"{MODULE}.AsyncUrlSeeder", Mock(return_value=FakeSeeder())):
        urls = await SitemapSeederService(domain="example.com").execute()

    assert urls == []


# --- RobotsSeederService ---------------------------------------------------


class FakeResponse:
    """Minimal httpx response stand-in exposing text and status raising."""

    def __init__(self, text: str) -> None:
        """Store the robots.txt body to serve back."""
        self.text = text

    def raise_for_status(self) -> None:
        """Pretend the response status was successful."""


class FakeHttpClient:
    """Async-context httpx client stand-in over a single response."""

    def __init__(
        self,
        response: FakeResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        """Arm the client with a response to serve or an error to raise."""
        self._response = response
        self._error = error

    async def __aenter__(self) -> FakeHttpClient:
        """Enter the async context, returning the client itself."""
        return self

    async def __aexit__(self, *args: object) -> bool:
        """Leave the async context without suppressing errors."""
        return False

    async def get(self, url: str) -> FakeResponse:
        """Return the armed response or raise the armed error."""
        if self._error is not None:
            raise self._error
        assert self._response is not None
        return self._response


def patch_client(
    response: FakeResponse | None, error: Exception | None = None
):
    """Patch the robots seeder's httpx client with a fake one."""
    return patch(
        f"{MODULE}.httpx.AsyncClient",
        Mock(return_value=FakeHttpClient(response=response, error=error)),
    )


async def test_robots_returns_wildcard_disallowed_in_scope_urls() -> None:
    """Collect in-scope Disallow paths under the wildcard user-agent."""
    robots = "\n".join(
        [
            "User-agent: *",
            "Disallow: /secret",
            "Disallow: /team/  # hidden staff list",
            "Allow: /public",
        ]
    )
    with patch_client(FakeResponse(robots)):
        urls = await RobotsSeederService(domain="example.com").execute()

    assert urls == [
        "https://example.com/secret",
        "https://example.com/team/",
    ]


async def test_robots_ignores_rules_for_other_user_agents() -> None:
    """Keep only the rules that apply to every user-agent."""
    robots = "\n".join(
        [
            "User-agent: BadBot",
            "Disallow: /private",
            "User-agent: *",
            "Disallow: /shared",
        ]
    )
    with patch_client(FakeResponse(robots)):
        urls = await RobotsSeederService(domain="example.com").execute()

    assert urls == ["https://example.com/shared"]


async def test_robots_skips_wildcard_and_anchor_patterns() -> None:
    """Drop pattern rules that cannot map to a concrete URL."""
    robots = "\n".join(
        [
            "User-agent: *",
            "Disallow: /*.pdf$",
            "Disallow: /reports/*",
            "Disallow: /clean",
        ]
    )
    with patch_client(FakeResponse(robots)):
        urls = await RobotsSeederService(domain="example.com").execute()

    assert urls == ["https://example.com/clean"]


async def test_robots_skips_out_of_scope_and_empty_disallow() -> None:
    """Drop off-domain and empty (allow-all) Disallow rules."""
    robots = "\n".join(
        [
            "User-agent: *",
            "Disallow:",
            "Disallow: https://other.com/x",
            "Disallow: /stay",
        ]
    )
    with patch_client(FakeResponse(robots)):
        urls = await RobotsSeederService(domain="example.com").execute()

    assert urls == ["https://example.com/stay"]


async def test_robots_returns_empty_when_fetch_fails() -> None:
    """Return an empty list when robots.txt cannot be fetched."""
    with patch_client(None, error=RuntimeError("robots boom")):
        urls = await RobotsSeederService(domain="example.com").execute()

    assert urls == []
