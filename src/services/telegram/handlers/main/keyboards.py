from typing import TYPE_CHECKING, final

from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.telegram.handlers.main.callbacks import MainCallback

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


@final
class MainKeyboard:
    """Build inline keyboards for the main menu."""

    @staticmethod
    def build_menu_keyboard() -> InlineKeyboardMarkup:
        """Build the main menu inline keyboard."""
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Companies 📊",
            callback_data=MainCallback(section="companies"),
        )
        builder.button(
            text="Exit ❌",
            callback_data=MainCallback(section="close"),
        )
        builder.adjust(1)
        return builder.as_markup()
