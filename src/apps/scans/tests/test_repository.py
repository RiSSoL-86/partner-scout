from datetime import timedelta
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.companies.tests.factories import CompanyFactory
from apps.persons.tests.factories import PersonFactory
from apps.scans.choices import (
    AggregationStatus,
    ConfirmationLevel,
    PositionType,
    ScanStatus,
)
from apps.scans.models import PersonSnapshot
from apps.scans.repository import PersonSnapshotRepository, ScanRepository
from apps.scans.tests.factories import PersonSnapshotFactory, ScanFactory

pytestmark = pytest.mark.django_db(transaction=True)

create_company = sync_to_async(CompanyFactory)
create_scan = sync_to_async(ScanFactory)
create_snapshot = sync_to_async(PersonSnapshotFactory)
create_person = sync_to_async(PersonFactory)


async def test_get_with_position_counts_newer_sibling_scans() -> None:
    """Return the scan with its index among newer company scans."""
    company = await create_company()
    now = timezone.now()
    await create_scan(company=company, created_timestamp=now)
    middle = await create_scan(
        company=company,
        created_timestamp=now - timedelta(hours=1),
    )
    await create_scan(
        company=company,
        created_timestamp=now - timedelta(hours=2),
    )

    scan, index, total = await ScanRepository().get_with_position(middle.id)

    assert scan is not None
    assert scan.id == middle.id
    assert index == 1
    assert total == 3


async def test_get_with_position_returns_empty_for_unknown_scan() -> None:
    """Return the empty tuple when the scan does not exist."""
    result = await ScanRepository().get_with_position(uuid4())

    assert result == (None, 0, 0)


async def test_get_by_position_returns_newest_scan_at_index_zero() -> None:
    """Return the newest scan for position zero with the company total."""
    company = await create_company()
    now = timezone.now()
    newest = await create_scan(company=company, created_timestamp=now)
    await create_scan(
        company=company,
        created_timestamp=now - timedelta(hours=1),
    )

    scan, index, total = await ScanRepository().get_by_position(
        company_id=company.id,
        scan_index=0,
    )

    assert scan is not None
    assert scan.id == newest.id
    assert index == 0
    assert total == 2


async def test_get_by_position_clamps_index_into_range() -> None:
    """Clamp an out-of-range position to the oldest available scan."""
    company = await create_company()
    now = timezone.now()
    await create_scan(company=company, created_timestamp=now)
    oldest = await create_scan(
        company=company,
        created_timestamp=now - timedelta(hours=1),
    )

    scan, index, total = await ScanRepository().get_by_position(
        company_id=company.id,
        scan_index=5,
    )

    assert scan is not None
    assert scan.id == oldest.id
    assert index == 1
    assert total == 2


async def test_get_by_position_returns_empty_without_scans() -> None:
    """Return the empty tuple when the company has no scans."""
    company = await create_company()

    result = await ScanRepository().get_by_position(
        company_id=company.id,
        scan_index=0,
    )

    assert result == (None, 0, 0)


async def test_list_by_scan_id_orders_by_confirmation_then_name() -> None:
    """Order snapshots by confirmation level then normalized name."""
    scan = await create_scan()
    low = await create_snapshot(
        scan=scan,
        person=await create_person(last_name="Zorin"),
        confirmation_level=ConfirmationLevel.UNLIKELY,
    )
    confirmed = await create_snapshot(
        scan=scan,
        person=await create_person(last_name="Adams"),
        confirmation_level=ConfirmationLevel.CONFIRMED,
    )

    snapshots = await PersonSnapshotRepository().list_all(
        filters={"scan_id": scan.id},
        select_related=("person",),
        order_by=("confirmation_level", "person__normalized_name"),
    )

    assert [snapshot.id for snapshot in snapshots] == [confirmed.id, low.id]


async def test_set_scan_status_persists_report_and_error() -> None:
    """Persist a scan status change together with its report text."""
    scan = await create_scan(scan_status=ScanStatus.RUNNING)

    await ScanRepository().set_scan_status(
        scan=scan,
        scan_status=ScanStatus.COMPLETED,
        scan_report="Mentions of persons: 3.",
    )

    reloaded = await ScanRepository().get(scan.id)
    assert reloaded is not None
    assert reloaded.scan_status == ScanStatus.COMPLETED
    assert reloaded.scan_report == "Mentions of persons: 3."


async def test_set_aggregation_status_persists_report() -> None:
    """Persist an aggregation status change with its report text."""
    scan = await create_scan(aggregation_status=AggregationStatus.RUNNING)

    await ScanRepository().set_aggregation_status(
        scan=scan,
        aggregation_status=AggregationStatus.COMPLETED,
        aggregation_report="Snapshots of person created: 2.",
    )

    reloaded = await ScanRepository().get(scan.id)
    assert reloaded is not None
    assert reloaded.aggregation_status == AggregationStatus.COMPLETED
    assert reloaded.aggregation_report == "Snapshots of person created: 2."


async def test_claim_for_aggregation_claims_a_pending_scan() -> None:
    """Move a pending scan to running and report the claim succeeded."""
    scan = await create_scan(aggregation_status=AggregationStatus.PENDING)

    claimed = await ScanRepository().claim_for_aggregation(scan_id=scan.id)

    assert claimed is True
    reloaded = await ScanRepository().get(scan.id)
    assert reloaded is not None
    assert reloaded.aggregation_status == AggregationStatus.RUNNING


async def test_claim_for_aggregation_rejects_a_claimed_scan() -> None:
    """Refuse to re-claim a scan that is no longer pending."""
    scan = await create_scan(aggregation_status=AggregationStatus.RUNNING)

    claimed = await ScanRepository().claim_for_aggregation(scan_id=scan.id)

    assert claimed is False


async def test_increment_pages_scanned_bumps_the_counter() -> None:
    """Add one to the running scan's scanned-pages counter."""
    scan = await create_scan(pages_scanned=4)

    await ScanRepository().increment_pages_scanned(scan=scan)

    reloaded = await ScanRepository().get(scan.id)
    assert reloaded is not None
    assert reloaded.pages_scanned == 5


async def test_replace_for_scan_swaps_the_scans_snapshots() -> None:
    """Drop a scan's old snapshots and store the freshly built set."""
    scan = await create_scan()
    await create_snapshot(scan=scan)
    repository = PersonSnapshotRepository()

    person = await create_person()
    written = await repository.replace_for_scan(
        scan_id=scan.id,
        person_snapshots=[
            PersonSnapshot(
                scan=scan,
                person=person,
                position_type=PositionType.PARTNER,
                confirmation_level=ConfirmationLevel.CONFIRMED,
            )
        ],
    )

    assert written == 1
    remaining = await repository.list_all(filters={"scan_id": scan.id})
    assert [snapshot.person_id for snapshot in remaining] == [person.id]


async def test_replace_for_scan_clears_snapshots_when_empty() -> None:
    """Remove a scan's snapshots when replaced with an empty set."""
    scan = await create_scan()
    await create_snapshot(scan=scan)
    repository = PersonSnapshotRepository()

    written = await repository.replace_for_scan(
        scan_id=scan.id, person_snapshots=[]
    )

    assert written == 0
    assert await repository.count(filters={"scan_id": scan.id}) == 0
