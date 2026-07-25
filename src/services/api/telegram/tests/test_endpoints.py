from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.urls import reverse

from apps.common.services.report_token import ReportTokenService
from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.tests.factories import PersonSnapshotFactory, ScanFactory
from apps.sources.tests.factories import SourceFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


def person_url(person_id: object) -> str:
    """Return the person report url for a person id."""
    return reverse(
        "api:telegram:telegram_person_detail",
        kwargs={"person_id": person_id},
    )


def scan_url(scan_id: object) -> str:
    """Return the company scan report url for a scan id."""
    return reverse(
        "api:telegram:telegram_company_scan_detail",
        kwargs={"scan_id": scan_id},
    )


def test_person_report_renders_with_valid_token(client: Client) -> None:
    """Render the person report for a correctly signed link."""
    person = PersonFactory(first_name="Alexander", last_name="Yakovlev")
    PersonMentionFactory(person=person, source=SourceFactory(title="Team"))
    token = ReportTokenService.sign(str(person.id))

    response = client.get(person_url(person.id), data={"token": token})

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    body = response.content.decode()
    assert person.normalized_name in body
    assert "Team" in body


def test_person_report_rejects_invalid_token(client: Client) -> None:
    """Reject the person report when the token does not match."""
    person = PersonFactory()

    response = client.get(person_url(person.id), data={"token": "tampered"})

    assert response.status_code == 403


def test_person_report_returns_not_found_for_unknown_person(
    client: Client,
) -> None:
    """Return 404 when the signed person does not exist."""
    person_id = uuid4()
    token = ReportTokenService.sign(str(person_id))

    response = client.get(person_url(person_id), data={"token": token})

    assert response.status_code == 404


def test_company_report_renders_with_valid_token(client: Client) -> None:
    """Render the company scan report for a correctly signed link."""
    scan = ScanFactory()
    person = PersonFactory(first_name="Ivan", last_name="Ivanov")
    PersonSnapshotFactory(scan=scan, person=person)
    token = ReportTokenService.sign(str(scan.id))

    response = client.get(scan_url(scan.id), data={"token": token})

    assert response.status_code == 200
    body = response.content.decode()
    assert scan.company.name in body
    assert person.normalized_name in body


def test_company_report_rejects_invalid_token(client: Client) -> None:
    """Reject the company report when the token does not match."""
    scan = ScanFactory()

    response = client.get(scan_url(scan.id), data={"token": "tampered"})

    assert response.status_code == 403


def test_company_report_returns_not_found_for_unknown_scan(
    client: Client,
) -> None:
    """Return 404 when the signed scan does not exist."""
    scan_id = uuid4()
    token = ReportTokenService.sign(str(scan_id))

    response = client.get(scan_url(scan_id), data={"token": token})

    assert response.status_code == 404
