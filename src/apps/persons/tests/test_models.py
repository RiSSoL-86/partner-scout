import uuid

import pytest
from django.db import IntegrityError, models, transaction
from django.db.models.functions import Lower

from apps.persons.choices import MentionType
from apps.persons.models import Person, PersonMention
from apps.sources.models import Source


def create_person() -> Person:
    """Create a person for person mention model tests."""
    return Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
        normalized_name="ivan petrov",
    )


def create_source() -> Source:
    """Create a source for person mention model tests."""
    return Source.objects.create(
        url="https://example.com/team",
        title="Team",
        content="Leadership profile page.",
    )


@pytest.mark.django_db
def test_person_defaults() -> None:
    """Create a canonical person without an optional middle name."""
    person = Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
        normalized_name="ivan petrov",
    )

    assert isinstance(person.id, uuid.UUID)
    assert person.middle_name == ""
    assert person.created_timestamp is not None
    assert str(person) == "ivan petrov"


@pytest.mark.django_db
def test_person_full_name_includes_middle_name() -> None:
    """Include a known middle name in the display representation."""
    person = Person.objects.create(
        first_name="Ivan",
        middle_name="Ivanovich",
        last_name="Petrov",
        normalized_name="ivan ivanovich petrov",
    )

    assert str(person) == "ivan ivanovich petrov"


def test_normalized_name_has_case_insensitive_unique_constraint() -> None:
    """Declare case-insensitive uniqueness for normalized names."""
    field = Person._meta.get_field("normalized_name")
    constraints = {
        constraint.name: constraint
        for constraint in Person._meta.constraints
        if isinstance(constraint, models.UniqueConstraint)
    }

    constraint = constraints["unique_normalized_name_name"]
    assert field.unique is False
    assert len(constraint.expressions) == 1
    assert isinstance(constraint.expressions[0], Lower)
    assert (
        constraint.expressions[0].source_expressions[0].name
        == "normalized_name"
    )


def test_person_mention_has_unique_person_source_constraint() -> None:
    """Declare uniqueness for a person mention in one source."""
    constraints = {
        constraint.name: constraint
        for constraint in PersonMention._meta.constraints
        if isinstance(constraint, models.UniqueConstraint)
    }

    constraint = constraints["unique_person_source_mention"]
    assert constraint.fields == ("person", "source")


@pytest.mark.django_db
def test_person_mention_defaults() -> None:
    """Create a person mention with the default mention type."""
    person = create_person()
    source = create_source()

    mention = PersonMention.objects.create(
        person=person,
        source=source,
        context="Ivan Petrov is listed as a partner.",
    )

    assert isinstance(mention.id, uuid.UUID)
    assert mention.mention_type == MentionType.OTHER
    assert mention.context == "Ivan Petrov is listed as a partner."
    assert mention.created_timestamp is not None
    assert mention.updated_timestamp is not None
    assert str(mention) == f"{person} in {source}"
    assert list(person.source_mentions.all()) == [mention]
    assert list(source.person_mentions.all()) == [mention]


@pytest.mark.django_db
def test_person_mention_rejects_duplicate_person_source() -> None:
    """Reject duplicate mentions for the same person and source."""
    person = create_person()
    source = create_source()
    PersonMention.objects.create(
        person=person,
        source=source,
        context="First context.",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        PersonMention.objects.create(
            person=person,
            source=source,
            context="Second context.",
        )


def test_mention_type_values() -> None:
    """Expose stable person mention type values."""
    assert MentionType.PROFILE == 0
    assert MentionType.TEAM == 1
    assert MentionType.AUTHOR == 2
    assert MentionType.INTERVIEW == 3
    assert MentionType.QUOTE == 4
    assert MentionType.EVENT == 5
    assert MentionType.OTHER == 6
