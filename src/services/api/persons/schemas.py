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
    from apps.scans.models import PersonSnapshot


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
class TimelineCompanyResponse(CamelCaseModel):
    """Company a person was seen in at one point of the timeline."""

    id: UUID
    name: str
    website_url: str


@final
class TimelineEntryResponse(CamelCaseModel):
    """One dated point of a person's career timeline (one scan)."""

    scan_id: UUID
    date: datetime
    company: TimelineCompanyResponse
    position_type: int
    role_title: str
    organizational_unit: str
    work_status: int
    specialization: int
    practice_area: int
    confirmation_level: int
    email: str
    phone: str
    person_sources_count: int

    @classmethod
    def build(
        cls,
        snapshot: PersonSnapshot,
        person_sources_count: int,
    ) -> Self:
        """Assemble one entry from a snapshot and its scan source count."""
        scan = snapshot.scan
        company = scan.company
        return cls(
            scan_id=scan.id,
            date=scan.created_timestamp,
            company=TimelineCompanyResponse(
                id=company.id,
                name=company.name,
                website_url=company.website_url,
            ),
            position_type=snapshot.position_type,
            role_title=snapshot.role_title,
            organizational_unit=snapshot.organizational_unit,
            work_status=snapshot.work_status,
            specialization=snapshot.specialization,
            practice_area=snapshot.practice_area,
            confirmation_level=snapshot.confirmation_level,
            email=snapshot.email,
            phone=snapshot.phone,
            person_sources_count=person_sources_count,
        )


@final
class PersonTimelineResponse(CamelCaseModel):
    """A person with a paginated page of their career timeline."""

    person: PersonResponse
    items: list[TimelineEntryResponse]
    total: int
    offset: int
    limit: int

    @classmethod
    def build(
        cls,
        person: Person,
        entries: list[tuple[PersonSnapshot, int]],
        total: int,
        offset: int,
        limit: int,
    ) -> Self:
        """Assemble the response from fetched person and timeline data."""
        return cls(
            person=PersonResponse.build(person),
            items=[
                TimelineEntryResponse.build(snapshot, person_sources_count)
                for snapshot, person_sources_count in entries
            ],
            total=total,
            offset=offset,
            limit=limit,
        )
