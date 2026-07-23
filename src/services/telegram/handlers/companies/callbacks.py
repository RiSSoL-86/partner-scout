from typing import Literal

from aiogram.filters.callback_data import CallbackData


class CompanyCallback(CallbackData, prefix="companies"):
    """Represent navigation payloads inside the companies section."""

    action: Literal["list", "back"]


class ScanCallback(CallbackData, prefix="scans"):
    """Represent navigation payloads for company scans."""

    company_id: str
    scan_index: int = 0


class PersonSnapshotCallback(CallbackData, prefix="snapshots"):
    """Represent navigation payloads for scan person snapshots."""

    company_id: str
    scan_index: int = 0
    offset: int = 0
