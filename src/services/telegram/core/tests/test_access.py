from types import SimpleNamespace
from typing import Any

import pytest

from services.telegram.core.access import AccessControlMiddleware

ALLOWED_USER = 111
ALLOWED_CHAT = -5403010879


def _chat(chat_id: int, chat_type: str) -> SimpleNamespace:
    return SimpleNamespace(id=chat_id, type=chat_type)


def _user(user_id: int) -> SimpleNamespace:
    return SimpleNamespace(id=user_id)


async def _run(
    middleware: AccessControlMiddleware,
    chat: SimpleNamespace | None,
    user: SimpleNamespace | None,
) -> bool:
    """Run the middleware and report whether the handler was reached."""
    reached = False

    async def handler(event: Any, data: dict[str, Any]) -> str:
        nonlocal reached
        reached = True
        return "ok"

    data: dict[str, Any] = {"event_chat": chat, "event_from_user": user}
    await middleware(handler, SimpleNamespace(), data)
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
    chat = _chat(ALLOWED_USER, "private")
    assert await _run(middleware, chat, _user(ALLOWED_USER)) is True


async def test_blocks_other_user_in_private_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Drop private updates from anyone but the allowed user."""
    chat = _chat(999, "private")
    assert await _run(middleware, chat, _user(999)) is False


async def test_allows_listed_group_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Reach the handler for any member of the allowed group chat."""
    chat = _chat(ALLOWED_CHAT, "supergroup")
    assert await _run(middleware, chat, _user(999)) is True


async def test_blocks_other_group_chat(
    middleware: AccessControlMiddleware,
) -> None:
    """Drop updates from group chats outside the allowlist."""
    chat = _chat(-1, "supergroup")
    assert await _run(middleware, chat, _user(ALLOWED_USER)) is False


async def test_allowed_user_cannot_bypass_via_foreign_group(
    middleware: AccessControlMiddleware,
) -> None:
    """The private allowlist must not open unlisted group chats."""
    chat = _chat(-1, "supergroup")
    assert await _run(middleware, chat, _user(ALLOWED_USER)) is False


async def test_open_when_no_allowlists_configured() -> None:
    """Answer everyone when both allowlists are empty."""
    middleware = AccessControlMiddleware(
        allowed_user_ids=frozenset(),
        allowed_chat_ids=frozenset(),
    )
    chat = _chat(999, "private")
    assert await _run(middleware, chat, _user(999)) is True
