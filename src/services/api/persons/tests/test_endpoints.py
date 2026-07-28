from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.urls import reverse

from apps.persons.choices import MentionType
from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.tests.factories import ScanFactory
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


def sources_url(person_id: object) -> str:
    """Return the person sources url for a person id."""
    return reverse(
        "api:persons:person_sources",
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


def test_person_sources_returns_all_sources(client: Client) -> None:
    """Return the person's sources with the person header and total."""
    person = PersonFactory(first_name="John", last_name="Doe")
    first_source = SourceFactory()
    second_source = SourceFactory()
    PersonMentionFactory(person=person, source=first_source)
    PersonMentionFactory(person=person, source=second_source)

    response = client.get(sources_url(person.id))

    assert response.status_code == 200
    body = response.json()
    assert body["person"]["id"] == str(person.id)
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_person_sources_deduplicates_across_scans(client: Client) -> None:
    """Count a source once even when it is mentioned in several scans."""
    person = PersonFactory(first_name="John", last_name="Doe")
    source = SourceFactory()
    PersonMentionFactory(person=person, source=source, scan=ScanFactory())
    PersonMentionFactory(person=person, source=source, scan=ScanFactory())

    response = client.get(sources_url(person.id))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == str(source.id)


def test_person_sources_returns_not_found(client: Client) -> None:
    """Return 404 when listing sources for an unknown person."""
    response = client.get(sources_url(uuid4()))

    assert response.status_code == 404
