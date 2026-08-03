import logging
from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.scans.choices import AggregationStatus, ScanStatus
from apps.scans.repository import PersonSnapshotRepository, ScanRepository
from services.aggregator.builder.services import (
    BuilderPersonSnapshotService,
)
from services.aggregator.classifier.services import ClassifierPersonService
from services.aggregator.collector.services import (
    CollectorPersonMentionService,
)

if TYPE_CHECKING:
    from apps.scans.models import Scan

logger = logging.getLogger(__name__)


@final
class PlanAggregationService(BaseService):
    """List the completed scans still awaiting aggregation."""

    scan_repository = ScanRepository()

    @override
    async def execute(self) -> list[UUID]:
        """Return the ids of scans ready to be aggregated."""
        scans = await self.scan_repository.list_all(
            filters={
                "scan_status": ScanStatus.COMPLETED,
                "aggregation_status": AggregationStatus.PENDING,
            },
            order_by=("created_timestamp",),
        )
        logger.info(msg=f"Planned aggregation for {len(scans)} scan(s)")
        return [scan.id for scan in scans]


@final
class AggregatePersonsService(BaseService):
    """Drive one scan's aggregation flow, delegating each step to a service."""

    scan_repository = ScanRepository()
    person_snapshot_repository = PersonSnapshotRepository()
    collector_person_mention_service = CollectorPersonMentionService()
    classifier_person_service = ClassifierPersonService()
    builder_person_snapshot_service = BuilderPersonSnapshotService()

    @override
    async def execute(self, scan_id: UUID) -> Scan | None:
        """Aggregate one scan, returning it, or None when it is gone."""
        scan = await self.scan_repository.find_one(
            filters={"id": scan_id},
            select_related=("company",),
        )
        if scan is None:
            return None

        if scan.scan_status != ScanStatus.COMPLETED:
            logger.info(
                msg=f"Scan {scan_id} is not completed "
                f"({scan.scan_status=}); skipping aggregation"
            )
            return scan

        if not await self.scan_repository.claim_for_aggregation(
            scan_id=scan_id
        ):
            logger.info(
                msg=f"Scan {scan_id} already claimed for aggregation; skipping"
            )
            return scan

        logger.info(msg=f"Aggregating scan {scan_id} ({scan.company.name})")
        try:
            written = await self._aggregate(scan)
        except Exception as error:
            logger.exception(msg=f"Scan {scan_id} aggregation failed")
            await self.scan_repository.set_aggregation_status(
                scan=scan,
                aggregation_status=AggregationStatus.FAILED,
                aggregation_error=str(error),
            )
            return scan

        logger.info(
            msg=f"Scan {scan_id} aggregated: {written} snapshot(s) written"
        )
        await self.scan_repository.set_aggregation_status(
            scan=scan,
            aggregation_status=AggregationStatus.COMPLETED,
            aggregation_report=f"Snapshots of person created: {written}.",
        )
        return scan

    async def _aggregate(self, scan: Scan) -> int:
        """Collect, classify and persist the scan's people as snapshots."""
        scan_person_mentions = (
            await self.collector_person_mention_service.execute(
                scan_id=scan.id
            )
        )
        if not scan_person_mentions:
            return await self.person_snapshot_repository.replace_for_scan(
                scan_id=scan.id, person_snapshots=[]
            )

        classifications = await self.classifier_person_service.execute(
            company_name=scan.company.name,
            scan_person_mentions=scan_person_mentions,
        )
        person_snapshots = await self.builder_person_snapshot_service.execute(
            scan=scan,
            scan_person_mentions=scan_person_mentions,
            classifications=classifications,
        )
        return await self.person_snapshot_repository.replace_for_scan(
            scan_id=scan.id, person_snapshots=person_snapshots
        )
