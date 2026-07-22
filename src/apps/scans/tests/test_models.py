import pytest
from django.db import IntegrityError, transaction

from apps.companies.models import Company
from apps.scans.choices import ScanStatus
from apps.scans.models import Scan


def create_company(name: str = "Example Consulting") -> Company:
    """Create a company for scan model tests."""
    return Company.objects.create(
        name=name,
        website_url="https://example.com",
    )


@pytest.mark.django_db
def test_scan_defaults() -> None:
    """Create a pending scan with empty progress and outcome fields."""
    company = create_company()

    scan = Scan.objects.create(company=company)

    assert scan.status == ScanStatus.PENDING
    assert scan.pages_scanned == 0
    assert scan.report == ""
    assert scan.error == ""
    assert str(scan) == f"{scan.id} (Example Consulting)"
    assert list(company.scans.all()) == [scan]


@pytest.mark.django_db
def test_company_allows_multiple_historical_scans() -> None:
    """Allow multiple completed or failed scans for one company."""
    company = create_company()

    completed = Scan.objects.create(
        company=company,
        status=ScanStatus.COMPLETED,
    )
    failed = Scan.objects.create(
        company=company,
        status=ScanStatus.FAILED,
    )

    assert list(company.scans.order_by("created_timestamp")) == [
        completed,
        failed,
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("existing_status", "new_status"),
    [
        (ScanStatus.PENDING, ScanStatus.PENDING),
        (ScanStatus.PENDING, ScanStatus.RUNNING),
        (ScanStatus.RUNNING, ScanStatus.PENDING),
        (ScanStatus.RUNNING, ScanStatus.RUNNING),
    ],
)
def test_company_allows_only_one_active_scan(
    existing_status: ScanStatus,
    new_status: ScanStatus,
) -> None:
    """Reject a second pending or running scan for one company."""
    company = create_company()
    Scan.objects.create(company=company, status=existing_status)

    with pytest.raises(IntegrityError), transaction.atomic():
        Scan.objects.create(company=company, status=new_status)


@pytest.mark.django_db
def test_company_can_start_scan_after_historical_scan() -> None:
    """Allow a new active scan after a previous scan has finished."""
    company = create_company()
    Scan.objects.create(company=company, status=ScanStatus.COMPLETED)

    active = Scan.objects.create(
        company=company,
        status=ScanStatus.PENDING,
    )

    assert active.status == ScanStatus.PENDING
