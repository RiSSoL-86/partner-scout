import uuid

import pytest
from django.db import models
from django.db.models.functions import Lower

from apps.persons.models import Person


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
