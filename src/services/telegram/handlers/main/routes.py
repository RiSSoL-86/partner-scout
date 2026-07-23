from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart

from services.telegram.handlers.common.decorators import require_message
from services.telegram.handlers.main.callbacks import MainCallback
from services.telegram.handlers.main.keyboards import MainKeyboard
from services.telegram.handlers.main.views import MainView

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, Message

router = Router(name="main")


@router.message(CommandStart())
async def show_main_menu(message: Message) -> None:
    """Show the main Telegram menu."""
    keyboard = MainKeyboard.build_menu_keyboard()
    content = MainView.build_menu_message(keyboard=keyboard)
    await message.answer(**content)


@router.callback_query(MainCallback.filter(F.section == "close"))
@require_message
async def close_main_menu(
    callback_query: CallbackQuery,
    message: Message,
) -> None:
    """Close the current main menu message."""
    try:
        await message.delete()
    except TelegramBadRequest:
        await message.edit_reply_markup(reply_markup=None)

    await callback_query.answer()
