from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING
from uuid import uuid4

from services.telegram.handlers.persons.keyboards.person import PersonKeyboard
from services.telegram.handlers.persons.keyboards.person_mentions import (
    PersonMentionsKeyboard,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def _labels(markup: InlineKeyboardMarkup) -> list[str]:
    return [button.text for row in markup.inline_keyboard for button in row]


def _person(name: str) -> SimpleNamespace:
    return SimpleNamespace(id=uuid4(), normalized_name=name)


def test_menu_keyboard_lists_actions() -> None:
    """Offer list, alphabet, back and exit in the menu keyboard."""
    labels = _labels(PersonKeyboard.build_menu_keyboard())

    assert labels == [
        "All persons 📋",
        "By alphabet 🔤",
        "Back ⬅️",
        "Exit ❌",
    ]


def test_list_keyboard_shows_both_navigation_buttons() -> None:
    """Show previous and next on a middle page of the persons list."""
    persons = [_person(f"Person {i}") for i in range(5)]

    labels = _labels(
        PersonKeyboard.build_list_keyboard(
            persons=persons,
            offset=5,
            page_size=5,
            total=20,
        ),
    )

    assert "6. Person 0 📎" in labels
    assert "⬅️ Previous" in labels
    assert "Next ➡️" in labels


def test_list_keyboard_without_navigation_on_single_page() -> None:
    """Hide navigation when a single page fits the total."""
    labels = _labels(
        PersonKeyboard.build_list_keyboard(
            persons=[_person("Solo")],
            offset=0,
            page_size=5,
            total=1,
        ),
    )

    assert "⬅️ Previous" not in labels
    assert "Next ➡️" not in labels


def test_alphabet_keyboard_lists_initials_with_counts() -> None:
    """Render one button per surname initial with its count."""
    initials = [("A", 1), ("B", 2), ("C", 3)]

    labels = _labels(PersonKeyboard.build_alphabet_keyboard(initials=initials))

    assert "A (1)" in labels
    assert "B (2)" in labels
    assert "C (3)" in labels
    assert "Back ⬅️" in labels


def test_alphabet_keyboard_wraps_rows_with_remainder() -> None:
    """Wrap initials into rows of five leaving the remainder last."""
    initials = [(chr(ord("A") + i), 1) for i in range(7)]

    markup = PersonKeyboard.build_alphabet_keyboard(initials=initials)

    row_sizes = [len(row) for row in markup.inline_keyboard]
    # 7 initials -> a row of 5 and a row of 2, then two single action rows.
    assert row_sizes == [5, 2, 1, 1]


def test_letter_keyboard_numbers_persons_and_navigates() -> None:
    """Number by-letter persons and expose a next page button."""
    persons = [_person("Ivanov Ivan"), _person("Ivanova Anna")]

    labels = _labels(
        PersonKeyboard.build_letter_keyboard(
            persons=persons,
            letter="I",
            offset=0,
            page_size=2,
            total=5,
        ),
    )

    assert "1. Ivanov Ivan 📎" in labels
    assert "Next ➡️" in labels
    assert "⬅️ Previous" not in labels


def test_letter_keyboard_shows_previous_on_later_pages() -> None:
    """Expose a previous page button once past the first by-letter page."""
    persons = [_person("Ivanov Ivan")]

    labels = _labels(
        PersonKeyboard.build_letter_keyboard(
            persons=persons,
            letter="I",
            offset=2,
            page_size=2,
            total=3,
        ),
    )

    assert "⬅️ Previous" in labels
    assert "Next ➡️" not in labels


def test_mentions_keyboard_shows_report_for_https_url() -> None:
    """Show the report button when the url is a secure link."""
    labels = _labels(
        PersonMentionsKeyboard.build_person_keyboard(
            report_url="https://example.com/report",
        ),
    )

    assert "Open report 🌐" in labels
    assert "Back ⬅️" in labels
    assert "Exit ❌" in labels


def test_mentions_keyboard_hides_report_without_https_url() -> None:
    """Hide the report button when no secure url is provided."""
    labels = _labels(
        PersonMentionsKeyboard.build_person_keyboard(report_url=""),
    )

    assert "Open report 🌐" not in labels
    assert "Back ⬅️" in labels


def _report_button(markup: InlineKeyboardMarkup) -> object:
    for row in markup.inline_keyboard:
        for button in row:
            if button.text == "Open report 🌐":
                return button
    raise AssertionError("report button not found")


def test_mentions_keyboard_uses_web_app_in_private_chat() -> None:
    """Open the report as a Web App in a private chat."""
    button = _report_button(
        PersonMentionsKeyboard.build_person_keyboard(
            report_url="https://example.com/report",
            is_private=True,
        ),
    )

    assert button.web_app is not None
    assert button.url is None


def test_mentions_keyboard_uses_url_in_group_chat() -> None:
    """Fall back to a url button outside of private chats."""
    button = _report_button(
        PersonMentionsKeyboard.build_person_keyboard(
            report_url="https://example.com/report",
            is_private=False,
        ),
    )

    assert button.web_app is None
    assert button.url == "https://example.com/report"
