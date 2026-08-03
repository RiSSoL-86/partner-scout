import logging
from typing import TYPE_CHECKING, final, override

from apps.common.services.base import BaseService
from apps.scans.models import PersonSnapshot, Scan
from services.aggregator.builder.utils import compute_confirmation_level

if TYPE_CHECKING:
    from collections.abc import Sequence

    from apps.persons.models import PersonMention
    from services.aggregator.schemas import (
        AiClassification,
        ScanPersonMentions,
    )

logger = logging.getLogger(__name__)


@final
class BuilderPersonSnapshotService(BaseService):
    """Merge LLM verdicts, deterministic rules and contacts into snapshots."""

    @override
    async def execute(
        self,
        scan: Scan,
        scan_person_mentions: ScanPersonMentions,
        classifications: dict[str, AiClassification],
    ) -> list[PersonSnapshot]:
        """Build one snapshot per person the LLM classified."""
        snapshots: list[PersonSnapshot] = []
        mentions_by_person = scan_person_mentions.mentions_by_person
        for person_id, mentions in mentions_by_person.items():
            person = scan_person_mentions.person_by_id.get(person_id)
            classification = classifications.get(str(person_id))
            if person is None or classification is None:
                logger.warning(
                    msg=f"No classification for person {person_id}; skipping"
                )
                continue

            email, phone = self._pick_contacts(mentions)
            snapshots.append(
                PersonSnapshot(
                    scan=scan,
                    person=person,
                    position_type=classification.position_type,
                    work_status=classification.work_status,
                    specialization=classification.specialization,
                    practice_area=classification.practice_area,
                    role_title=classification.role_title,
                    organizational_unit=classification.organizational_unit,
                    email=email,
                    phone=phone,
                    confirmation_level=compute_confirmation_level(mentions),
                )
            )
        return snapshots

    @staticmethod
    def _pick_contacts(mentions: Sequence[PersonMention]) -> tuple[str, str]:
        """Take the first non-empty email and phone across the mentions."""
        email = next(
            (m.email for m in mentions if m.email.strip()),
            "",
        )
        phone = next(
            (m.phone for m in mentions if m.phone.strip()),
            "",
        )
        return email, phone
