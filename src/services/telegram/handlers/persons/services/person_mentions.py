from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository, PersonRepository

if TYPE_CHECKING:
    from apps.persons.models import Person


@final
class PersonMentionsService(BaseService):
    """Load a person and their mentions count for Telegram handlers."""

    person_repository = PersonRepository()
    mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
    ) -> tuple[Person | None, int]:
        """Return the person and how many mentions they have."""
        person = await self.person_repository.get(person_id)
        if person is None:
            return None, 0

        total = await self.mention_repository.count_by_person_id(
            person_id=person_id,
        )
        return person, total
