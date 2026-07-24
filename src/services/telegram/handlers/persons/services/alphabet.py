from typing import final, override

from apps.persons.repository import PersonRepository
from services.telegram.handlers.common.services.base import BaseTelegramService


@final
class PersonAlphabetTelegramService(BaseTelegramService):
    """Load surname initials with counts for Telegram handlers."""

    person_repository = PersonRepository()

    @override
    async def execute(self) -> list[tuple[str, int]]:
        """Return surname initials with their person counts."""
        return await self.person_repository.list_surname_initials()
