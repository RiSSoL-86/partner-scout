from typing import final

from pydantic import BaseModel, Field

from apps.persons.choices import MentionType
from apps.sources.choices import PageType


@final
class ExtractedPerson(BaseModel):
    """One partner or director the gate LLM found on a page."""

    first_name: str = Field(description="Person given name.")
    middle_name: str = Field(
        default="",
        description="Person middle name or patronymic, empty if absent.",
    )
    last_name: str = Field(description="Person family name.")
    mention_type: MentionType = Field(
        description=(
            "How the person appears on this page: 0 personal profile, "
            "1 organizational-unit listing, 2 otherwise."
        ),
    )
    context: str = Field(
        description="Short quote from the page justifying the person.",
    )


@final
class PageExtraction(BaseModel):
    """Gate LLM verdict for a single crawled page."""

    is_relevant: bool = Field(
        description="True only for a partner or director of this firm.",
    )
    page_type: PageType = Field(
        description="Recognized page type code for this page.",
    )
    persons: list[ExtractedPerson] = Field(
        default_factory=list,
        description="Relevant persons, empty when not relevant.",
    )


@final
class CrawledPage(BaseModel):
    """One fetched page paired with its gate verdict."""

    url: str
    title: str
    content: str
    extraction: PageExtraction
