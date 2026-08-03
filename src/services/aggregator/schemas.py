from typing import final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from apps.persons.models import Person, PersonMention
from apps.scans.choices import (
    PositionType,
    PracticeArea,
    Specialization,
    WorkStatus,
)


@final
class ScanPersonMentions(BaseModel):
    """A scan's people paired with their mentions, grouped per person."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    person_by_id: dict[UUID, Person]
    mentions_by_person: dict[UUID, list[PersonMention]]

    def __bool__(self) -> bool:
        """Report whether the scan mentioned anyone at all."""
        return bool(self.mentions_by_person)


@final
class AiClassification(BaseModel):
    """The LLM verdict for one person, mapped onto snapshot fields."""

    person_id: str = Field(
        description="Same identifier as in the matching input person.",
    )
    position_type: PositionType = Field(
        description="Partner-level position: 0 partner, 1 director.",
    )
    work_status: WorkStatus = Field(
        description="Employment state: 0 unknown, 1 front line, "
        "2 back office.",
    )
    specialization: Specialization = Field(
        description="Specialization: 0 unknown, 1 industrial, 2 functional.",
    )
    practice_area: PracticeArea = Field(
        description=(
            "Practice area: 0 unknown, 1 audit, 2 tax and legal, "
            "3 consulting and deals."
        ),
    )
    role_title: str = Field(
        description="Best single job title for the person across sources.",
    )
    organizational_unit: str = Field(
        default="",
        description="Department or practice unit, empty when unknown.",
    )


@final
class AiAggregationResult(BaseModel):
    """The full LLM response covering every person in the scan."""

    persons: list[AiClassification] = Field(
        default_factory=list,
        description="One classification per input person.",
    )
