from typing import TYPE_CHECKING, final
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.common.repository import BaseRepository
from apps.scans.choices import AggregationStatus
from apps.scans.models import PersonSnapshot, Scan, ScanSource

if TYPE_CHECKING:
    from collections.abc import Sequence

    from apps.scans.choices import ScanStatus


@final
class ScanRepository(BaseRepository[Scan, UUID]):
    """Persistence operations for scans."""

    model = Scan

    @staticmethod
    async def set_scan_status(
        scan: Scan,
        scan_status: ScanStatus,
        scan_report: str = "",
        scan_error: str = "",
    ) -> Scan:
        """Persist a scan status change with any report or error text."""
        scan.scan_status = scan_status
        scan.scan_report = scan_report
        scan.scan_error = scan_error
        await scan.asave(
            update_fields=(
                "scan_status",
                "scan_report",
                "scan_error",
                "updated_timestamp",
            ),
        )
        return scan

    @staticmethod
    async def set_aggregation_status(
        scan: Scan,
        aggregation_status: AggregationStatus,
        aggregation_report: str = "",
        aggregation_error: str = "",
    ) -> Scan:
        """Persist an aggregation status change with error or report text."""
        scan.aggregation_status = aggregation_status
        scan.aggregation_report = aggregation_report
        scan.aggregation_error = aggregation_error
        await scan.asave(
            update_fields=(
                "aggregation_status",
                "aggregation_report",
                "aggregation_error",
                "updated_timestamp",
            ),
        )
        return scan

    async def claim_for_aggregation(self, scan_id: UUID) -> bool:
        """Atomically move a pending scan to running; True when claimed."""
        claimed = await self.model.objects.filter(
            id=scan_id,
            aggregation_status=AggregationStatus.PENDING,
        ).aupdate(
            aggregation_status=AggregationStatus.RUNNING,
            updated_timestamp=timezone.now(),
        )
        return claimed == 1

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

    async def replace_for_scan(
        self,
        scan_id: UUID,
        person_snapshots: Sequence[PersonSnapshot],
    ) -> int:
        """Atomically swap a scan's snapshots for a freshly aggregated set."""
        snapshots = list(person_snapshots)

        @transaction.atomic
        def swap() -> int:
            self.model.objects.filter(scan_id=scan_id).delete()
            if not snapshots:
                return 0
            return len(self.model.objects.bulk_create(objs=snapshots))

        return await sync_to_async(swap)()
