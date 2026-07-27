from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.scans.models import PersonSnapshot, Scan, ScanSource


@final
class ScanRepository(BaseRepository[Scan, UUID]):
    """Persistence operations for scans."""

    model = Scan

    async def get_with_position(
        self,
        scan_id: UUID,
    ) -> tuple[Scan | None, int, int]:
        """Return a scan with its index among newer company scans."""
        scan = await self.find_one(
            filters={"id": scan_id},
            select_related=("company",),
        )
        if scan is None:
            return None, 0, 0

        total = await self.count(filters={"company_id": scan.company_id})
        scan_index = await self.count(
            filters={
                "company_id": scan.company_id,
                "created_timestamp__gt": scan.created_timestamp,
            },
        )
        return scan, scan_index, total

    async def get_by_position(
        self,
        company_id: UUID,
        scan_index: int,
    ) -> tuple[Scan | None, int, int]:
        """Return a company scan by clamped index, plus index and total."""
        total = await self.count(filters={"company_id": company_id})
        if total == 0:
            return None, 0, 0

        scan_index = min(max(scan_index, 0), total - 1)
        ordered = self.get_queryset(
            filters={"company_id": company_id},
            select_related=("company",),
            order_by=("-created_timestamp",),
        )

        scan: Scan | None = None
        async for instance in ordered[scan_index : scan_index + 1]:
            scan = instance

        return scan, scan_index, total


@final
class ScanSourceRepository(BaseRepository[ScanSource, UUID]):
    """Persistence operations for scan-source links."""

    model = ScanSource


@final
class PersonSnapshotRepository(BaseRepository[PersonSnapshot, UUID]):
    """Persistence operations for person snapshots."""

    model = PersonSnapshot
