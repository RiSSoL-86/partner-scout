from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository
from apps.scans.repository import (
    PersonSnapshotRepository,
    ScanRepository,
    ScanSourceRepository,
)

if TYPE_CHECKING:
    from apps.scans.models import PersonSnapshot, Scan


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
    ) -> (
        tuple[Scan, int, int, list[PersonSnapshot], int, dict[UUID, int]]
        | None
    ):
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
            select_related=("person", "scan__company"),
            order_by=(
                "person__normalized_name",
                "position_type",
                "confirmation_level",
            ),
        )
        total_sources_count = await self.scan_source_repository.count(
            filters={"scan_id": scan.id},
        )
        mention_repository = self.person_mention_repository
        person_source_counts = (
            await mention_repository.count_sources_by_person_for_scan(
                scan_id=scan.id,
            )
        )
        return (
            scan,
            scan_index,
            scans_total,
            person_snapshots,
            total_sources_count,
            person_source_counts,
        )
