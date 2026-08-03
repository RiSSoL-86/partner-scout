from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from asgiref.sync import sync_to_async

from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.choices import (
    PositionType,
    PracticeArea,
    Specialization,
    WorkStatus,
)
from apps.scans.tests.factories import ScanFactory
from services.aggregator.classifier.services import ClassifierPersonService
from services.aggregator.schemas import (
    AiAggregationResult,
    AiClassification,
    ScanPersonMentions,
)

if TYPE_CHECKING:
    from services.aggregator.classifier.schemas import AiPersonInput

pytestmark = pytest.mark.django_db(transaction=True)

create_scan = sync_to_async(ScanFactory)
create_person = sync_to_async(PersonFactory)
create_mention = sync_to_async(PersonMentionFactory)


def classify_batch(
    company_name: str, persons: list[AiPersonInput]
) -> AiAggregationResult:
    """Fake the LLM: echo one default classification per input person."""
    return AiAggregationResult(
        persons=[
            AiClassification(
                person_id=person.person_id,
                position_type=PositionType.PARTNER,
                work_status=WorkStatus.FRONT_LINE,
                specialization=Specialization.FUNCTIONAL,
                practice_area=PracticeArea.AUDIT,
                role_title=person.mentions[0].role_title,
            )
            for person in persons
        ]
    )


async def build_scan_person_mentions(count: int) -> ScanPersonMentions:
    """Create ``count`` people with one mention each within a scan."""
    scan = await create_scan()
    person_by_id = {}
    mentions_by_person = {}
    for index in range(count):
        person = await create_person(last_name=f"Partner{index}")
        mention = await create_mention(
            scan=scan, person=person, role_title=f"Partner {index}"
        )
        person_by_id[person.id] = person
        mentions_by_person[person.id] = [mention]
    return ScanPersonMentions(
        person_by_id=person_by_id,
        mentions_by_person=mentions_by_person,
    )


async def test_classifies_every_person_keyed_by_id() -> None:
    """Return one classification per person keyed by person id."""
    scan_person_mentions = await build_scan_person_mentions(count=3)
    service = ClassifierPersonService()
    service.aggregator_ai_service = AsyncMock()  # type: ignore[misc]
    service.aggregator_ai_service.execute.side_effect = (
        lambda company_name, persons: classify_batch(company_name, persons)
    )

    classifications = await service.execute(
        company_name="Acme",
        scan_person_mentions=scan_person_mentions,
    )

    assert set(classifications) == {
        str(person_id) for person_id in scan_person_mentions.person_by_id
    }


async def test_splits_people_into_bounded_batches(settings) -> None:
    """Call the LLM once per batch of at most the configured size."""
    settings.AGGREGATOR_LLM_BATCH_SIZE = 2
    scan_person_mentions = await build_scan_person_mentions(count=5)
    service = ClassifierPersonService()
    service.aggregator_ai_service = AsyncMock()  # type: ignore[misc]
    service.aggregator_ai_service.execute.side_effect = (
        lambda company_name, persons: classify_batch(company_name, persons)
    )

    classifications = await service.execute(
        company_name="Acme",
        scan_person_mentions=scan_person_mentions,
    )

    # 5 people at batch size 2 → batches of 2, 2, 1.
    assert service.aggregator_ai_service.execute.await_count == 3
    batch_sizes = [
        len(call.kwargs["persons"])
        for call in service.aggregator_ai_service.execute.await_args_list
    ]
    assert batch_sizes == [2, 2, 1]
    assert len(classifications) == 5


async def test_no_llm_call_for_an_empty_scan() -> None:
    """Skip the LLM entirely when the scan mentioned no one."""
    service = ClassifierPersonService()
    service.aggregator_ai_service = AsyncMock()  # type: ignore[misc]

    classifications = await service.execute(
        company_name="Acme",
        scan_person_mentions=ScanPersonMentions(
            person_by_id={}, mentions_by_person={}
        ),
    )

    assert classifications == {}
    service.aggregator_ai_service.execute.assert_not_awaited()
