from typing import TYPE_CHECKING, Any, final

from aiogram.utils.formatting import (
    Text,
    as_line,
    as_list,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from aiogram.types import InlineKeyboardMarkup

    from apps.persons.models import Person


@final
class PersonView:
    """Build Telegram message payloads for the persons section."""

    @staticmethod
    def build_menu_message(
        keyboard: InlineKeyboardMarkup,
    ) -> dict[str, Any]:
        """Build kwargs for displaying the persons menu."""
        return {
            "text": "Persons menu 👥:",
            "reply_markup": keyboard,
        }

    @staticmethod
    def build_list_message(
        keyboard: InlineKeyboardMarkup,
        persons: Sequence[Person],
        offset: int,
        total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying a page of all persons."""
        if persons:
            header = (
                f"Persons {offset + 1}-{offset + len(persons)}/{total} 👥:"
            )
            content = as_list(
                as_line(header),
                *(
                    as_list(
                        as_line(f"{offset + index}. ", person.normalized_name),
                        as_line("ID: ", person.id),
                        as_line("\n"),
                    )
                    for index, person in enumerate(persons, start=1)
                ),
            )
        else:
            content = Text("Persons list is empty 🤷‍♂️")

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }

    @staticmethod
    def build_alphabet_message(
        keyboard: InlineKeyboardMarkup,
        initials: Sequence[tuple[str, int]],
    ) -> dict[str, Any]:
        """Build kwargs for displaying the surname alphabet index."""
        if initials:
            total = sum(count for _, count in initials)
            content = as_list(
                as_line(f"Persons {total} 👥:"),
                as_line("Pick a surname letter:"),
            )
        else:
            content = Text("No persons found 🤷‍♂️")

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }

    @staticmethod
    def build_letter_message(
        keyboard: InlineKeyboardMarkup,
        persons: Sequence[Person],
        letter: str,
        offset: int,
        total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying a page of persons by surname letter."""
        if persons:
            content = as_list(
                as_line(
                    f"Surnames on {letter} {offset + 1}-"
                    f"{offset + len(persons)}/{total} 👤:",
                ),
                *(
                    as_list(
                        as_line(f"{offset + index}. ", person.normalized_name),
                        as_line("ID: ", person.id),
                        as_line("\n"),
                    )
                    for index, person in enumerate(persons, start=1)
                ),
            )
        else:
            content = Text("No persons for this letter 🤷‍♂️")

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }
