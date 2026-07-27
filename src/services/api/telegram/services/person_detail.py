from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository, PersonRepository

if TYPE_CHECKING:
    from apps.persons.models import Person, PersonMention


@final
class PersonDetailService(BaseService):
    """Load one person and their mentions for the Telegram report page."""

    person_repository = PersonRepository()
    mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
    ) -> tuple[Person, list[PersonMention]] | None:
        """Return the person and their mentions, or None when missing."""
        person = await self.person_repository.get(person_id)
        if person is None:
            return None

        mentions = await self.mention_repository.list_all(
            filters={"person_id": person_id},
            select_related=("source",),
            order_by=("-created_timestamp",),
        )
        return person, mentions
