from typing import TYPE_CHECKING, Any, final

from aiogram.utils.formatting import (
    Text,
    as_line,
    as_list,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

    from apps.companies.models import Company
    from apps.scans.models import Scan


@final
class CompanyView:
    """Build Telegram message payloads for the companies section."""

    @staticmethod
    def build_menu_message(
        keyboard: InlineKeyboardMarkup,
    ) -> dict[str, Any]:
        """Build kwargs for displaying the companies menu."""
        return {
            "text": "Companies menu 📊:",
            "reply_markup": keyboard,
        }

    @staticmethod
    def build_list_message(
        keyboard: InlineKeyboardMarkup,
        companies: list[Company],
        offset: int,
        total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying the companies list."""
        if companies:
            last = offset + len(companies)
            content: Text = as_line(
                f"Companies {offset + 1}-{last}/{total} 📊:"
            )
        else:
            content = Text("Companies list is empty 🤷‍♂️")

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }

    @staticmethod
    def build_scan_message(
        keyboard: InlineKeyboardMarkup,
        company: Company,
        scan: Scan | None,
        scan_index: int,
        scans_total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying one company scan."""
        header = as_line(company.name, " 📊:")
        if scan is not None:
            content = as_list(
                header,
                as_line(f"Scan {scan_index + 1}/{scans_total} 🔎"),
                as_line("Status: ", scan.get_status_display()),
                as_line(
                    "Scan date: ",
                    (
                        scan.created_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if scan.created_timestamp is not None
                        else "➖"
                    ),
                ),
            )
        else:
            content = as_list(
                header,
                Text("No scans found in this company 🤷‍♂️"),
            )

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }
