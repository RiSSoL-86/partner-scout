from typing import Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository, PersonRepository
from apps.scans.repository import PersonSnapshotRepository


@final
class PersonDetailService(BaseService):
    """Load one person and a page of the scans they appeared in."""

    person_repository = PersonRepository()
    person_snapshot_repository = PersonSnapshotRepository()
    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
        offset: int,
        limit: int,
    ) -> dict[str, Any] | None:
        """Return the person, a page of their scans and per-scan mentions."""
        person = await self.person_repository.get(person_id)
        if person is None:
            return None

        snapshots, scans_total = await self.person_snapshot_repository.list(
            filters={"person_id": person_id},
            select_related=("scan", "scan__company"),
            order_by=("-scan__created_timestamp",),
            offset=offset,
            limit=limit,
        )
        mentions_by_scan = (
            await self.person_mention_repository.list_by_scans_for_person(
                person_id=person_id,
                scan_ids=[snapshot.scan_id for snapshot in snapshots],
            )
        )
        return {
            "person": person,
            "snapshots": snapshots,
            "scans_total": scans_total,
            "mentions_by_scan": mentions_by_scan,
        }
