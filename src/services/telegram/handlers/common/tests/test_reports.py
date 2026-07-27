from urllib.parse import parse_qs, urlsplit

from django.test import override_settings

from apps.common.services.report_token import ReportTokenService
from services.telegram.handlers.common.reports import build_report_url


@override_settings(SITE_URL="https://example.com/")
def test_build_report_url_strips_trailing_slash_and_signs() -> None:
    """Compose a signed report url without a doubled slash."""
    url = build_report_url("persons", "abc-123")

    assert url.startswith(
        "https://example.com/api/telegram/persons/abc-123/?",
    )
    assert "token=" in url


@override_settings(SITE_URL="https://example.com")
def test_build_report_url_embeds_section_and_valid_token() -> None:
    """Embed the section path and a token the service can verify."""
    url = build_report_url("companies/scans", "scan-id")

    assert "/api/telegram/companies/scans/scan-id/?" in url
    token = parse_qs(urlsplit(url).query)["token"][0]
    assert ReportTokenService.unsign(token) == "scan-id"
