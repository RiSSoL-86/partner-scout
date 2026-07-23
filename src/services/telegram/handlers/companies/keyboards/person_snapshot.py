from typing import TYPE_CHECKING, final

from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.telegram.handlers.companies.callbacks import (
    PersonSnapshotCallback,
    ScanCallback,
)
from services.telegram.handlers.main.callbacks import MainCallback

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


@final
class PersonSnapshotKeyboard:
    """Build inline keyboards for scan person snapshots."""

    @staticmethod
    def build_list_keyboard(
        company_id: str,
        scan_index: int,
        offset: int,
        page_size: int,
        total: int,
    ) -> InlineKeyboardMarkup:
        """Build the person snapshots pagination inline keyboard."""
        builder = InlineKeyboardBuilder()

        nav_count = 0
        if offset > 0:
            builder.button(
                text="⬅️ Previous",
                callback_data=PersonSnapshotCallback(
                    company_id=company_id,
                    scan_index=scan_index,
                    offset=max(offset - page_size, 0),
                ),
            )
            nav_count += 1
        if offset + page_size < total:
            builder.button(
                text="Next ➡️",
                callback_data=PersonSnapshotCallback(
                    company_id=company_id,
                    scan_index=scan_index,
                    offset=offset + page_size,
                ),
            )
            nav_count += 1

        builder.button(
            text="Back ⬅️",
            callback_data=ScanCallback(
                company_id=company_id,
                scan_index=scan_index,
            ),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )

        sizes = [nav_count] if nav_count else []
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()
