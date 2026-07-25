from unittest.mock import AsyncMock

from aiogram.exceptions import TelegramBadRequest

from services.telegram.handlers.main import routes


async def test_show_main_menu_answers_with_menu(message: AsyncMock) -> None:
    """Send the main menu in reply to the start command."""
    await routes.show_main_menu(message)

    message.answer.assert_awaited_once()
    assert "Partner Scout" in message.answer.await_args.kwargs["text"]


async def test_close_main_menu_deletes_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Delete the menu message and acknowledge the callback."""
    await routes.close_main_menu(callback_query)

    message.delete.assert_awaited_once()
    message.edit_reply_markup.assert_not_awaited()
    callback_query.answer.assert_awaited_once_with()


async def test_close_main_menu_strips_markup_when_delete_fails(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Fall back to removing the markup when the message cannot be deleted."""
    message.delete.side_effect = TelegramBadRequest(
        method=object(),
        message="message can't be deleted",
    )

    await routes.close_main_menu(callback_query)

    message.edit_reply_markup.assert_awaited_once_with(reply_markup=None)
    callback_query.answer.assert_awaited_once_with()
