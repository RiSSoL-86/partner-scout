from typing import TYPE_CHECKING, final

from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.telegram.handlers.main.callbacks import MainCallback
from services.telegram.handlers.persons.callbacks import (
    PersonCallback,
    PersonMentionCallback,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


@final
class PersonMentionKeyboard:
    """Build inline keyboards for person mentions."""

    @staticmethod
    def build_list_keyboard(
        person_id: str,
        offset: int,
        page_size: int,
        total: int,
    ) -> InlineKeyboardMarkup:
        """Build the person mentions pagination inline keyboard."""
        builder = InlineKeyboardBuilder()

        nav_count = 0
        if offset > 0:
            builder.button(
                text="⬅️ Previous",
                callback_data=PersonMentionCallback(
                    person_id=person_id,
                    offset=max(offset - page_size, 0),
                ),
            )
            nav_count += 1
        if offset + page_size < total:
            builder.button(
                text="Next ➡️",
                callback_data=PersonMentionCallback(
                    person_id=person_id,
                    offset=offset + page_size,
                ),
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

        sizes = [nav_count] if nav_count else []
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()
