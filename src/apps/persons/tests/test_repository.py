from datetime import timedelta

import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.persons.repository import (
    PersonMentionRepository,
    PersonRepository,
)
from apps.persons.tests.factories import PersonFactory, PersonMentionFactory

pytestmark = pytest.mark.django_db(transaction=True)

create_person = sync_to_async(PersonFactory)
create_mention = sync_to_async(PersonMentionFactory)


async def test_list_by_person_id_returns_mentions_newest_first() -> None:
    """Return every mention of a person ordered newest first."""
    person = await create_person()
    now = timezone.now()
    older = await create_mention(
        person=person,
        created_timestamp=now - timedelta(hours=2),
    )
    newer = await create_mention(person=person, created_timestamp=now)

    mentions = await PersonMentionRepository().list_by_person_id(person.id)

    assert [mention.id for mention in mentions] == [newer.id, older.id]


async def test_list_by_person_id_excludes_other_persons() -> None:
    """Return only the mentions belonging to the requested person."""
    person = await create_person()
    await create_mention(person=person)
    await create_mention(person=await create_person())

    mentions = await PersonMentionRepository().list_by_person_id(person.id)

    assert {mention.person_id for mention in mentions} == {person.id}


async def test_list_by_person_id_returns_empty_without_mentions() -> None:
    """Return an empty list when the person has no mentions."""
    person = await create_person()

    mentions = await PersonMentionRepository().list_by_person_id(person.id)

    assert mentions == []


async def test_count_by_person_id_counts_only_target_person() -> None:
    """Count only the mentions of the requested person."""
    person = await create_person()
    await create_mention(person=person)
    await create_mention(person=person)
    await create_mention(person=await create_person())

    total = await PersonMentionRepository().count_by_person_id(person.id)

    assert total == 2


async def test_list_by_surname_initial_filters_and_paginates() -> None:
    """Return a page of persons sharing a surname initial with the total."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Ivanova")
    await create_person(last_name="Petrov")

    page, total = await PersonRepository().list_by_surname_initial(
        initial="I",
        offset=0,
        limit=1,
    )

    assert total == 2
    assert len(page) == 1
    assert page[0].normalized_name.startswith("Ivanov")


async def test_list_surname_initials_groups_counts_ordered() -> None:
    """Group surname initials with their counts ordered alphabetically."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Petrov")
    await create_person(last_name="Petrova")

    initials = await PersonRepository().list_surname_initials()

    assert initials == [("I", 1), ("P", 2)]
