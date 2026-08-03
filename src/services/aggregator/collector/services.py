import logging
from typing import final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository
from services.aggregator.schemas import ScanPersonMentions

logger = logging.getLogger(__name__)


@final
class CollectorPersonMentionService(BaseService):
    """Load a scan's people and their mentions, grouped per person."""

    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(self, scan_id: UUID) -> ScanPersonMentions:
        """Return the scan's people keyed by id with their mentions."""
        repository = self.person_mention_repository
        mentions_by_person = await repository.list_grouped_by_person_for_scan(
            scan_id=scan_id
        )
        if not mentions_by_person:
            return ScanPersonMentions(person_by_id={}, mentions_by_person={})

        return ScanPersonMentions(
            person_by_id={
                mentions[0].person_id: mentions[0].person
                for mentions in mentions_by_person.values()
            },
            mentions_by_person=mentions_by_person,
        )
