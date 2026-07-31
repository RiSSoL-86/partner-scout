from typing import TYPE_CHECKING, Any

from aiogram.exceptions import TelegramBadRequest

if TYPE_CHECKING:
    from aiogram.types import Message


async def safe_edit_text(message: Message, **kwargs: Any) -> None:
    """Edit message text, ignoring Telegram's "not modified" error."""
    try:
        await message.edit_text(**kwargs)
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise
