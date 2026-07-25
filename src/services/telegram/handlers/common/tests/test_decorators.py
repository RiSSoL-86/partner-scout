from typing import Any
from unittest.mock import AsyncMock

from aiogram.types import CallbackQuery, Message

from services.telegram.handlers.common.decorators import require_message


async def test_require_message_injects_accessible_message() -> None:
    """Pass the accessible message and extra kwargs to the handler."""
    seen: dict[str, Any] = {}

    @require_message
    async def handler(
        callback_query: CallbackQuery,
        message: Message,
        **kwargs: Any,
    ) -> str:
        seen.update(query=callback_query, message=message, kwargs=kwargs)
        return "handled"

    message = AsyncMock(spec=Message)
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    query.message = message

    result = await handler(query, extra=1)

    assert result == "handled"
    assert seen == {"query": query, "message": message, "kwargs": {"extra": 1}}
    query.answer.assert_not_awaited()


async def test_require_message_skips_inaccessible_message() -> None:
    """Answer and skip the handler when the message is inaccessible."""

    @require_message
    async def handler(
        callback_query: CallbackQuery,
        message: Message,
        **kwargs: Any,
    ) -> str:
        raise AssertionError("handler must not run")

    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    query.message = None

    result = await handler(query)

    assert result is None
    query.answer.assert_awaited_once_with()
