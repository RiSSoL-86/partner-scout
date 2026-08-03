from datetime import timedelta

import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.persons.models import Person
from apps.persons.repository import (
    PersonMentionRepository,
    PersonRepository,
)
from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.tests.factories import ScanFactory

pytestmark = pytest.mark.django_db(transaction=True)

create_person = sync_to_async(PersonFactory)
create_mention = sync_to_async(PersonMentionFactory)
create_scan = sync_to_async(ScanFactory)


async def test_list_by_person_id_returns_mentions_newest_first() -> None:
    """Return every mention of a person ordered newest first."""
    person = await create_person()
    now = timezone.now()
    older = await create_mention(
        person=person,
        created_timestamp=now - timedelta(hours=2),
    )
    newer = await create_mention(person=person, created_timestamp=now)

    mentions = await PersonMentionRepository().list_all(
        filters={"person_id": person.id},
        select_related=("source",),
        order_by=("-created_timestamp",),
    )

    assert [mention.id for mention in mentions] == [newer.id, older.id]


async def test_list_by_person_id_excludes_other_persons() -> None:
    """Return only the mentions belonging to the requested person."""
    person = await create_person()
    await create_mention(person=person)
    await create_mention(person=await create_person())

    mentions = await PersonMentionRepository().list_all(
        filters={"person_id": person.id},
    )

    assert {mention.person_id for mention in mentions} == {person.id}


async def test_list_by_person_id_returns_empty_without_mentions() -> None:
    """Return an empty list when the person has no mentions."""
    person = await create_person()

    mentions = await PersonMentionRepository().list_all(
        filters={"person_id": person.id},
    )

    assert mentions == []


async def test_count_by_person_id_counts_only_target_person() -> None:
    """Count only the mentions of the requested person."""
    person = await create_person()
    await create_mention(person=person)
    await create_mention(person=person)
    await create_mention(person=await create_person())

    total = await PersonMentionRepository().count(
        filters={"person_id": person.id},
    )

    assert total == 2


async def test_count_by_scan_for_person_groups_by_scan() -> None:
    """Group a person's mention counts per scan, ignoring other people."""
    person = await create_person()
    first_scan = await create_scan()
    second_scan = await create_scan()
    await create_mention(person=person, scan=first_scan)
    await create_mention(person=person, scan=first_scan)
    await create_mention(person=person, scan=second_scan)
    await create_mention(person=await create_person(), scan=first_scan)

    counts = await PersonMentionRepository().count_by_scan_for_person(
        person_id=person.id,
        scan_ids=[first_scan.id, second_scan.id],
    )

    assert counts == {first_scan.id: 2, second_scan.id: 1}


async def test_count_by_scan_for_person_empty_scan_ids() -> None:
    """Return an empty mapping when no scan ids are given."""
    person = await create_person()
    await create_mention(person=person)

    counts = await PersonMentionRepository().count_by_scan_for_person(
        person_id=person.id,
        scan_ids=[],
    )

    assert counts == {}


async def test_count_by_person_for_scan_groups_by_person() -> None:
    """Group a scan's mention counts per person, ignoring other scans."""
    scan = await create_scan()
    first = await create_person()
    second = await create_person()
    await create_mention(scan=scan, person=first)
    await create_mention(scan=scan, person=first)
    await create_mention(scan=scan, person=second)
    await create_mention(scan=await create_scan(), person=first)

    counts = await PersonMentionRepository().count_by_person_for_scan(
        scan_id=scan.id,
    )

    assert counts == {first.id: 2, second.id: 1}


async def test_list_grouped_by_person_for_scan_groups_and_prefetches() -> None:
    """Group a scan's mentions by person with people and sources joined."""
    scan = await create_scan()
    first = await create_person()
    second = await create_person()
    await create_mention(scan=scan, person=first)
    await create_mention(scan=scan, person=first)
    await create_mention(scan=scan, person=second)

    grouped = await PersonMentionRepository().list_grouped_by_person_for_scan(
        scan_id=scan.id,
    )

    assert set(grouped) == {first.id, second.id}
    assert len(grouped[first.id]) == 2
    # person and source are prefetched: touching them hits no extra query.
    assert grouped[first.id][0].person.id == first.id
    assert grouped[second.id][0].source is not None


async def test_list_grouped_by_person_for_scan_empty_without_mentions() -> (
    None
):
    """Return an empty mapping when the scan mentioned no one."""
    scan = await create_scan()

    grouped = await PersonMentionRepository().list_grouped_by_person_for_scan(
        scan_id=scan.id,
    )

    assert grouped == {}


async def test_list_by_surname_initial_filters_and_paginates() -> None:
    """Return a page of persons sharing a surname initial with the total."""
    await create_person(last_name="Ivanov")
    await create_person(last_name="Ivanova")
    await create_person(last_name="Petrov")

    page, total = await PersonRepository().list(
        filters={"normalized_name__istartswith": "I"},
        order_by=("normalized_name",),
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


async def resolve(
    repository: PersonRepository,
    first_name: str,
    middle_name: str,
    last_name: str,
) -> Person:
    """Resolve a name to a person through the identity-aware get_or_create."""
    return await repository.get_or_create(
        filters={},
        instance=Person(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
        ),
    )


async def test_get_or_create_makes_a_new_person() -> None:
    """Create a fresh record when no matching identity exists yet."""
    repository = PersonRepository()

    person = await resolve(repository, "Анвар", "", "Гафиатуллин")

    assert person.identity_key == "анвар гафиатуллин"
    assert await repository.count() == 1


async def test_get_or_create_merges_swapped_name_order() -> None:
    """Collapse a first/last swap onto the same identity, no new record."""
    repository = PersonRepository()
    first = await resolve(repository, "Анвар", "", "Гафиатуллин")

    again = await resolve(repository, "Гафиатуллин", "", "Анвар")

    assert again.id == first.id
    assert await repository.count() == 1


async def test_get_or_create_enriches_missing_patronymic() -> None:
    """Fill a patronymic-less record instead of spawning a duplicate."""
    repository = PersonRepository()
    bare = await resolve(repository, "Анвар", "", "Гафиатуллин")

    enriched = await resolve(repository, "Анвар", "Раисович", "Гафиатуллин")

    assert enriched.id == bare.id
    assert enriched.middle_name == "Раисович"
    assert enriched.normalized_name == "Гафиатуллин Анвар Раисович"
    assert await repository.count() == 1


async def test_get_or_create_matches_same_patronymic() -> None:
    """Return the existing record when the patronymic is the same."""
    repository = PersonRepository()
    first = await resolve(repository, "Анвар", "Раисович", "Гафиатуллин")

    again = await resolve(repository, "Анвар", "раисович", "Гафиатуллин")

    assert again.id == first.id
    assert await repository.count() == 1


async def test_get_or_create_splits_on_different_patronymic() -> None:
    """Treat a different patronymic as a namesake and keep both records."""
    repository = PersonRepository()
    raisovich = await resolve(repository, "Анвар", "Раисович", "Гафиатуллин")

    rinatovich = await resolve(repository, "Анвар", "Ринатович", "Гафиатуллин")

    assert rinatovich.id != raisovich.id
    assert await repository.count() == 2


async def test_get_or_create_bare_name_attaches_to_oldest() -> None:
    """Attach an ambiguous bare name to the oldest matching record."""
    repository = PersonRepository()
    oldest = await resolve(repository, "Анвар", "Раисович", "Гафиатуллин")
    await resolve(repository, "Анвар", "Ринатович", "Гафиатуллин")

    bare = await resolve(repository, "Анвар", "", "Гафиатуллин")

    assert bare.id == oldest.id
    assert await repository.count() == 2
