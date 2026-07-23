import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from apps.companies.models import Company
from apps.persons.models import Person
from apps.scans.choices import ConfirmationLevel, PositionType, ScanStatus
from apps.scans.models import PersonSnapshot, Scan, ScanSource
from apps.sources.models import Source


def create_company(name: str = "Example Consulting") -> Company:
    """Create a company for scan model tests."""
    return Company.objects.create(
        name=name,
        website_url="https://example.com",
    )


def create_person() -> Person:
    """Create a person for scan model tests."""
    return Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
        normalized_name="ivan petrov",
    )


def create_source(content: str = "Leadership profile page.") -> Source:
    """Create a source for scan model tests."""
    return Source.objects.create(
        url="https://example.com/team",
        title="Team",
        content=content,
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


@pytest.mark.django_db
def test_scan_source_links_scan_to_canonical_source() -> None:
    """Link a scan to a source found during that scan."""
    scan = Scan.objects.create(company=create_company())
    source = create_source()

    scan_source = ScanSource.objects.create(scan=scan, source=source)

    assert str(scan_source) == f"{scan} -> {source}"
    assert list(scan.source_links.all()) == [scan_source]
    assert list(source.scan_links.all()) == [scan_source]


@pytest.mark.django_db
def test_scan_source_rejects_duplicate_scan_source() -> None:
    """Reject duplicate scan-source links."""
    scan = Scan.objects.create(company=create_company())
    source = create_source()
    ScanSource.objects.create(scan=scan, source=source)

    with pytest.raises(IntegrityError), transaction.atomic():
        ScanSource.objects.create(scan=scan, source=source)


@pytest.mark.django_db
def test_person_snapshot_defaults() -> None:
    """Create one extracted person state for a scan."""
    scan = Scan.objects.create(company=create_company())
    person = create_person()
    source = create_source()
    ScanSource.objects.create(scan=scan, source=source)

    snapshot = PersonSnapshot.objects.create(
        scan=scan,
        person=person,
        source=source,
        role_title="Partner",
    )

    assert snapshot.position_type == PositionType.OTHER
    assert snapshot.organizational_unit == ""
    assert snapshot.email == ""
    assert snapshot.phone == ""
    assert snapshot.confirmation_level == ConfirmationLevel.LOW
    assert str(snapshot) == f"{person} - Partner (Example Consulting)"
    assert list(scan.person_snapshots.all()) == [snapshot]
    assert list(person.snapshots.all()) == [snapshot]
    assert list(source.person_snapshots.all()) == [snapshot]


@pytest.mark.django_db
def test_person_snapshot_rejects_duplicate_role_per_scan() -> None:
    """Reject duplicate person roles inside one scan."""
    scan = Scan.objects.create(company=create_company())
    person = create_person()
    source = create_source()
    ScanSource.objects.create(scan=scan, source=source)
    PersonSnapshot.objects.create(
        scan=scan,
        person=person,
        source=source,
        role_title="Partner",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        PersonSnapshot.objects.create(
            scan=scan,
            person=person,
            source=source,
            role_title="Partner",
        )


@pytest.mark.django_db
def test_person_snapshot_requires_source_linked_to_scan() -> None:
    """Reject snapshot evidence sources not found in the same scan."""
    scan = Scan.objects.create(company=create_company())
    snapshot = PersonSnapshot(
        scan=scan,
        person=create_person(),
        source=create_source(),
        role_title="Partner",
    )

    with pytest.raises(ValidationError) as exc_info:
        snapshot.full_clean()

    assert "source" in exc_info.value.message_dict


def test_scan_indexes_are_declared() -> None:
    """Declare indexes used by scan reports."""
    indexes = {index.name: index for index in Scan._meta.indexes}

    assert indexes["scan_company_created_idx"].fields == [
        "company",
        "created_timestamp",
    ]
    assert indexes["scan_status_created_idx"].fields == [
        "status",
        "created_timestamp",
    ]


def test_person_snapshot_indexes_are_declared() -> None:
    """Declare indexes used by snapshot reports."""
    indexes = {index.name: index for index in PersonSnapshot._meta.indexes}

    assert indexes["ps_scan_position_idx"].fields == [
        "scan",
        "position_type",
    ]
    assert indexes["ps_person_created_idx"].fields == [
        "person",
        "created_timestamp",
    ]


def test_person_snapshot_has_unique_role_constraint() -> None:
    """Declare uniqueness for person roles inside one scan."""
    constraints = {
        constraint.name: constraint
        for constraint in PersonSnapshot._meta.constraints
        if isinstance(constraint, models.UniqueConstraint)
    }

    assert constraints["unique_person_snapshot_role_per_scan"].fields == (
        "scan",
        "person",
        "role_title",
        "organizational_unit",
    )


def test_scan_source_has_unique_scan_source_constraint() -> None:
    """Declare uniqueness for sources inside one scan."""
    constraints = {
        constraint.name: constraint
        for constraint in ScanSource._meta.constraints
        if isinstance(constraint, models.UniqueConstraint)
    }

    assert constraints["unique_source_per_scan"].fields == ("scan", "source")


def test_scan_choice_values() -> None:
    """Expose stable scan choice values."""
    assert ScanStatus.PENDING == 0
    assert ScanStatus.RUNNING == 1
    assert ScanStatus.COMPLETED == 2
    assert ScanStatus.FAILED == 3
    assert PositionType.PARTNER == 0
    assert PositionType.DIRECTOR == 1
    assert PositionType.OTHER == 2
    assert ConfirmationLevel.CONFIRMED == 0
    assert ConfirmationLevel.HIGH == 1
    assert ConfirmationLevel.LOW == 2
