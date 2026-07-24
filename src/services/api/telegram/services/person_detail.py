from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.persons.repository import PersonRepository
from services.api.common.services.base import BaseService

if TYPE_CHECKING:
    from apps.persons.models import Person


@final
class TelegramPersonDetailService(BaseService):
    """Load one person for the Telegram report page."""

    person_repository = PersonRepository()

    @override
    async def execute(self, person_id: UUID) -> Person | None:
        """Return one person by id."""
        return await self.person_repository.get(person_id)
