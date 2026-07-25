from datetime import datetime
from types import SimpleNamespace

from services.telegram.handlers.companies.views.company import CompanyView

MARKUP = object()


def test_menu_message_renders_header() -> None:
    """Render the companies menu header with the keyboard."""
    content = CompanyView.build_menu_message(keyboard=MARKUP)

    assert content["text"] == "Companies menu 📊:"
    assert content["reply_markup"] is MARKUP


def test_list_message_shows_pagination_header() -> None:
    """Render the companies list header with its page range and total."""
    content = CompanyView.build_list_message(
        keyboard=MARKUP,
        companies=["first", "second"],
        offset=5,
        total=20,
    )

    assert "Companies 6-7/20 📊:" in content["text"]


def test_list_message_handles_empty_page() -> None:
    """Render a placeholder when the companies page is empty."""
    content = CompanyView.build_list_message(
        keyboard=MARKUP,
        companies=[],
        offset=0,
        total=0,
    )

    assert "empty" in content["text"]


def test_scan_message_renders_scan_details() -> None:
    """Render a company scan with its status and formatted date."""
    company = SimpleNamespace(name="Acme")
    scan = SimpleNamespace(
        get_status_display=lambda: "Completed",
        created_timestamp=datetime(2026, 7, 25, 12, 30, 0),
    )

    content = CompanyView.build_scan_message(
        keyboard=MARKUP,
        company=company,
        scan=scan,
        scan_index=0,
        scans_total=3,
    )

    text = content["text"]
    assert "Acme 📊:" in text
    assert "Scan 1/3 🔎" in text
    assert "Status: Completed" in text
    assert "2026-07-25 12:30:00" in text


def test_scan_message_handles_missing_timestamp() -> None:
    """Render a dash when the scan has no creation timestamp."""
    company = SimpleNamespace(name="Acme")
    scan = SimpleNamespace(
        get_status_display=lambda: "Pending",
        created_timestamp=None,
    )

    content = CompanyView.build_scan_message(
        keyboard=MARKUP,
        company=company,
        scan=scan,
        scan_index=1,
        scans_total=2,
    )

    assert "➖" in content["text"]


def test_scan_message_handles_company_without_scans() -> None:
    """Render a placeholder when the company has no scans."""
    company = SimpleNamespace(name="Acme")

    content = CompanyView.build_scan_message(
        keyboard=MARKUP,
        company=company,
        scan=None,
        scan_index=0,
        scans_total=0,
    )

    assert "No scans found" in content["text"]
