from collections.abc import Sequence
from typing import TYPE_CHECKING, final

from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.telegram.handlers.companies.callbacks import (
    CompanyCallback,
    PersonSnapshotCallback,
    ScanCallback,
)
from services.telegram.handlers.main.callbacks import MainCallback

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

    from apps.companies.models import Company


@final
class CompanyKeyboard:
    """Build inline keyboards for the companies section."""

    @staticmethod
    def build_menu_keyboard() -> InlineKeyboardMarkup:
        """Build the companies section inline keyboard."""
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Companies list 📈",
            callback_data=CompanyCallback(action="list"),
        )
        builder.button(
            text="Back ⬅️",
            callback_data=CompanyCallback(action="back"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def build_list_keyboard(
        companies: Sequence[Company],
    ) -> InlineKeyboardMarkup:
        """Build the companies list actions inline keyboard."""
        builder = InlineKeyboardBuilder()
        for company in companies:
            builder.button(
                text=f"Details: {company.name} 🔎",
                callback_data=ScanCallback(company_id=str(company.id)),
            )

        builder.button(
            text="Back ⬅️",
            callback_data=CompanyCallback(action="back"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def build_scan_keyboard(
        company_id: str,
        scan_index: int,
        scans_total: int,
    ) -> InlineKeyboardMarkup:
        """Build the company scan navigation inline keyboard."""
        builder = InlineKeyboardBuilder()

        has_older = scan_index + 1 < scans_total
        has_newer = scan_index > 0
        can_view_snapshots = scans_total > 0

        sizes: list[int] = []

        nav_count = 0
        if has_older:
            builder.button(
                text="⬅️ Previous scan",
                callback_data=ScanCallback(
                    company_id=company_id,
                    scan_index=scan_index + 1,
                ),
            )
            nav_count += 1
        if has_newer:
            builder.button(
                text="Next scan ➡️",
                callback_data=ScanCallback(
                    company_id=company_id,
                    scan_index=scan_index - 1,
                ),
            )
            nav_count += 1
        if nav_count:
            sizes.append(nav_count)

        if can_view_snapshots:
            builder.button(
                text="People found 👥",
                callback_data=PersonSnapshotCallback(
                    company_id=company_id,
                    scan_index=scan_index,
                ),
            )
            sizes.append(1)

        builder.button(
            text="Back ⬅️",
            callback_data=CompanyCallback(action="list"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()
