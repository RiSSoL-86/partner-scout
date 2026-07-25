from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async

from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
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
create_mention = sync_to_async(PersonMentionFactory)


async def test_execute_returns_person_with_mentions_count() -> None:
    """Return the person together with how many mentions they have."""
    person = await create_person()
    await create_mention(person=person)
    await create_mention(person=person)

    loaded, total = await PersonMentionsService().execute(person.id)

    assert loaded is not None
    assert loaded.id == person.id
    assert total == 2


async def test_execute_returns_none_for_unknown_person() -> None:
    """Return no person and a zero count for an unknown id."""
    loaded, total = await PersonMentionsService().execute(uuid4())

    assert loaded is None
    assert total == 0


async def test_list_service_paginates_persons_by_name() -> None:
    """Return a page of persons ordered by name with their total."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Petrov")
    await create_person(last_name="Sidorov")

    persons, total = await PersonListService().execute(offset=0, limit=2)

    assert total == 3
    assert len(persons) == 2


async def test_by_letter_service_filters_by_surname_initial() -> None:
    """Return only persons whose surname starts with the letter."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Ivanova")
    await create_person(last_name="Petrov")

    persons, total = await PersonByLetterListService().execute(
        letter="I",
        offset=0,
        limit=10,
    )

    assert total == 2
    assert all(
        person.normalized_name.startswith("Ivanov") for person in persons
    )


async def test_alphabet_service_groups_initials_with_counts() -> None:
    """Return surname initials with their counts ordered alphabetically."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Petrov")
    await create_person(last_name="Petrova")

    initials = await PersonAlphabetService().execute()

    assert initials == [("I", 1), ("P", 2)]
