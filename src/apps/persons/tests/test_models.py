import uuid

import pytest
from django.db import IntegrityError, models, transaction
from django.db.models.functions import Lower

from apps.companies.models import Company
from apps.persons.choices import MentionType
from apps.persons.models import Person, PersonMention
from apps.scans.models import Scan
from apps.sources.models import Source


def create_person() -> Person:
    """Create a person for person mention model tests."""
    return Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
    )


def create_source() -> Source:
    """Create a source for person mention model tests."""
    return Source.objects.create(
        url="https://example.com/team",
        title="Team",
    )


def create_scan() -> Scan:
    """Create a scan for person mention model tests."""
    company = Company.objects.create(
        name="Example Consulting",
        website_url="https://example.com",
    )
    return Scan.objects.create(company=company)


@pytest.mark.django_db
def test_person_defaults() -> None:
    """Create a canonical person without an optional middle name."""
    person = Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
    )

    assert isinstance(person.id, uuid.UUID)
    assert person.middle_name == ""
    assert person.created_timestamp is not None
    assert str(person) == "Petrov Ivan"


@pytest.mark.django_db
def test_person_full_name_includes_middle_name() -> None:
    """Assemble the normalized name as last, first then middle name."""
    person = Person.objects.create(
        first_name="Ivan",
        middle_name="Ivanovich",
        last_name="Petrov",
    )

    assert str(person) == "Petrov Ivan Ivanovich"


@pytest.mark.django_db
def test_normalized_name_is_generated_ignoring_input() -> None:
    """Overwrite any supplied normalized name with the assembled value."""
    person = Person.objects.create(
        first_name="Ivan",
        middle_name="Ivanovich",
        last_name="Petrov",
        normalized_name="whatever",
    )

    assert person.normalized_name == "Petrov Ivan Ivanovich"


def test_identity_key_has_case_insensitive_unique_constraint() -> None:
    """Declare case-insensitive uniqueness for identity key and patronymic."""
    constraints = {
        constraint.name: constraint
        for constraint in Person._meta.constraints
        if isinstance(constraint, models.UniqueConstraint)
    }

    constraint = constraints["unique_person_identity"]
    assert len(constraint.expressions) == 2
    assert all(isinstance(expr, Lower) for expr in constraint.expressions)
    assert [
        expr.source_expressions[0].name for expr in constraint.expressions
    ] == ["identity_key", "middle_name"]


def test_identity_key_ignores_name_order() -> None:
    """Assemble the same identity key regardless of first/last order."""
    swapped = Person.build_identity_key(
        first_name="Гафиатуллин", last_name="Анвар"
    )
    straight = Person.build_identity_key(
        first_name="Анвар", last_name="Гафиатуллин"
    )

    assert swapped == straight == "анвар гафиатуллин"


@pytest.mark.django_db
def test_identity_key_is_generated_on_save() -> None:
    """Derive the identity key from the name parts, excluding patronymic."""
    person = Person.objects.create(
        first_name="Анвар",
        middle_name="Раисович",
        last_name="Гафиатуллин",
    )

    assert person.identity_key == "анвар гафиатуллин"


def test_person_mention_has_unique_person_source_constraint() -> None:
    """Declare uniqueness for a person mention in one scan source."""
    constraints = {
        constraint.name: constraint
        for constraint in PersonMention._meta.constraints
        if isinstance(constraint, models.UniqueConstraint)
    }

    constraint = constraints["unique_person_source_mention_per_scan"]
    assert constraint.fields == ("scan", "person", "source")


@pytest.mark.django_db
def test_person_mention_defaults() -> None:
    """Create a person mention with the default mention type."""
    person = create_person()
    source = create_source()
    scan = create_scan()

    mention = PersonMention.objects.create(
        scan=scan,
        person=person,
        source=source,
    )

    assert isinstance(mention.id, uuid.UUID)
    assert mention.mention_type == MentionType.OTHER
    assert mention.role_title == ""
    assert mention.email == ""
    assert mention.phone == ""
    assert mention.created_timestamp is not None
    assert mention.updated_timestamp is not None
    assert str(mention) == f"{person} in {source}"
    assert list(person.source_mentions.all()) == [mention]
    assert list(source.person_mentions.all()) == [mention]
    assert list(scan.person_mentions.all()) == [mention]


@pytest.mark.django_db
def test_person_mention_rejects_duplicate_person_source() -> None:
    """Reject duplicate mentions for one person, source and scan."""
    person = create_person()
    source = create_source()
    scan = create_scan()
    PersonMention.objects.create(
        scan=scan,
        person=person,
        source=source,
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        PersonMention.objects.create(
            scan=scan,
            person=person,
            source=source,
        )


def test_mention_type_values() -> None:
    """Expose stable person mention type values."""
    assert MentionType.PROFILE == 0
    assert MentionType.ORG_UNIT == 1
    assert MentionType.OTHER == 2
