from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.scans.repository import PersonSnapshotRepository, ScanRepository

if TYPE_CHECKING:
    from apps.scans.models import PersonSnapshot, Scan


@final
class CompanyScanDetailService(BaseService):
    """Load one company scan and its person snapshots by scan id."""

    scan_repository = ScanRepository()
    person_snapshot_repository = PersonSnapshotRepository()

    @override
    async def execute(
        self,
        scan_id: UUID,
    ) -> tuple[Scan, int, int, list[PersonSnapshot]] | None:
        """Return the scan, its position, scans total and its snapshots."""
        (
            scan,
            scan_index,
            scans_total,
        ) = await self.scan_repository.get_with_position(
            scan_id=scan_id,
        )
        if scan is None:
            return None

        person_snapshots = (
            await self.person_snapshot_repository.list_by_scan_id(
                scan_id=scan.id,
            )
        )
        return scan, scan_index, scans_total, person_snapshots
