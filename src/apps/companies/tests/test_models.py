import pytest
from django.db import IntegrityError, transaction

from apps.companies.models import Company


@pytest.mark.django_db
def test_company_defaults() -> None:
    """Create an enabled company that has not been scanned yet."""
    company = Company.objects.create(
        name="Example Consulting",
        website_url="https://example.com",
    )

    assert company.scan_enabled is True
    assert company.last_scanned_at is None
    assert company.created_timestamp is not None
    assert company.updated_timestamp is not None
    assert str(company) == "Example Consulting"


@pytest.mark.django_db
def test_company_name_is_unique_case_insensitively() -> None:
    """Reject company names that differ only by letter casing."""
    Company.objects.create(
        name="Example Consulting",
        website_url="https://example.com",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        Company.objects.create(
            name="EXAMPLE CONSULTING",
            website_url="https://other.example.com",
        )
