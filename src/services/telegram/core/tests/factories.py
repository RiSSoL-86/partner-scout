import factory
from aiogram.types import Chat, User


class ChatFactory(factory.Factory[Chat]):
    """Build aiogram ``Chat`` objects with private-chat defaults."""

    class Meta:
        """Configure the generated aiogram object."""

        model = Chat

    id = factory.Sequence(lambda n: n + 1)
    type = "private"


class UserFactory(factory.Factory[User]):
    """Build aiogram ``User`` objects with valid defaults."""

    class Meta:
        """Configure the generated aiogram object."""

        model = User

    id = factory.Sequence(lambda n: n + 1)
    is_bot = False
    first_name = factory.Sequence(lambda n: f"User {n}")
