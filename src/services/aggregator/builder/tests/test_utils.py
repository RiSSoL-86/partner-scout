import pytest
from asgiref.sync import sync_to_async

from apps.persons.choices import MentionType
from apps.persons.tests.factories import PersonMentionFactory
from apps.scans.choices import ConfirmationLevel
from apps.sources.tests.factories import SourceFactory
from services.aggregator.builder.utils import compute_confirmation_level

pytestmark = pytest.mark.django_db(transaction=True)

create_mention = sync_to_async(PersonMentionFactory)
create_source = sync_to_async(SourceFactory)


async def test_confirms_on_a_profile_mention() -> None:
    """Rate a person with a profile mention as confirmed."""
    mention = await create_mention(mention_type=MentionType.PROFILE)

    assert compute_confirmation_level([mention]) == ConfirmationLevel.CONFIRMED


async def test_confirms_on_an_org_unit_mention() -> None:
    """Rate a person listed in an org unit as confirmed."""
    mention = await create_mention(mention_type=MentionType.ORG_UNIT)

    assert compute_confirmation_level([mention]) == ConfirmationLevel.CONFIRMED


async def test_probable_when_more_than_two_sources_agree() -> None:
    """Rate a person mentioned by over two sources as probable."""
    mentions = [
        await create_mention(
            mention_type=MentionType.OTHER,
            source=await create_source(),
        )
        for _ in range(3)
    ]

    assert compute_confirmation_level(mentions) == ConfirmationLevel.PROBABLE


async def test_unlikely_with_two_or_fewer_weak_sources() -> None:
    """Rate a person seen by at most two weak sources as unlikely."""
    mentions = [
        await create_mention(
            mention_type=MentionType.OTHER,
            source=await create_source(),
        )
        for _ in range(2)
    ]

    assert compute_confirmation_level(mentions) == ConfirmationLevel.UNLIKELY


async def test_unlikely_when_repeated_by_a_single_source() -> None:
    """Ignore repeat weak mentions from one source when rating."""
    source = await create_source()
    mentions = [
        await create_mention(mention_type=MentionType.OTHER, source=source)
        for _ in range(3)
    ]

    assert compute_confirmation_level(mentions) == ConfirmationLevel.UNLIKELY
