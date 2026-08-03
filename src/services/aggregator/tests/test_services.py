from datetime import timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.choices import (
    AggregationStatus,
    ConfirmationLevel,
    PositionType,
    ScanStatus,
)
from apps.scans.models import PersonSnapshot
from apps.scans.repository import PersonSnapshotRepository, ScanRepository
from apps.scans.tests.factories import ScanFactory
from services.aggregator.schemas import ScanPersonMentions
from services.aggregator.services import (
    AggregatePersonsService,
    PlanAggregationService,
)

pytestmark = pytest.mark.django_db(transaction=True)

create_scan = sync_to_async(ScanFactory)
create_person = sync_to_async(PersonFactory)
create_mention = sync_to_async(PersonMentionFactory)


async def reload_scan(scan_id):
    """Re-read a scan from the database to observe persisted changes."""
    return await ScanRepository().find_one(filters={"id": scan_id})


# --- PlanAggregationService ------------------------------------------------


async def test_plan_lists_pending_completed_scans_oldest_first() -> None:
    """Return completed, aggregation-pending scan ids oldest first."""
    now = timezone.now()
    newer = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.PENDING,
        created_timestamp=now,
    )
    older = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.PENDING,
        created_timestamp=now - timedelta(hours=1),
    )

    scan_ids = await PlanAggregationService().execute()

    assert scan_ids == [older.id, newer.id]


async def test_plan_skips_running_and_already_aggregated_scans() -> None:
    """Exclude non-completed and already-aggregated scans from the plan."""
    await create_scan(
        scan_status=ScanStatus.RUNNING,
        aggregation_status=AggregationStatus.PENDING,
    )
    await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.COMPLETED,
    )
    eligible = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.PENDING,
    )

    scan_ids = await PlanAggregationService().execute()

    assert scan_ids == [eligible.id]


# --- AggregatePersonsService ----------------------------------------------


def build_service() -> AggregatePersonsService:
    """Build the service with its collaborating steps mocked out."""
    service = AggregatePersonsService()
    service.collector_person_mention_service = AsyncMock()  # type: ignore[misc]
    service.classifier_person_service = AsyncMock()  # type: ignore[misc]
    service.builder_person_snapshot_service = AsyncMock()  # type: ignore[misc]
    return service


async def test_aggregate_returns_none_for_a_missing_scan() -> None:
    """Return None when the scan no longer exists."""
    service = build_service()

    assert await service.execute(scan_id=uuid4()) is None


async def test_aggregate_skips_a_scan_that_is_not_completed() -> None:
    """Leave a not-completed scan untouched."""
    scan = await create_scan(scan_status=ScanStatus.RUNNING)
    service = build_service()

    result = await service.execute(scan_id=scan.id)

    assert result is not None
    service.collector_person_mention_service.execute.assert_not_awaited()
    reloaded = await reload_scan(scan.id)
    assert reloaded.aggregation_status == AggregationStatus.PENDING


async def test_aggregate_skips_an_already_claimed_scan() -> None:
    """Skip a scan another worker already claimed for aggregation."""
    scan = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.RUNNING,
    )
    service = build_service()

    await service.execute(scan_id=scan.id)

    service.collector_person_mention_service.execute.assert_not_awaited()


async def test_aggregate_writes_snapshots_and_marks_completed() -> None:
    """Run the full flow and persist the built snapshots for the scan."""
    scan = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.PENDING,
    )
    person = await create_person()
    mention = await create_mention(scan=scan, person=person)
    service = build_service()
    service.collector_person_mention_service.execute.return_value = (
        ScanPersonMentions(
            person_by_id={person.id: person},
            mentions_by_person={person.id: [mention]},
        )
    )
    service.classifier_person_service.execute.return_value = {}
    service.builder_person_snapshot_service.execute.return_value = [
        PersonSnapshot(
            scan=scan,
            person=person,
            position_type=PositionType.PARTNER,
            role_title="Partner",
            confirmation_level=ConfirmationLevel.CONFIRMED,
        )
    ]

    result = await service.execute(scan_id=scan.id)

    assert result is not None
    stored = await PersonSnapshotRepository().count(
        filters={"scan_id": scan.id}
    )
    assert stored == 1
    reloaded = await reload_scan(scan.id)
    assert reloaded.aggregation_status == AggregationStatus.COMPLETED
    assert "1" in reloaded.aggregation_report


async def test_aggregate_completes_with_zero_when_no_one_mentioned() -> None:
    """Short-circuit classification and report zero snapshots."""
    scan = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.PENDING,
    )
    service = build_service()
    service.collector_person_mention_service.execute.return_value = (
        ScanPersonMentions(person_by_id={}, mentions_by_person={})
    )

    await service.execute(scan_id=scan.id)

    service.classifier_person_service.execute.assert_not_awaited()
    service.builder_person_snapshot_service.execute.assert_not_awaited()
    reloaded = await reload_scan(scan.id)
    assert reloaded.aggregation_status == AggregationStatus.COMPLETED
    assert "0" in reloaded.aggregation_report


async def test_aggregate_marks_failed_when_a_step_raises() -> None:
    """Record the failure when an aggregation step raises."""
    scan = await create_scan(
        scan_status=ScanStatus.COMPLETED,
        aggregation_status=AggregationStatus.PENDING,
    )
    service = build_service()
    service.collector_person_mention_service.execute.side_effect = (
        RuntimeError("collector boom")
    )

    await service.execute(scan_id=scan.id)

    reloaded = await reload_scan(scan.id)
    assert reloaded.aggregation_status == AggregationStatus.FAILED
    assert "collector boom" in reloaded.aggregation_error
