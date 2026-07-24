from typing import Literal
from urllib.parse import urlencode

from django.conf import settings

from apps.common.services.report_token import ReportTokenService


def build_report_url(
    section: Literal["companies", "persons"], resource_id: str
) -> str:
    """Build a report url based on section and resource id."""
    token = ReportTokenService.sign(resource_id)
    query = urlencode({"token": token})
    base: str = settings.SITE_URL.rstrip("/")  # type: ignore[misc]
    return f"{base}/api/telegram/{section}/{resource_id}?{query}"
