from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.scans.repository import PersonSnapshotRepository, ScanRepository
from services.telegram.handlers.common.services.base import BaseTelegramService

if TYPE_CHECKING:
    from apps.scans.models import PersonSnapshot, Scan


@final
class PersonSnapshotListTelegramService(BaseTelegramService):
    """Load a page of person snapshots for a company scan by position."""

    scan_repository = ScanRepository()
    snapshot_repository = PersonSnapshotRepository()

    @override
    async def execute(
        self,
        company_id: UUID,
        scan_index: int = 0,
        offset: int = 0,
        limit: int = 5,
    ) -> tuple[Scan | None, int, list[PersonSnapshot], int]:
        """Return the scan, its index, a snapshots page and their total."""
        (
            scan,
            scan_index,
            _,
        ) = await self.scan_repository.get_company_scan_by_position(
            company_id=company_id,
            scan_index=scan_index,
        )
        if scan is None:
            return None, scan_index, [], 0

        (
            snapshots,
            snapshots_total,
        ) = await self.snapshot_repository.list_for_scan(
            scan_id=scan.id,
            offset=offset,
            limit=limit,
        )
        return scan, scan_index, snapshots, snapshots_total
