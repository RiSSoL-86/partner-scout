import logging
from typing import TYPE_CHECKING, Any, final, override

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Chat, TelegramObject, User

logger = logging.getLogger(__name__)


@final
class AccessControlMiddleware(BaseMiddleware):
    """Drop updates from chats and users outside the allowlist."""

    def __init__(
        self,
        allowed_user_ids: frozenset[int],
        allowed_chat_ids: frozenset[int],
    ) -> None:
        self._allowed_user_ids = allowed_user_ids
        self._allowed_chat_ids = allowed_chat_ids

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat | None = data.get("event_chat")
        user: User | None = data.get("event_from_user")
        if self._is_allowed(chat, user):
            return await handler(event, data)

        logger.warning(
            msg=f"Blocked Telegram update: "
            f"chat_id={None if chat is None else chat.id} "
            f"chat_type={None if chat is None else chat.type} "
            f"user_id={None if user is None else user.id}"
        )
        return None

    def _is_allowed(self, chat: Chat | None, user: User | None) -> bool:
        if not self._allowed_user_ids and not self._allowed_chat_ids:
            return True
        if chat is not None and chat.id in self._allowed_chat_ids:
            return True
        return (
            chat is not None
            and chat.type == "private"
            and user is not None
            and user.id in self._allowed_user_ids
        )
