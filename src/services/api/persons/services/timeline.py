from typing import TYPE_CHECKING, Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository, PersonRepository
from apps.scans.repository import PersonSnapshotRepository

if TYPE_CHECKING:
    from apps.scans.models import PersonSnapshot

type TimelineEntry = tuple["PersonSnapshot", int]


@final
class PersonTimelineService(BaseService):
    """Load a page of a person's snapshots with their mention counts."""

    person_repository = PersonRepository()
    person_snapshot_repository = PersonSnapshotRepository()
    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> dict[str, Any] | None:
        """Return the person, a page of timeline entries and total, or None."""
        person = await self.person_repository.get(person_id)
        if person is None:
            return None

        snapshots, total = await self.person_snapshot_repository.list(
            filters={"person_id": person_id},
            select_related=("scan", "scan__company"),
            order_by=("-scan__created_timestamp",),
            offset=offset,
            limit=limit,
        )

        mention_counts = (
            await self.person_mention_repository.count_by_scan_for_person(
                person_id=person_id,
                scan_ids=[snapshot.scan_id for snapshot in snapshots],
            )
        )
        entries: list[TimelineEntry] = [
            (snapshot, mention_counts.get(snapshot.scan_id, 0))
            for snapshot in snapshots
        ]
        return {
            "person": person,
            "entries": entries,
            "total": total,
        }
