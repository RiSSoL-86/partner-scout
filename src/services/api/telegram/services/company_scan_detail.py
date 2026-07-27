from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.scans.repository import (
    PersonSnapshotRepository,
    ScanRepository,
    ScanSourceRepository,
)

if TYPE_CHECKING:
    from apps.scans.models import PersonSnapshot, Scan


@final
class CompanyScanDetailService(BaseService):
    """Load one company scan and its person snapshots by scan id."""

    scan_repository = ScanRepository()
    person_snapshot_repository = PersonSnapshotRepository()
    scan_source_repository = ScanSourceRepository()

    @override
    async def execute(
        self,
        scan_id: UUID,
    ) -> tuple[Scan, int, int, list[PersonSnapshot], int] | None:
        """Return the scan, position, total, snapshots and sources count."""
        (
            scan,
            scan_index,
            scans_total,
        ) = await self.scan_repository.get_with_position(
            scan_id=scan_id,
        )
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
        sources_count = await self.scan_source_repository.count(
            filters={"scan_id": scan.id},
        )
        return scan, scan_index, scans_total, person_snapshots, sources_count
