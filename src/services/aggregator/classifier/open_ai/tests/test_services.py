from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from apps.persons.choices import MentionType
from apps.scans.choices import (
    PositionType,
    PracticeArea,
    Specialization,
    WorkStatus,
)
from services.aggregator.classifier.open_ai.services import (
    AggregatorOpenAiService,
)
from services.aggregator.classifier.schemas import AiMention, AiPersonInput
from services.aggregator.schemas import AiAggregationResult, AiClassification


def make_person_input(person_id: str = "p-1") -> AiPersonInput:
    """Build a single-mention LLM input payload for one person."""
    return AiPersonInput(
        person_id=person_id,
        full_name="Ivan Petrov",
        mentions=[
            AiMention(
                role_title="Partner",
                mention_type=MentionType.PROFILE,
                source_title="Team page",
            )
        ],
    )


async def test_returns_the_parsed_llm_result() -> None:
    """Return the structured result the OpenAI client parsed."""
    parsed = AiAggregationResult(
        persons=[
            AiClassification(
                person_id="p-1",
                position_type=PositionType.PARTNER,
                work_status=WorkStatus.FRONT_LINE,
                specialization=Specialization.FUNCTIONAL,
                practice_area=PracticeArea.AUDIT,
                role_title="Partner",
            )
        ]
    )
    service = AggregatorOpenAiService()
    service.client = AsyncMock()  # type: ignore[misc]
    service.client.responses.parse.return_value = SimpleNamespace(
        output_parsed=parsed
    )

    result = await service.execute(
        company_name="Acme", persons=[make_person_input()]
    )

    assert result is parsed
    call = service.client.responses.parse.await_args
    assert call.kwargs["model"] == service.model
    assert call.kwargs["temperature"] == service.temperature
    assert call.kwargs["text_format"] is AiAggregationResult


async def test_raises_when_the_client_returns_no_parsed_result() -> None:
    """Fail loudly when the LLM produced no parsed result."""
    service = AggregatorOpenAiService()
    service.client = AsyncMock()  # type: ignore[misc]
    service.client.responses.parse.return_value = SimpleNamespace(
        output_parsed=None
    )

    with pytest.raises(ValueError, match="no parsed result"):
        await service.execute(
            company_name="Acme", persons=[make_person_input()]
        )
