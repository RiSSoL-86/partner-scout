import logging
from typing import final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository, PersonRepository
from services.aggregator.schemas import ScanPersonMentions

logger = logging.getLogger(__name__)


@final
class CollectorPersonMentionService(BaseService):
    """Load a scan's people and their mentions, grouped per person."""

    person_repository = PersonRepository()
    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(self, scan_id: UUID) -> ScanPersonMentions:
        """Return the scan's people keyed by id with their mentions."""
        counts = await self.person_mention_repository.count_by_person_for_scan(
            scan_id=scan_id
        )
        mentions_by_person = (
            await self.person_mention_repository.list_by_persons_for_scan(
                scan_id=scan_id,
                person_ids=list(counts.keys()),
            )
        )
        if not mentions_by_person:
            return ScanPersonMentions(person_by_id={}, mentions_by_person={})

        persons = await self.person_repository.list_all(
            filters={"id__in": list(mentions_by_person.keys())},
        )
        return ScanPersonMentions(
            person_by_id={person.id: person for person in persons},
            mentions_by_person=mentions_by_person,
        )
