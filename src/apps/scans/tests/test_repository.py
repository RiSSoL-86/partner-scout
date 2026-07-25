from datetime import timedelta
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.companies.tests.factories import CompanyFactory
from apps.persons.tests.factories import PersonFactory
from apps.scans.choices import ConfirmationLevel
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
        confirmation_level=ConfirmationLevel.LOW,
    )
    confirmed = await create_snapshot(
        scan=scan,
        person=await create_person(last_name="Adams"),
        confirmation_level=ConfirmationLevel.CONFIRMED,
    )

    snapshots = await PersonSnapshotRepository().list_by_scan_id(scan.id)

    assert [snapshot.id for snapshot in snapshots] == [confirmed.id, low.id]
