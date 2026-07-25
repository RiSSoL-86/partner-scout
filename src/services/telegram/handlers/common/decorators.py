import functools
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.types import CallbackQuery, Message

CallbackHandler = Callable[..., Awaitable[Any]]


def require_message(handler: CallbackHandler) -> CallbackHandler:
    """Guard a callback query handler and inject its accessible message.

    Answers and skips the handler when the attached message is missing or
    inaccessible, so handlers receive a concrete ``Message`` to work with.
    """

    @functools.wraps(handler)
    async def wrapper(callback_query: CallbackQuery, **kwargs: Any) -> Any:
        message = callback_query.message
        if not isinstance(message, Message):
            await callback_query.answer()
            return None
        return await handler(callback_query, message, **kwargs)

    return wrapper
