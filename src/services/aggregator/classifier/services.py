import logging
from typing import TYPE_CHECKING, final, override

from django.conf import settings

from apps.common.services.base import BaseService
from services.aggregator.classifier.open_ai.services import (
    AggregatorOpenAiService,
)
from services.aggregator.classifier.schemas import (
    AiMention,
    AiPersonInput,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from services.aggregator.schemas import (
        AiClassification,
        ScanPersonMentions,
    )

logger = logging.getLogger(__name__)


@final
class ClassifierPersonService(BaseService):
    """Classify a scan's people via the LLM, one bounded batch at a time."""

    aggregator_ai_service = AggregatorOpenAiService()

    @override
    async def execute(
        self,
        company_name: str,
        scan_person_mentions: ScanPersonMentions,
    ) -> dict[str, AiClassification]:
        """Return one classification per person, keyed by person id."""
        batch_size: int = settings.AGGREGATOR_LLM_BATCH_SIZE  # type: ignore[misc]
        person_by_id = scan_person_mentions.person_by_id
        logger.info(
            msg=f"Classifying {len(person_by_id)} person(s) "
            f"in batches of {batch_size}"
        )
        classifications: dict[str, AiClassification] = {}
        for batch in self._iter_batches(scan_person_mentions, batch_size):
            ai_result = await self.aggregator_ai_service.execute(
                company_name=company_name,
                persons=batch,
            )
            for classification in ai_result.persons:
                classifications[classification.person_id] = classification
        return classifications

    @staticmethod
    def _iter_batches(
        scan_person_mentions: ScanPersonMentions,
        batch_size: int,
    ) -> Iterator[list[AiPersonInput]]:
        """Yield the per-person LLM payload in batches of ``batch_size``.

        Streaming keeps each LLM request small so a scan with many people
        cannot exceed the model's context limit in a single call.
        """
        batch: list[AiPersonInput] = []
        mentions_by_person = scan_person_mentions.mentions_by_person
        for person_id, mentions in mentions_by_person.items():
            person = scan_person_mentions.person_by_id.get(person_id)
            if person is None:
                continue
            batch.append(
                AiPersonInput(
                    person_id=str(person_id),
                    full_name=person.normalized_name,
                    mentions=[
                        AiMention(
                            role_title=mention.role_title,
                            mention_type=mention.mention_type,
                            source_title=mention.source.title,
                        )
                        for mention in mentions
                    ],
                )
            )
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
