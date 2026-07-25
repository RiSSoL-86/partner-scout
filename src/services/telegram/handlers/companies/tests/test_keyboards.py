from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING
from uuid import uuid4

from services.telegram.handlers.companies.keyboards.company import (
    CompanyKeyboard,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def _labels(markup: InlineKeyboardMarkup) -> list[str]:
    return [button.text for row in markup.inline_keyboard for button in row]


def test_menu_keyboard_lists_actions() -> None:
    """Offer the list, back and exit actions in the menu keyboard."""
    labels = _labels(CompanyKeyboard.build_menu_keyboard())

    assert labels == ["All companies 📈", "Back ⬅️", "Exit ❌"]


def test_list_keyboard_numbers_companies_from_offset() -> None:
    """Number the company buttons continuing from the page offset."""
    companies = [
        SimpleNamespace(id=uuid4(), name="Acme"),
        SimpleNamespace(id=uuid4(), name="Globex"),
    ]

    markup = CompanyKeyboard.build_list_keyboard(
        companies=companies,
        offset=10,
        page_size=5,
        total=42,
    )

    labels = _labels(markup)
    assert "11. Acme 🔎" in labels
    assert "12. Globex 🔎" in labels


def test_list_keyboard_without_navigation_on_single_page() -> None:
    """Hide navigation buttons when a single page fits the total."""
    companies = [SimpleNamespace(id=uuid4(), name="Acme")]

    labels = _labels(
        CompanyKeyboard.build_list_keyboard(
            companies=companies,
            offset=0,
            page_size=5,
            total=1,
        ),
    )

    assert "⬅️ Previous" not in labels
    assert "Next ➡️" not in labels


def test_list_keyboard_shows_both_navigation_buttons() -> None:
    """Show previous and next when a middle page has neighbours."""
    companies = [SimpleNamespace(id=uuid4(), name=f"C{i}") for i in range(5)]

    labels = _labels(
        CompanyKeyboard.build_list_keyboard(
            companies=companies,
            offset=5,
            page_size=5,
            total=20,
        ),
    )

    assert "⬅️ Previous" in labels
    assert "Next ➡️" in labels


def test_scan_keyboard_shows_navigation_and_report() -> None:
    """Show both scan navigations and the report link in the middle."""
    labels = _labels(
        CompanyKeyboard.build_scan_keyboard(
            company_id="cid",
            scan_index=1,
            scans_total=3,
            report_url="https://example.com/report",
        ),
    )

    assert "⬅️ Previous scan" in labels
    assert "Next scan ➡️" in labels
    assert "Open report 🌐" in labels


def test_scan_keyboard_hides_navigation_and_report_at_edges() -> None:
    """Hide navigation and report for the only scan without a url."""
    labels = _labels(
        CompanyKeyboard.build_scan_keyboard(
            company_id="cid",
            scan_index=0,
            scans_total=1,
            report_url="",
        ),
    )

    assert "⬅️ Previous scan" not in labels
    assert "Next scan ➡️" not in labels
    assert "Open report 🌐" not in labels
    assert "Back ⬅️" in labels
    assert "Exit ❌" in labels
