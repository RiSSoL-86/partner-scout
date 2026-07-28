from datetime import datetime
from typing import TYPE_CHECKING, Self, final
from uuid import UUID

from apps.scans.choices import (
    ConfirmationLevel,
    PositionType,
    PracticeArea,
    ScanStatus,
    Specialization,
    WorkStatus,
)
from services.api.common.schemas import (
    CamelCaseModel,
    ChoiceOption,
    build_choice_options,
)
from services.api.companies.schemas import CompanyResponse

if TYPE_CHECKING:
    from apps.persons.models import PersonMention
    from apps.scans.models import PersonSnapshot, Scan


@final
class ScanResponse(CamelCaseModel):
    """Full scan payload shown in the scan detail."""

    id: UUID
    status: int
    pages_scanned: int
    report: str
    error: str
    created_at: datetime


@final
class PersonSnapshotResponse(CamelCaseModel):
    """One extracted person shown in the scan detail."""

    person_id: UUID
    full_name: str
    role_title: str
    organizational_unit: str
    position_type: int
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
        person_snapshot: PersonSnapshot,
        person_sources_count: int = 0,
    ) -> Self:
        """Assemble the response from a person snapshot instance."""
        return cls(
            person_id=person_snapshot.person_id,
            full_name=person_snapshot.person.normalized_name,
            role_title=person_snapshot.role_title,
            organizational_unit=person_snapshot.organizational_unit,
            position_type=person_snapshot.position_type,
            work_status=person_snapshot.work_status,
            specialization=person_snapshot.specialization,
            practice_area=person_snapshot.practice_area,
            confirmation_level=person_snapshot.confirmation_level,
            email=person_snapshot.email,
            phone=person_snapshot.phone,
            person_sources_count=person_sources_count,
        )


@final
class ScanDetailResponse(CamelCaseModel):
    """Full company scan detail payload."""

    company: CompanyResponse
    scan: ScanResponse
    scan_index: int
    scans_total: int
    person_snapshots: list[PersonSnapshotResponse]
    partner_count: int
    director_count: int
    confirmed_count: int
    total_sources_count: int

    @classmethod
    def build(
        cls,
        scan: Scan,
        scan_index: int,
        scans_total: int,
        person_snapshots: list[PersonSnapshot],
        total_sources_count: int,
        person_source_counts: dict[UUID, int],
    ) -> Self:
        """Assemble the detail payload from fetched scan data."""
        return cls(
            company=CompanyResponse.build(scan.company),
            scan=ScanResponse(
                id=scan.id,
                status=scan.status,
                pages_scanned=scan.pages_scanned,
                report=scan.report,
                error=scan.error,
                created_at=scan.created_timestamp,
            ),
            scan_index=scan_index,
            scans_total=scans_total,
            person_snapshots=[
                PersonSnapshotResponse.build(
                    person_snapshot,
                    person_sources_count=person_source_counts.get(
                        person_snapshot.person_id,
                        0,
                    ),
                )
                for person_snapshot in person_snapshots
            ],
            partner_count=sum(
                1
                for person_snapshot in person_snapshots
                if person_snapshot.position_type == PositionType.PARTNER
            ),
            director_count=sum(
                1
                for person_snapshot in person_snapshots
                if person_snapshot.position_type == PositionType.DIRECTOR
            ),
            confirmed_count=sum(
                1
                for person_snapshot in person_snapshots
                if person_snapshot.confirmation_level
                == ConfirmationLevel.CONFIRMED
            ),
            total_sources_count=total_sources_count,
        )


@final
class SourceRefResponse(CamelCaseModel):
    """Source metadata shown for one mention in a scan."""

    id: UUID
    url: str
    title: str
    page_type: int
    published_at: datetime | None


@final
class PersonMentionResponse(CamelCaseModel):
    """One source where the scan mentioned the person."""

    id: UUID
    mention_type: int
    context: str
    source: SourceRefResponse

    @classmethod
    def build(cls, person_mention: PersonMention) -> Self:
        """Assemble the response from a person mention instance."""
        source = person_mention.source
        return cls(
            id=person_mention.id,
            mention_type=person_mention.mention_type,
            context=person_mention.context,
            source=SourceRefResponse(
                id=source.id,
                url=source.url,
                title=source.title,
                page_type=source.page_type,
                published_at=source.published_timestamp,
            ),
        )


@final
class ScanPersonDetailResponse(CamelCaseModel):
    """One person seen through a single scan with its source mentions."""

    company: CompanyResponse
    scan: ScanResponse
    person_snapshot: PersonSnapshotResponse
    mentions: list[PersonMentionResponse]
    mentions_count: int

    @classmethod
    def build(
        cls,
        person_snapshot: PersonSnapshot,
        person_mentions: list[PersonMention],
    ) -> Self:
        """Assemble the payload from the snapshot and its mentions."""
        scan = person_snapshot.scan
        return cls(
            company=CompanyResponse.build(scan.company),
            scan=ScanResponse(
                id=scan.id,
                status=scan.status,
                pages_scanned=scan.pages_scanned,
                report=scan.report,
                error=scan.error,
                created_at=scan.created_timestamp,
            ),
            person_snapshot=PersonSnapshotResponse.build(
                person_snapshot,
                person_sources_count=len(person_mentions),
            ),
            mentions=[
                PersonMentionResponse.build(person_mention)
                for person_mention in person_mentions
            ],
            mentions_count=len(person_mentions),
        )


@final
class ScanChoices(CamelCaseModel):
    """Choice fields of the scan entity."""

    status: list[ChoiceOption]


@final
class PersonSnapshotChoices(CamelCaseModel):
    """Choice fields of the person snapshot entity."""

    position_type: list[ChoiceOption]
    work_status: list[ChoiceOption]
    specialization: list[ChoiceOption]
    practice_area: list[ChoiceOption]
    confirmation_level: list[ChoiceOption]


@final
class ScanChoicesResponse(CamelCaseModel):
    """Selectable choice values for the scan and its snapshots."""

    scan: ScanChoices
    person_snapshot: PersonSnapshotChoices

    @classmethod
    def build(cls) -> Self:
        """Assemble the scan-related choice values from the enums."""
        return cls(
            scan=ScanChoices(
                status=build_choice_options(ScanStatus),
            ),
            person_snapshot=PersonSnapshotChoices(
                position_type=build_choice_options(PositionType),
                work_status=build_choice_options(WorkStatus),
                specialization=build_choice_options(Specialization),
                practice_area=build_choice_options(PracticeArea),
                confirmation_level=build_choice_options(ConfirmationLevel),
            ),
        )
