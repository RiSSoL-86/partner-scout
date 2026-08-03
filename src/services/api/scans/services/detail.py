from typing import Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository
from apps.scans.repository import (
    PersonSnapshotRepository,
    ScanRepository,
    ScanSourceRepository,
)


@final
class ScanDetailService(BaseService):
    """Load one scan and its person snapshots by scan id."""

    scan_repository = ScanRepository()
    person_snapshot_repository = PersonSnapshotRepository()
    scan_source_repository = ScanSourceRepository()
    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        scan_id: UUID,
    ) -> dict[str, Any] | None:
        """Return scan, position, total, snapshots, sources and counts."""
        (
            scan,
            scan_index,
            scans_total,
        ) = await self.scan_repository.get_with_position(scan_id=scan_id)
        if scan is None:
            return None

        person_snapshots = await self.person_snapshot_repository.list_all(
            filters={"scan_id": scan.id},
            select_related=("person",),
            order_by=(
                "person__normalized_name",
                "position_type",
                "confirmation_level",
            ),
        )
        total_sources_count = await self.scan_source_repository.count(
            filters={"scan_id": scan.id},
        )
        person_mention_counts = (
            await self.person_mention_repository.count_by_person_for_scan(
                scan_id=scan.id,
            )
        )
        return {
            "scan": scan,
            "scan_index": scan_index,
            "scans_total": scans_total,
            "person_snapshots": person_snapshots,
            "total_sources_count": total_sources_count,
            "person_mention_counts": person_mention_counts,
        }
