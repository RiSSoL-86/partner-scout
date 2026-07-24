from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.persons.repository import PersonMentionRepository, PersonRepository
from services.telegram.handlers.common.services.base import BaseTelegramService

if TYPE_CHECKING:
    from apps.persons.models import Person, PersonMention


@final
class PersonMentionListTelegramService(BaseTelegramService):
    """Load a page of one person mentions for Telegram handlers."""

    person_repository = PersonRepository()
    mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
        offset: int = 0,
        limit: int = 5,
    ) -> tuple[Person | None, list[PersonMention], int]:
        """Return the person, a mentions page and their total."""
        person = await self.person_repository.get(person_id)
        if person is None:
            return None, [], 0

        mentions, total = await self.mention_repository.list_for_person(
            person_id=person_id,
            offset=offset,
            limit=limit,
        )
        return person, mentions, total
