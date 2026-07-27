from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.urls import reverse

from apps.persons.tests.factories import PersonFactory
from apps.scans.choices import PositionType, ScanStatus
from apps.scans.tests.factories import PersonSnapshotFactory, ScanFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


def scan_detail_url(scan_id: object) -> str:
    """Return the scan detail url for a scan id."""
    return reverse("api:scans:scan_detail", kwargs={"scan_id": scan_id})


def scan_choices_url() -> str:
    """Return the scan choices url."""
    return reverse("api:scans:scan_choices")


def test_scan_choices_expose_scan_and_snapshot(client: Client) -> None:
    """Expose scan and snapshot choices with value and label."""
    response = client.get(scan_choices_url())

    assert response.status_code == 200
    body = response.json()
    statuses = body["scan"]["status"]
    assert {option["value"] for option in statuses} == set(ScanStatus.values)
    positions = body["personSnapshot"]["positionType"]
    assert {option["value"] for option in positions} == set(
        PositionType.values
    )
    partner = next(
        option
        for option in positions
        if option["value"] == PositionType.PARTNER
    )
    assert partner["label"] == "partner"


def test_scan_detail_returns_scan_with_snapshots(client: Client) -> None:
    """Return the scan detail with its person snapshots."""
    scan = ScanFactory()
    person = PersonFactory(first_name="Ivan", last_name="Ivanov")
    PersonSnapshotFactory(scan=scan, person=person)

    response = client.get(scan_detail_url(scan.id))

    assert response.status_code == 200
    body = response.json()
    assert body["scan"]["id"] == str(scan.id)
    assert body["company"]["id"] == str(scan.company_id)
    assert body["scansTotal"] == 1
    assert len(body["personSnapshots"]) == 1
    assert body["personSnapshots"][0]["personId"] == str(person.id)
    assert body["personSnapshots"][0]["fullName"] == person.normalized_name


def test_scan_detail_returns_not_found(client: Client) -> None:
    """Return 404 for an unknown scan."""
    response = client.get(scan_detail_url(uuid4()))

    assert response.status_code == 404
