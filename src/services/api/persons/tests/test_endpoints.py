from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.urls import reverse

from apps.persons.choices import MentionType
from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.tests.factories import PersonSnapshotFactory, ScanFactory
from apps.sources.tests.factories import SourceFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


def person_choices_url() -> str:
    """Return the person choices url."""
    return reverse("api:persons:person_choices")


def list_url() -> str:
    """Return the person list url."""
    return reverse("api:persons:person_list")


def timeline_url(person_id: object) -> str:
    """Return the person timeline url for a person id."""
    return reverse(
        "api:persons:person_timeline",
        kwargs={"person_id": person_id},
    )


def test_person_choices_expose_mention_type(client: Client) -> None:
    """Expose the mention type choices with value and label."""
    response = client.get(person_choices_url())

    assert response.status_code == 200
    options = response.json()["personMention"]["mentionType"]
    assert {option["value"] for option in options} == set(MentionType.values)
    profile = next(
        option for option in options if option["value"] == MentionType.PROFILE
    )
    assert profile["label"] == "profile"


def test_person_list_returns_page(client: Client) -> None:
    """Return every person ordered by name with its total."""
    PersonFactory(first_name="John", last_name="Beta")
    PersonFactory(first_name="John", last_name="Alpha")

    response = client.get(list_url())

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["lastName"] for item in body["items"]] == ["Alpha", "Beta"]
    assert body["offset"] == 0
    assert body["limit"] == 20


def test_person_list_filters_by_name(client: Client) -> None:
    """Filter persons by a case-insensitive normalized name substring."""
    PersonFactory(first_name="Jane", last_name="Acme")
    PersonFactory(first_name="John", last_name="Globex")

    response = client.get(list_url(), data={"search": "acme"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["lastName"] == "Acme"


def test_person_list_paginates(client: Client) -> None:
    """Apply offset and limit to the person list."""
    for index in range(3):
        PersonFactory(first_name="John", last_name=f"Name{index}")

    response = client.get(list_url(), data={"offset": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1


def test_person_list_rejects_invalid_limit(client: Client) -> None:
    """Reject a limit above the allowed maximum."""
    response = client.get(list_url(), data={"limit": 999})

    assert response.status_code == 400


def test_person_timeline_returns_entries_newest_first(client: Client) -> None:
    """Return one entry per snapshot ordered by scan date, newest first."""
    person = PersonFactory(first_name="John", last_name="Doe")
    older_scan = ScanFactory(
        created_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )
    newer_scan = ScanFactory(
        created_timestamp=datetime(2026, 6, 1, tzinfo=UTC),
    )
    PersonSnapshotFactory(person=person, scan=older_scan, role_title="Junior")
    PersonSnapshotFactory(person=person, scan=newer_scan, role_title="Partner")

    response = client.get(timeline_url(person.id))

    assert response.status_code == 200
    body = response.json()
    assert body["person"]["id"] == str(person.id)
    assert body["total"] == 2
    assert [item["roleTitle"] for item in body["items"]] == [
        "Partner",
        "Junior",
    ]
    first = body["items"][0]
    assert first["scanId"] == str(newer_scan.id)
    assert first["company"]["id"] == str(newer_scan.company_id)


def test_person_timeline_keeps_repeated_snapshots(client: Client) -> None:
    """Keep an entry per scan even when the role never changes."""
    person = PersonFactory(first_name="John", last_name="Doe")
    for _ in range(3):
        PersonSnapshotFactory(
            person=person,
            scan=ScanFactory(),
            role_title="Partner",
        )

    response = client.get(timeline_url(person.id))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_person_timeline_counts_sources_per_scan(client: Client) -> None:
    """Report how many sources prove the person's state in that scan."""
    person = PersonFactory(first_name="John", last_name="Doe")
    scan = ScanFactory()
    PersonSnapshotFactory(person=person, scan=scan, role_title="Partner")
    PersonMentionFactory(person=person, scan=scan, source=SourceFactory())
    PersonMentionFactory(person=person, scan=scan, source=SourceFactory())

    response = client.get(timeline_url(person.id))

    assert response.status_code == 200
    entry = response.json()["items"][0]
    assert entry["personMentionsCount"] == 2
    assert "sources" not in entry


def test_person_timeline_counts_zero_without_mentions(client: Client) -> None:
    """Show a snapshot with no mentions as a zero mention count."""
    person = PersonFactory(first_name="John", last_name="Doe")
    PersonSnapshotFactory(person=person, scan=ScanFactory())

    response = client.get(timeline_url(person.id))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["personMentionsCount"] == 0


def test_person_timeline_paginates(client: Client) -> None:
    """Apply offset and limit to the timeline while reporting the total."""
    person = PersonFactory(first_name="John", last_name="Doe")
    for _ in range(3):
        PersonSnapshotFactory(person=person, scan=ScanFactory())

    response = client.get(
        timeline_url(person.id), data={"offset": 1, "limit": 1}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1


def test_person_timeline_returns_not_found(client: Client) -> None:
    """Return 404 when listing the timeline for an unknown person."""
    response = client.get(timeline_url(uuid4()))

    assert response.status_code == 404
