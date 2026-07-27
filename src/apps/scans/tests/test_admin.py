import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.companies.models import Company
from apps.persons.models import Person
from apps.scans.admin import (
    PersonSnapshotAdmin,
    PersonSnapshotInline,
    ScanAdmin,
    ScanSourceAdmin,
    ScanSourceInline,
)
from apps.scans.choices import PositionType
from apps.scans.models import PersonSnapshot, Scan, ScanSource
from apps.sources.models import Source


def create_company() -> Company:
    """Create a company for scan admin tests."""
    return Company.objects.create(
        name="Example Consulting",
        website_url="https://example.com",
    )


def create_person() -> Person:
    """Create a person for scan admin tests."""
    return Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
    )


def create_source() -> Source:
    """Create a source for scan admin tests."""
    return Source.objects.create(
        url="https://example.com/team",
        title="Team",
        content="Leadership profile page.",
    )


@pytest.fixture
def admin_client() -> Client:
    """Return an authenticated admin client."""
    user_model = get_user_model()
    user = user_model.objects.create_superuser(
        email="admin@example.com",
        password="password",
        first_name="Admin",
        last_name="User",
    )
    client = Client()
    client.force_login(user)
    return client


def test_scan_admin_registration() -> None:
    """Register scan with source and snapshot inlines."""
    scan_admin = admin.site._registry[Scan]

    assert isinstance(scan_admin, ScanAdmin)
    assert scan_admin.inlines == (ScanSourceInline, PersonSnapshotInline)


def test_scan_source_admin_registration() -> None:
    """Register scan-source links as a standalone admin section."""
    scan_source_admin = admin.site._registry[ScanSource]

    assert isinstance(scan_source_admin, ScanSourceAdmin)
    assert scan_source_admin.autocomplete_fields == ("scan", "source")


def test_person_snapshot_admin_registration() -> None:
    """Register person snapshots as a standalone admin section."""
    person_snapshot_admin = admin.site._registry[PersonSnapshot]

    assert isinstance(person_snapshot_admin, PersonSnapshotAdmin)
    assert person_snapshot_admin.autocomplete_fields == (
        "scan",
        "person",
    )


@pytest.mark.django_db
def test_scan_admin_pages_are_available(admin_client: Client) -> None:
    """Open scan admin pages as a superuser."""
    scan = Scan.objects.create(company=create_company())

    urls = (
        reverse("admin:scans_scan_changelist"),
        reverse("admin:scans_scan_add"),
        reverse("admin:scans_scan_change", args=(scan.pk,)),
    )

    for url in urls:
        response = admin_client.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
def test_scan_source_admin_pages_are_available(admin_client: Client) -> None:
    """Open scan-source admin pages as a superuser."""
    scan = Scan.objects.create(company=create_company())
    source = create_source()
    scan_source = ScanSource.objects.create(scan=scan, source=source)

    urls = (
        reverse("admin:scans_scansource_changelist"),
        reverse("admin:scans_scansource_add"),
        reverse("admin:scans_scansource_change", args=(scan_source.pk,)),
    )

    for url in urls:
        response = admin_client.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
def test_person_snapshot_admin_pages_are_available(
    admin_client: Client,
) -> None:
    """Open person snapshot admin pages as a superuser."""
    scan = Scan.objects.create(company=create_company())
    person = create_person()
    snapshot = PersonSnapshot.objects.create(
        scan=scan,
        person=person,
        position_type=PositionType.PARTNER,
        role_title="Partner",
    )

    urls = (
        reverse("admin:scans_personsnapshot_changelist"),
        reverse("admin:scans_personsnapshot_add"),
        reverse("admin:scans_personsnapshot_change", args=(snapshot.pk,)),
    )

    for url in urls:
        response = admin_client.get(url)

        assert response.status_code == 200
