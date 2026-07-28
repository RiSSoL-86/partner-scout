from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.urls import reverse

from apps.persons.choices import MentionType
from apps.persons.tests.factories import (
    PersonFactory,
    PersonMentionFactory,
)
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


def scan_person_detail_url(scan_id: object, person_id: object) -> str:
    """Return the scan person detail url for a scan and person id."""
    return reverse(
        "api:scans:scan_person_detail",
        kwargs={"scan_id": scan_id, "person_id": person_id},
    )


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
    PersonMentionFactory(scan=scan, person=person)
    PersonMentionFactory(scan=scan, person=person)

    response = client.get(scan_detail_url(scan.id))

    assert response.status_code == 200
    body = response.json()
    assert body["scan"]["id"] == str(scan.id)
    assert body["company"]["id"] == str(scan.company_id)
    assert body["scansTotal"] == 1
    assert len(body["personSnapshots"]) == 1
    assert body["personSnapshots"][0]["personId"] == str(person.id)
    assert body["personSnapshots"][0]["fullName"] == person.normalized_name
    assert body["personSnapshots"][0]["personSourcesCount"] == 2
    assert body["totalSourcesCount"] == 0


def test_scan_detail_returns_not_found(client: Client) -> None:
    """Return 404 for an unknown scan."""
    response = client.get(scan_detail_url(uuid4()))

    assert response.status_code == 404


def test_scan_person_detail_returns_scan_scoped_mentions(
    client: Client,
) -> None:
    """Return only the mentions found during the requested scan."""
    scan = ScanFactory()
    other_scan = ScanFactory(company=scan.company)
    person = PersonFactory(first_name="Ivan", last_name="Ivanov")
    PersonSnapshotFactory(scan=scan, person=person)

    mention = PersonMentionFactory(
        scan=scan,
        person=person,
        mention_type=MentionType.PROFILE,
    )
    PersonMentionFactory(scan=other_scan, person=person)

    response = client.get(scan_person_detail_url(scan.id, person.id))

    assert response.status_code == 200
    body = response.json()
    assert body["scan"]["id"] == str(scan.id)
    assert body["company"]["id"] == str(scan.company_id)
    assert body["personSnapshot"]["personId"] == str(person.id)
    assert body["personSnapshot"]["personSourcesCount"] == 1
    assert body["mentionsCount"] == 1
    assert len(body["mentions"]) == 1
    assert body["mentions"][0]["id"] == str(mention.id)
    assert body["mentions"][0]["source"]["id"] == str(mention.source_id)
    assert body["mentions"][0]["mentionTypeValue"] == MentionType.PROFILE


def test_scan_person_detail_returns_not_found_when_absent(
    client: Client,
) -> None:
    """Return 404 when the person has no snapshot in the scan."""
    scan = ScanFactory()

    response = client.get(scan_person_detail_url(scan.id, uuid4()))

    assert response.status_code == 404
