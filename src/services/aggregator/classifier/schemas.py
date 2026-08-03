from typing import final

from pydantic import BaseModel, Field

from apps.persons.choices import MentionType


@final
class AiMention(BaseModel):
    """One source mention handed to the LLM for a single person."""

    role_title: str = Field(
        description="Job title copied verbatim from the source.",
    )
    mention_type: MentionType = Field(
        description=(
            "How the person appears in the source: 0 personal profile, "
            "1 organizational-unit listing, 2 otherwise."
        ),
    )
    source_title: str = Field(description="Title of the source page.")


@final
class AiPersonInput(BaseModel):
    """All evidence for one person collected within a single scan."""

    person_id: str = Field(
        description="Opaque identifier echoed back verbatim in the result.",
    )
    full_name: str = Field(description="Person full name as normalized.")
    mentions: list[AiMention] = Field(
        description="Every source mention of this person in the scan.",
    )
