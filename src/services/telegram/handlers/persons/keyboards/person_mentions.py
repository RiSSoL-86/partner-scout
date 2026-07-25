from typing import TYPE_CHECKING, final

from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.telegram.handlers.main.callbacks import MainCallback
from services.telegram.handlers.persons.callbacks import PersonCallback

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


@final
class PersonMentionsKeyboard:
    """Build inline keyboards for the person card."""

    @staticmethod
    def build_person_keyboard(report_url: str) -> InlineKeyboardMarkup:
        """Build the person card inline keyboard with a report link."""
        builder = InlineKeyboardBuilder()

        sizes: list[int] = []
        if report_url.startswith("https://"):
            builder.button(
                text="Open report 🌐",
                web_app=WebAppInfo(url=report_url),
            )
            sizes.append(1)

        builder.button(
            text="Back ⬅️",
            callback_data=PersonCallback(action="menu"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )
        sizes.extend((1, 1))
        builder.adjust(*sizes)
        return builder.as_markup()
