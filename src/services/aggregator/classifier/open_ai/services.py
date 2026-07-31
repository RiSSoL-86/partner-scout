import json
import logging
from typing import TYPE_CHECKING, final, override

from django.conf import settings
from openai import AsyncOpenAI

from apps.common.services.base import BaseService
from services.aggregator.classifier.open_ai.prompt import (
    build_aggregate_prompt,
)
from services.aggregator.schemas import AiAggregationResult

if TYPE_CHECKING:
    from services.aggregator.classifier.schemas import (
        AiPersonInput,
    )

logger = logging.getLogger(__name__)


@final
class AggregatorOpenAiService(BaseService):
    """Classify a scan's people with one structured LLM call."""

    def __init__(self) -> None:
        """Build the OpenAI client from project settings."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,  # type: ignore[misc]
        )
        self.model: str = settings.AGGREGATOR_LLM_MODEL  # type: ignore[misc]
        self.temperature: float = (
            settings.AGGREGATOR_LLM_TEMPERATURE  # type: ignore[misc]
        )

    @override
    async def execute(
        self,
        company_name: str,
        persons: list[AiPersonInput],
    ) -> AiAggregationResult:
        """Return one classification per supplied person."""
        payload = json.dumps(
            [person.model_dump() for person in persons],
            ensure_ascii=False,
        )
        response = await self.client.responses.parse(
            model=self.model,
            temperature=self.temperature,
            input=[
                {
                    "role": "system",
                    "content": build_aggregate_prompt(company_name),
                },
                {"role": "user", "content": payload},
            ],
            text_format=AiAggregationResult,
        )
        result = response.output_parsed
        if result is None:
            raise ValueError("Aggregator LLM returned no parsed result")
        return result
