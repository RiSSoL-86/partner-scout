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
        """Return a scan by id with its position among its company scans.

        Scans are ordered newest first, so the index counts how many newer
        scans the same company has. Returns ``(None, 0, 0)`` when the scan
        does not exist.
        """
        scan = (
            await self.model.objects.select_related("company")
            .filter(id=scan_id)
            .afirst()
        )
        if scan is None:
            return None, 0, 0

        company_scans = self.model.objects.filter(company_id=scan.company_id)
        total = await company_scans.acount()
        scan_index = await company_scans.filter(
            created_timestamp__gt=scan.created_timestamp,
        ).acount()

        return scan, scan_index, total

    async def get_by_position(
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

    async def list_by_scan_id(
        self,
        scan_id: UUID,
    ) -> list[PersonSnapshot]:
        """Return every person snapshot for a scan with related records."""
        ordered = (
            self.model.objects.filter(scan_id=scan_id)
            .select_related("person", "source")
            .order_by("confirmation_level", "person__normalized_name")
        )
        return [snapshot async for snapshot in ordered]
