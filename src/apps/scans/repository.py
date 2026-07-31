from typing import TYPE_CHECKING, final
from uuid import UUID

from django.db.models import F

from apps.common.repository import BaseRepository
from apps.scans.models import PersonSnapshot, Scan, ScanSource

if TYPE_CHECKING:
    from apps.scans.choices import ScanStatus


@final
class ScanRepository(BaseRepository[Scan, UUID]):
    """Persistence operations for scans."""

    model = Scan

    @staticmethod
    async def set_status(
        scan: Scan,
        status: ScanStatus,
        error: str = "",
    ) -> Scan:
        """Persist a scan status change and any accompanying error text."""
        scan.status = status
        scan.error = error
        await scan.asave(
            update_fields=("status", "error", "updated_timestamp"),
        )
        return scan

    @staticmethod
    async def increment_pages_scanned(scan: Scan) -> Scan:
        """Persist one more counted page for the running scan."""
        scan.pages_scanned = F("pages_scanned") + 1
        await scan.asave(
            update_fields=("pages_scanned", "updated_timestamp"),
        )
        return scan

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
