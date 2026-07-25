from unittest.mock import AsyncMock

import pytest
from aiogram.types import CallbackQuery, Message


@pytest.fixture
def message() -> AsyncMock:
    """Return an accessible ``Message`` mock for callback handlers.

    aiogram shortcut methods are not ``async def``, so ``AsyncMock``'s spec
    detection leaves them synchronous; the awaited ones are set explicitly.
    """
    mock = AsyncMock(spec=Message)
    mock.edit_text = AsyncMock()
    mock.answer = AsyncMock()
    mock.delete = AsyncMock()
    mock.edit_reply_markup = AsyncMock()
    return mock


@pytest.fixture
def callback_query(message: AsyncMock) -> AsyncMock:
    """Return a ``CallbackQuery`` mock carrying an accessible message."""
    query = AsyncMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    query.message = message
    return query
