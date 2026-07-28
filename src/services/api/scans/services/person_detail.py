from typing import Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository
from apps.scans.repository import PersonSnapshotRepository


@final
class ScanPersonDetailService(BaseService):
    """Load a person's snapshot and source mentions within one scan."""

    person_snapshot_repository = PersonSnapshotRepository()
    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        scan_id: UUID,
        person_id: UUID,
    ) -> dict[str, Any] | None:
        """Return the person snapshot and its scan mentions, or None."""
        person_snapshot = await self.person_snapshot_repository.find_one(
            filters={"scan_id": scan_id, "person_id": person_id},
            select_related=("person", "scan__company"),
        )
        if person_snapshot is None:
            return None

        person_mentions = await self.person_mention_repository.list_all(
            filters={"scan_id": scan_id, "person_id": person_id},
            select_related=("source",),
            order_by=("mention_type", "source__title"),
        )
        return {
            "person_snapshot": person_snapshot,
            "person_mentions": person_mentions,
        }
