from typing import Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonMentionRepository
from apps.scans.choices import ConfirmationLevel, PositionType
from apps.scans.repository import (
    PersonSnapshotRepository,
    ScanRepository,
    ScanSourceRepository,
)


@final
class CompanyScanDetailService(BaseService):
    """Load one company scan and a page of its person snapshots."""

    scan_repository = ScanRepository()
    person_snapshot_repository = PersonSnapshotRepository()
    scan_source_repository = ScanSourceRepository()
    person_mention_repository = PersonMentionRepository()

    @override
    async def execute(
        self,
        scan_id: UUID,
        offset: int,
        limit: int,
    ) -> dict[str, Any] | None:
        """Return the scan, position, a page of snapshots and aggregates."""
        (
            scan,
            scan_index,
            scans_total,
        ) = await self.scan_repository.get_with_position(
            scan_id=scan_id,
        )
        if scan is None:
            return None

        (
            person_snapshots,
            persons_total,
        ) = await self.person_snapshot_repository.list(
            filters={"scan_id": scan.id},
            select_related=("person",),
            order_by=(
                "person__normalized_name",
                "position_type",
                "confirmation_level",
            ),
            offset=offset,
            limit=limit,
        )
        partner_count = await self.person_snapshot_repository.count(
            filters={
                "scan_id": scan.id,
                "position_type": PositionType.PARTNER,
            },
        )
        director_count = await self.person_snapshot_repository.count(
            filters={
                "scan_id": scan.id,
                "position_type": PositionType.DIRECTOR,
            },
        )
        confirmed_count = await self.person_snapshot_repository.count(
            filters={
                "scan_id": scan.id,
                "confirmation_level": ConfirmationLevel.CONFIRMED,
            },
        )
        total_sources_count = await self.scan_source_repository.count(
            filters={"scan_id": scan.id},
        )
        mentions_by_person = (
            await self.person_mention_repository.list_by_persons_for_scan(
                scan_id=scan.id,
                person_ids=[
                    snapshot.person_id for snapshot in person_snapshots
                ],
            )
        )
        return {
            "scan": scan,
            "scan_index": scan_index,
            "scans_total": scans_total,
            "person_snapshots": person_snapshots,
            "persons_total": persons_total,
            "mentions_by_person": mentions_by_person,
            "partner_count": partner_count,
            "director_count": director_count,
            "confirmed_count": confirmed_count,
            "total_sources_count": total_sources_count,
        }
