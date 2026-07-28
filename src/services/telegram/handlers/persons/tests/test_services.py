from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async

from apps.persons.tests.factories import PersonFactory
from apps.scans.tests.factories import PersonSnapshotFactory
from services.telegram.handlers.persons.services.alphabet import (
    PersonAlphabetService,
)
from services.telegram.handlers.persons.services.by_letter import (
    PersonByLetterListService,
)
from services.telegram.handlers.persons.services.list import (
    PersonListService,
)
from services.telegram.handlers.persons.services.person_mentions import (
    PersonMentionsService,
)

pytestmark = pytest.mark.django_db(transaction=True)

create_person = sync_to_async(PersonFactory)
create_snapshot = sync_to_async(PersonSnapshotFactory)


async def test_execute_returns_person_with_scans_count() -> None:
    """Return the person together with how many scans they appear in."""
    person = await create_person()
    await create_snapshot(person=person)
    await create_snapshot(person=person)

    result = await PersonMentionsService().execute(person.id)

    assert result["person"] is not None
    assert result["person"].id == person.id
    assert result["total"] == 2


async def test_execute_returns_none_for_unknown_person() -> None:
    """Return no person and a zero count for an unknown id."""
    result = await PersonMentionsService().execute(uuid4())

    assert result["person"] is None
    assert result["total"] == 0


async def test_list_service_paginates_persons_by_name() -> None:
    """Return a page of persons ordered by name with their total."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Petrov")
    await create_person(last_name="Sidorov")

    result = await PersonListService().execute(offset=0, limit=2)

    assert result["total"] == 3
    assert len(result["persons"]) == 2


async def test_by_letter_service_filters_by_surname_initial() -> None:
    """Return only persons whose surname starts with the letter."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Ivanova")
    await create_person(last_name="Petrov")

    result = await PersonByLetterListService().execute(
        letter="I",
        offset=0,
        limit=10,
    )

    assert result["total"] == 2
    assert all(
        person.normalized_name.startswith("Ivanov")
        for person in result["persons"]
    )


async def test_alphabet_service_groups_initials_with_counts() -> None:
    """Return surname initials with their counts ordered alphabetically."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Petrov")
    await create_person(last_name="Petrova")

    initials = await PersonAlphabetService().execute()

    assert initials == [("I", 1), ("P", 2)]
