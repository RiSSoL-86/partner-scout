import factory
from factory.django import DjangoModelFactory

from apps.companies.tests.factories import CompanyFactory
from apps.persons.tests.factories import PersonFactory
from apps.scans.choices import ConfirmationLevel, PositionType, ScanStatus
from apps.scans.models import PersonSnapshot, Scan


class ScanFactory(DjangoModelFactory[Scan]):
    """Build completed scans with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = Scan
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    status = ScanStatus.COMPLETED
    pages_scanned = 0

    @factory.post_generation
    def created_timestamp(obj, create, extracted, **kwargs):
        """Override the managed creation timestamp when one is given."""
        if create and extracted is not None:
            Scan.objects.filter(pk=obj.pk).update(
                created_timestamp=extracted,
            )
            obj.created_timestamp = extracted


class PersonSnapshotFactory(DjangoModelFactory[PersonSnapshot]):
    """Build person snapshots with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = PersonSnapshot

    scan = factory.SubFactory(ScanFactory)
    person = factory.SubFactory(PersonFactory)
    position_type = PositionType.PARTNER
    role_title = factory.Sequence(lambda n: f"Role {n}")
    confirmation_level = ConfirmationLevel.UNLIKELY
