from typing import TYPE_CHECKING, final

from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.telegram.handlers.main.callbacks import MainCallback
from services.telegram.handlers.persons.callbacks import (
    PersonCallback,
    PersonLetterCallback,
    PersonListCallback,
    PersonMentionCallback,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from aiogram.types import InlineKeyboardMarkup

    from apps.persons.models import Person

ALPHABET_ROW_SIZE = 5


@final
class PersonKeyboard:
    """Build inline keyboards for the persons section."""

    @staticmethod
    def build_menu_keyboard() -> InlineKeyboardMarkup:
        """Build the persons section menu inline keyboard."""
        builder = InlineKeyboardBuilder()
        builder.button(
            text="All persons 📋",
            callback_data=PersonListCallback(),
        )
        builder.button(
            text="By alphabet 🔤",
            callback_data=PersonCallback(action="alphabet"),
        )
        builder.button(
            text="Back ⬅️",
            callback_data=PersonCallback(action="back"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def build_list_keyboard(
        persons: Sequence[Person],
        offset: int,
        page_size: int,
        total: int,
    ) -> InlineKeyboardMarkup:
        """Build the full persons list inline keyboard."""
        builder = InlineKeyboardBuilder()
        for person in persons:
            builder.button(
                text=f"Mentions: {person.normalized_name} 📎",
                callback_data=PersonMentionCallback(person_id=str(person.id)),
            )

        nav_count = 0
        if offset > 0:
            builder.button(
                text="⬅️ Previous",
                callback_data=PersonListCallback(
                    offset=max(offset - page_size, 0),
                ),
            )
            nav_count += 1
        if offset + page_size < total:
            builder.button(
                text="Next ➡️",
                callback_data=PersonListCallback(offset=offset + page_size),
            )
            nav_count += 1

        builder.button(
            text="Back ⬅️",
            callback_data=PersonCallback(action="menu"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )

        sizes = [1] * len(persons)
        if nav_count:
            sizes.append(nav_count)
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()

    @staticmethod
    def build_alphabet_keyboard(
        initials: Sequence[tuple[str, int]],
    ) -> InlineKeyboardMarkup:
        """Build the surname-initial alphabet index inline keyboard."""
        builder = InlineKeyboardBuilder()
        for initial, total in initials:
            builder.button(
                text=f"{initial} ({total})",
                callback_data=PersonLetterCallback(letter=initial),
            )

        builder.button(
            text="Back ⬅️",
            callback_data=PersonCallback(action="menu"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )

        full_rows, remainder = divmod(len(initials), ALPHABET_ROW_SIZE)
        sizes = [ALPHABET_ROW_SIZE] * full_rows
        if remainder:
            sizes.append(remainder)
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()

    @staticmethod
    def build_letter_keyboard(
        persons: Sequence[Person],
        letter: str,
        offset: int,
        page_size: int,
        total: int,
    ) -> InlineKeyboardMarkup:
        """Build the persons-by-letter list inline keyboard."""
        builder = InlineKeyboardBuilder()
        for person in persons:
            builder.button(
                text=f"Mentions: {person.normalized_name} 📎",
                callback_data=PersonMentionCallback(person_id=str(person.id)),
            )

        nav_count = 0
        if offset > 0:
            builder.button(
                text="⬅️ Previous",
                callback_data=PersonLetterCallback(
                    letter=letter,
                    offset=max(offset - page_size, 0),
                ),
            )
            nav_count += 1
        if offset + page_size < total:
            builder.button(
                text="Next ➡️",
                callback_data=PersonLetterCallback(
                    letter=letter,
                    offset=offset + page_size,
                ),
            )
            nav_count += 1

        builder.button(
            text="Back ⬅️",
            callback_data=PersonCallback(action="alphabet"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )

        sizes = [1] * len(persons)
        if nav_count:
            sizes.append(nav_count)
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()
