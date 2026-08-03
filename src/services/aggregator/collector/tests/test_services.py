import pytest
from asgiref.sync import sync_to_async

from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.tests.factories import ScanFactory
from services.aggregator.collector.services import (
    CollectorPersonMentionService,
)

pytestmark = pytest.mark.django_db(transaction=True)

create_scan = sync_to_async(ScanFactory)
create_person = sync_to_async(PersonFactory)
create_mention = sync_to_async(PersonMentionFactory)


async def test_groups_a_scans_mentions_by_person() -> None:
    """Return the scan's people keyed by id with their mentions."""
    scan = await create_scan()
    first = await create_person()
    second = await create_person()
    await create_mention(scan=scan, person=first)
    await create_mention(scan=scan, person=first)
    await create_mention(scan=scan, person=second)

    result = await CollectorPersonMentionService().execute(scan_id=scan.id)

    assert set(result.person_by_id) == {first.id, second.id}
    assert result.person_by_id[first.id].id == first.id
    assert len(result.mentions_by_person[first.id]) == 2
    assert len(result.mentions_by_person[second.id]) == 1


async def test_ignores_mentions_from_other_scans() -> None:
    """Collect only the mentions belonging to the requested scan."""
    scan = await create_scan()
    person = await create_person()
    await create_mention(scan=scan, person=person)
    await create_mention(scan=await create_scan(), person=person)

    result = await CollectorPersonMentionService().execute(scan_id=scan.id)

    assert len(result.mentions_by_person[person.id]) == 1


async def test_returns_empty_result_without_mentions() -> None:
    """Return an empty, falsy result when the scan mentioned no one."""
    scan = await create_scan()

    result = await CollectorPersonMentionService().execute(scan_id=scan.id)

    assert not result
    assert result.person_by_id == {}
    assert result.mentions_by_person == {}
