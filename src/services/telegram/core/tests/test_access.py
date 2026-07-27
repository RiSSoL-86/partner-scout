from typing import TYPE_CHECKING, Any

import pytest
from aiogram.types import Update

from services.telegram.core.access import AccessControlMiddleware
from services.telegram.core.tests.factories import ChatFactory, UserFactory

if TYPE_CHECKING:
    from aiogram.types import Chat, User

ALLOWED_USER = 111
ALLOWED_CHAT = -100


async def _run(
    middleware: AccessControlMiddleware,
    chat: Chat | None,
    user: User | None,
) -> bool:
    """Run the middleware and report whether the handler was reached."""
    reached = False

    async def handler(event: Any, data: dict[str, Any]) -> str:
        nonlocal reached
        reached = True
        return "ok"

    data: dict[str, Any] = {"event_chat": chat, "event_from_user": user}
    await middleware(handler, Update(update_id=1), data)
    return reached


@pytest.fixture
def middleware() -> AccessControlMiddleware:
    """Return a middleware locked to one user and one group chat."""
    return AccessControlMiddleware(
        allowed_user_ids=frozenset({ALLOWED_USER}),
        allowed_chat_ids=frozenset({ALLOWED_CHAT}),
    )


async def test_allows_own_private_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Reach the handler for the allowed user in a private chat."""
    chat = ChatFactory(id=ALLOWED_USER, type="private")
    user = UserFactory(id=ALLOWED_USER)
    assert await _run(middleware, chat, user) is True


async def test_blocks_other_user_in_private_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Drop private updates from anyone but the allowed user."""
    chat = ChatFactory(id=999, type="private")
    assert await _run(middleware, chat, UserFactory(id=999)) is False


async def test_allows_listed_group_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Reach the handler for any member of the allowed group chat."""
    chat = ChatFactory(id=ALLOWED_CHAT, type="supergroup")
    assert await _run(middleware, chat, UserFactory(id=999)) is True


async def test_blocks_other_group_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Drop updates from group chats outside the allowlist."""
    chat = ChatFactory(id=-1, type="supergroup")
    assert await _run(middleware, chat, UserFactory(id=ALLOWED_USER)) is False


async def test_allowed_user_cannot_bypass_via_foreign_group(
    middleware: AccessControlMiddleware,
) -> None:
    """The private allowlist must not open unlisted group chats."""
    chat = ChatFactory(id=-1, type="supergroup")
    assert await _run(middleware, chat, UserFactory(id=ALLOWED_USER)) is False


async def test_open_when_no_allowlists_configured() -> None:
    """Answer everyone when both allowlists are empty."""
    middleware = AccessControlMiddleware(
        allowed_user_ids=frozenset(),
        allowed_chat_ids=frozenset(),
    )
    chat = ChatFactory(id=999, type="private")
    assert await _run(middleware, chat, UserFactory(id=999)) is True
