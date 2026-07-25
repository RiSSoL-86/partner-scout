from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from services.telegram.handlers.common.messaging import safe_edit_text


async def test_safe_edit_text_forwards_kwargs() -> None:
    """Edit the message text with the provided kwargs."""
    message = AsyncMock(spec=Message)
    message.edit_text = AsyncMock()

    await safe_edit_text(message, text="hello", reply_markup=None)

    message.edit_text.assert_awaited_once_with(text="hello", reply_markup=None)


async def test_safe_edit_text_swallows_not_modified() -> None:
    """Ignore Telegram's "message is not modified" bad request."""
    message = AsyncMock(spec=Message)
    message.edit_text = AsyncMock(
        side_effect=TelegramBadRequest(
            method=object(),
            message="message is not modified",
        ),
    )

    await safe_edit_text(message, text="hello")


async def test_safe_edit_text_reraises_other_bad_requests() -> None:
    """Re-raise any bad request other than "not modified"."""
    message = AsyncMock(spec=Message)
    message.edit_text = AsyncMock()
    message.edit_text.side_effect = TelegramBadRequest(
        method=object(),
        message="message to edit not found",
    )

    with pytest.raises(TelegramBadRequest):
        await safe_edit_text(message, text="hello")
