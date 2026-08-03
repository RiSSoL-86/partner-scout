import pytest

from services.scanner.crawler.url_collector.utils import is_in_scope


@pytest.mark.parametrize(
    ("url", "domain"),
    [
        ("https://example.com/team", "example.com"),
        ("https://www.example.com/team", "example.com"),
        ("https://example.com/team", "www.example.com"),
        ("http://example.com/a/b?x=1", "example.com"),
    ],
)
def test_in_scope_urls_stay_on_the_company_domain(
    url: str, domain: str
) -> None:
    """Treat www-prefixed and bare host variants as the same domain."""
    assert is_in_scope(url=url, domain=domain) is True


@pytest.mark.parametrize(
    ("url", "domain"),
    [
        ("https://other.com/team", "example.com"),
        ("https://sub.example.com/team", "example.com"),
        ("https://example.org/team", "example.com"),
    ],
)
def test_out_of_scope_urls_are_rejected(url: str, domain: str) -> None:
    """Reject URLs that leave the company domain."""
    assert is_in_scope(url=url, domain=domain) is False
