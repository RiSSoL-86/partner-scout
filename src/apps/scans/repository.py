from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.scans.models import PersonSnapshot, Scan, ScanSource


@final
class ScanRepository(BaseRepository[Scan, UUID]):
    """Persistence operations for scans."""

    model = Scan

    async def get_company_scan_by_position(
        self,
        company_id: UUID,
        scan_index: int,
    ) -> tuple[Scan | None, int, int]:
        """Return a company scan by position, its index and scans total.

        Scans are ordered newest first, so index ``0`` is the latest scan.
        The requested index is clamped into the available range.
        """
        queryset = self.model.objects.filter(company_id=company_id)
        total = await queryset.acount()
        if total == 0:
            return None, 0, 0

        scan_index = min(max(scan_index, 0), total - 1)
        ordered = queryset.select_related("company").order_by(
            "-created_timestamp",
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

    async def list_for_scan(
        self,
        scan_id: UUID,
        offset: int = 0,
        limit: int = 5,
    ) -> tuple[list[PersonSnapshot], int]:
        """Return a page of person snapshots for a scan and their total."""
        queryset = self.model.objects.filter(scan_id=scan_id)
        total = await queryset.acount()
        ordered = queryset.select_related("person", "source").order_by(
            "created_timestamp",
        )
        page = [
            snapshot async for snapshot in ordered[offset : offset + limit]
        ]
        return page, total
