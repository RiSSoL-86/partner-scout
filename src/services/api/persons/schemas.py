from datetime import datetime
from typing import TYPE_CHECKING, Self, final
from uuid import UUID

from pydantic import BaseModel, Field

from apps.persons.choices import MentionType
from services.api.common.schemas import (
    CamelCaseModel,
    ChoiceOption,
    build_choice_options,
)

if TYPE_CHECKING:
    from apps.persons.models import Person
    from apps.sources.models import Source


@final
class PersonMentionChoices(CamelCaseModel):
    """Choice fields of the person mention entity."""

    mention_type: list[ChoiceOption]


@final
class PersonChoicesResponse(CamelCaseModel):
    """Selectable choice values for person mentions."""

    person_mention: PersonMentionChoices

    @classmethod
    def build(cls) -> Self:
        """Assemble the person-related choice values from the enums."""
        return cls(
            person_mention=PersonMentionChoices(
                mention_type=build_choice_options(MentionType),
            ),
        )


@final
class PersonListQuery(BaseModel):
    """Query parameters for the paginated person list."""

    search: str = ""
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


@final
class PageQuery(BaseModel):
    """Query parameters for a generic paginated list."""

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


@final
class PersonResponse(CamelCaseModel):
    """Single person payload."""

    id: UUID
    full_name: str
    first_name: str
    middle_name: str
    last_name: str
    created_at: datetime

    @classmethod
    def build(cls, person: Person) -> Self:
        """Assemble the response from a person instance."""
        return cls(
            id=person.id,
            full_name=person.normalized_name,
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            created_at=person.created_timestamp,
        )


@final
class PersonListResponse(CamelCaseModel):
    """Paginated page of persons."""

    items: list[PersonResponse]
    total: int
    offset: int
    limit: int


@final
class PersonSourceResponse(CamelCaseModel):
    """One source document known for the person."""

    id: UUID
    url: str
    title: str
    page_type: str
    page_type_value: int
    published_at: datetime | None
    created_at: datetime

    @classmethod
    def build(cls, source: Source) -> Self:
        """Assemble the response from a source instance."""
        return cls(
            id=source.id,
            url=source.url,
            title=source.title,
            page_type=str(source.get_page_type_display()),
            page_type_value=source.page_type,
            published_at=source.published_timestamp,
            created_at=source.created_timestamp,
        )


@final
class PersonSourcesResponse(CamelCaseModel):
    """A person with a paginated page of all their known sources."""

    person: PersonResponse
    items: list[PersonSourceResponse]
    total: int
    offset: int
    limit: int

    @classmethod
    def build(
        cls,
        person: Person,
        sources: list[Source],
        total: int,
        offset: int,
        limit: int,
    ) -> Self:
        """Assemble the response from fetched person and source data."""
        return cls(
            person=PersonResponse.build(person),
            items=[PersonSourceResponse.build(source) for source in sources],
            total=total,
            offset=offset,
            limit=limit,
        )
