from typing import TYPE_CHECKING, Any, final

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


@final
class MainView:
    """Build Telegram message payloads for the main menu."""

    @staticmethod
    def build_menu_message(
        keyboard: InlineKeyboardMarkup,
    ) -> dict[str, Any]:
        """Build kwargs for displaying the main menu."""
        return {
            "text": "Partner Scout bot is running 🏃‍♂️ 🏃‍♂️ 🏃‍♂️",
            "reply_markup": keyboard,
        }
