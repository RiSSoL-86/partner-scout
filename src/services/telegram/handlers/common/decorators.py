import functools
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.types import CallbackQuery, Message

CallbackHandler = Callable[..., Awaitable[Any]]


def require_message(handler: CallbackHandler) -> CallbackHandler:
    """Guard a callback handler and inject its accessible message."""

    @functools.wraps(handler)
    async def wrapper(callback_query: CallbackQuery, **kwargs: Any) -> Any:
        message = callback_query.message
        if not isinstance(message, Message):
            await callback_query.answer()
            return None
        return await handler(callback_query, message, **kwargs)

    return wrapper
