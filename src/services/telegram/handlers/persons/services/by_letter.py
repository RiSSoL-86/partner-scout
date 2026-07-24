from typing import TYPE_CHECKING, final, override

from apps.persons.repository import PersonRepository
from services.telegram.handlers.common.services.base import BaseTelegramService

if TYPE_CHECKING:
    from apps.persons.models import Person


@final
class PersonByLetterListTelegramService(BaseTelegramService):
    """Load a page of persons by surname initial for Telegram handlers."""

    person_repository = PersonRepository()

    @override
    async def execute(
        self,
        letter: str,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Person], int]:
        """Return a page of persons by surname initial and their total."""
        return await self.person_repository.list_by_surname_initial(
            initial=letter,
            offset=offset,
            limit=limit,
        )
