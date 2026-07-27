from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.urls import reverse

from apps.companies.tests.factories import CompanyFactory
from apps.scans.tests.factories import ScanFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


def list_url() -> str:
    """Return the company list url."""
    return reverse("api:companies:company_list")


def scans_url(company_id: object) -> str:
    """Return the company scans url for a company id."""
    return reverse(
        "api:companies:company_scans",
        kwargs={"company_id": company_id},
    )


def test_company_list_returns_page(client: Client) -> None:
    """Return every company ordered by name with its total."""
    CompanyFactory(name="Beta")
    CompanyFactory(name="Alpha")

    response = client.get(list_url())

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["name"] for item in body["items"]] == ["Alpha", "Beta"]
    assert body["offset"] == 0
    assert body["limit"] == 20


def test_company_list_filters_by_name(client: Client) -> None:
    """Filter companies by a case-insensitive name substring."""
    CompanyFactory(name="Acme Group")
    CompanyFactory(name="Globex")

    response = client.get(list_url(), data={"search": "acme"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Acme Group"


def test_company_list_paginates(client: Client) -> None:
    """Apply offset and limit to the company list."""
    for index in range(3):
        CompanyFactory(name=f"Company {index}")

    response = client.get(list_url(), data={"offset": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Company 1"


def test_company_list_rejects_invalid_limit(client: Client) -> None:
    """Reject a limit above the allowed maximum."""
    response = client.get(list_url(), data={"limit": 999})

    assert response.status_code == 400


def test_company_scans_returns_company_scans(client: Client) -> None:
    """Return a company's scans newest-first with the company header."""
    company = CompanyFactory(name="Acme")
    ScanFactory(company=company)
    ScanFactory(company=company)

    response = client.get(scans_url(company.id))

    assert response.status_code == 200
    body = response.json()
    assert body["company"]["id"] == str(company.id)
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_company_scans_returns_not_found(client: Client) -> None:
    """Return 404 when listing scans for an unknown company."""
    response = client.get(scans_url(uuid4()))

    assert response.status_code == 404
