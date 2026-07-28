from typing import Literal, final

from aiogram.filters.callback_data import CallbackData


@final
class CompanyCallback(CallbackData, prefix="companies"):
    """Represent navigation payloads inside the companies section."""

    action: Literal["back"]


@final
class CompanyListCallback(CallbackData, prefix="company_list"):
    """Represent navigation payloads for the companies list page."""

    offset: int = 0


@final
class ScanCallback(CallbackData, prefix="scans"):
    """Represent navigation payloads for company scans."""

    company_id: str
    scan_index: int = 0
