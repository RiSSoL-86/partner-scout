from types import SimpleNamespace
from uuid import uuid4

from services.telegram.handlers.persons.keyboards.person import PersonKeyboard
from services.telegram.handlers.persons.views.person import PersonView
from services.telegram.handlers.persons.views.person_mentions import (
    PersonMentionsView,
)

MARKUP = object()


def test_menu_message_renders_header() -> None:
    """Render the persons menu header with the keyboard."""
    content = PersonView.build_menu_message(keyboard=MARKUP)

    assert content["text"] == "Persons menu 👥:"
    assert content["reply_markup"] is MARKUP


def test_list_message_shows_pagination_header() -> None:
    """Render the persons list header with its page range and total."""
    content = PersonView.build_list_message(
        keyboard=MARKUP,
        persons=["first", "second"],
        offset=5,
        total=42,
    )

    assert "Persons 6-7/42 👥:" in content["text"]


def test_alphabet_message_sums_initial_counts() -> None:
    """Render the alphabet index with the total number of persons."""
    content = PersonView.build_alphabet_message(
        keyboard=MARKUP,
        initials=[("I", 2), ("P", 3)],
    )

    assert "Persons 5 👥:" in content["text"]
    assert "Pick a surname letter" in content["text"]


def test_alphabet_message_handles_no_persons() -> None:
    """Render a placeholder when there are no surname initials."""
    content = PersonView.build_alphabet_message(keyboard=MARKUP, initials=[])

    assert "No persons found" in content["text"]


def test_letter_message_shows_pagination_header() -> None:
    """Render the by-letter header with its page range and total."""
    content = PersonView.build_letter_message(
        keyboard=MARKUP,
        persons=["first", "second"],
        letter="I",
        offset=0,
        total=5,
    )

    assert "Surnames on I 1-2/5 👤:" in content["text"]


def test_letter_message_handles_empty_page() -> None:
    """Render a placeholder when no persons match the letter."""
    content = PersonView.build_letter_message(
        keyboard=MARKUP,
        persons=[],
        letter="Z",
        offset=0,
        total=0,
    )

    assert "No persons for this letter" in content["text"]


def test_list_message_handles_empty_page() -> None:
    """Render a placeholder when the persons page is empty."""
    content = PersonView.build_list_message(
        keyboard=MARKUP,
        persons=[],
        offset=0,
        total=0,
    )

    assert "empty" in content["text"]


def test_menu_message_shows_mentions_count() -> None:
    """Render the person card with their name and mentions count."""
    person = SimpleNamespace(normalized_name="Yakovlev Alexander")

    content = PersonMentionsView.build_person_message(
        keyboard=MARKUP,
        person=person,
        total=3,
    )

    assert "Yakovlev Alexander 👤:" in content["text"]
    assert "Mentions 3 📎" in content["text"]


def test_menu_message_handles_person_without_mentions() -> None:
    """Render a placeholder when the person has no mentions."""
    person = SimpleNamespace(normalized_name="No One")

    content = PersonMentionsView.build_person_message(
        keyboard=MARKUP,
        person=person,
        total=0,
    )

    assert "No mentions found" in content["text"]


def test_list_keyboard_numbers_persons_from_offset() -> None:
    """Number the person buttons continuing from the page offset."""
    persons = [
        SimpleNamespace(id=uuid4(), normalized_name="Ivanov Ivan"),
        SimpleNamespace(id=uuid4(), normalized_name="Petrov Petr"),
    ]

    markup = PersonKeyboard.build_list_keyboard(
        persons=persons,
        offset=10,
        page_size=5,
        total=42,
    )

    labels = [button.text for row in markup.inline_keyboard for button in row]
    assert "11. Ivanov Ivan 📎" in labels
    assert "12. Petrov Petr 📎" in labels
