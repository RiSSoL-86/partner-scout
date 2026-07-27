from datetime import datetime
from typing import TYPE_CHECKING, Self, final

from apps.scans.choices import ConfirmationLevel, PositionType
from services.api.common.schemas import CamelCaseModel

if TYPE_CHECKING:
    from apps.persons.models import Person, PersonMention
    from apps.scans.models import PersonSnapshot, Scan


@final
class CompanyResponse(CamelCaseModel):
    """Company shown in the scan report header."""

    name: str
    website_url: str
    scan_enabled: bool


@final
class ScanResponse(CamelCaseModel):
    """Scan shown in the report."""

    status: str
    status_value: int
    pages_scanned: int
    report: str
    error: str
    created_at: datetime


@final
class PersonSnapshotResponse(CamelCaseModel):
    """One extracted person shown in the report."""

    full_name: str
    role_title: str
    organizational_unit: str
    position_type: str
    position_type_value: int
    work_status: str
    work_status_value: int
    specialization: str
    specialization_value: int
    practice_area: str
    practice_area_value: int
    confirmation_level: str
    confirmation_level_value: int
    email: str
    phone: str

    @classmethod
    def build(cls, person_snapshot: PersonSnapshot) -> Self:
        """Assemble the response from a person snapshot instance."""
        return cls(
            full_name=person_snapshot.person.normalized_name,
            role_title=person_snapshot.role_title,
            organizational_unit=person_snapshot.organizational_unit,
            position_type=str(person_snapshot.get_position_type_display()),
            position_type_value=person_snapshot.position_type,
            work_status=str(person_snapshot.get_work_status_display()),
            work_status_value=person_snapshot.work_status,
            specialization=str(person_snapshot.get_specialization_display()),
            specialization_value=person_snapshot.specialization,
            practice_area=str(person_snapshot.get_practice_area_display()),
            practice_area_value=person_snapshot.practice_area,
            confirmation_level=str(
                person_snapshot.get_confirmation_level_display()
            ),
            confirmation_level_value=person_snapshot.confirmation_level,
            email=person_snapshot.email,
            phone=person_snapshot.phone,
        )


@final
class CompanyScanResponse(CamelCaseModel):
    """Full company scan report page payload."""

    company: CompanyResponse
    scan: ScanResponse
    scan_index: int
    scans_total: int
    person_snapshots: list[PersonSnapshotResponse]
    partner_count: int
    director_count: int
    confirmed_count: int
    sources_count: int

    @classmethod
    def build(
        cls,
        scan: Scan,
        scan_index: int,
        scans_total: int,
        person_snapshots: list[PersonSnapshot],
        sources_count: int,
    ) -> Self:
        """Assemble the report payload from fetched scan data."""
        return cls(
            company=CompanyResponse.model_validate(scan.company),
            scan=ScanResponse(
                status=str(scan.get_status_display()),
                status_value=scan.status,
                pages_scanned=scan.pages_scanned,
                report=scan.report,
                error=scan.error,
                created_at=scan.created_timestamp,
            ),
            scan_index=scan_index,
            scans_total=scans_total,
            person_snapshots=[
                PersonSnapshotResponse.build(person_snapshot)
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
            sources_count=sources_count,
        )


@final
class PersonMentionResponse(CamelCaseModel):
    """One source mention shown in the person report."""

    source_title: str
    source_url: str
    mention_type: str
    mention_type_value: int
    context: str
    seen_at: datetime

    @classmethod
    def build(cls, mention: PersonMention) -> Self:
        """Assemble the response from a person mention instance."""
        return cls(
            source_title=mention.source.title,
            source_url=mention.source.url,
            mention_type=str(mention.get_mention_type_display()),
            mention_type_value=mention.mention_type,
            context=mention.context,
            seen_at=mention.created_timestamp,
        )


@final
class PersonReportResponse(CamelCaseModel):
    """Full person report page payload."""

    full_name: str
    mentions: list[PersonMentionResponse]
    sources_count: int

    @classmethod
    def build(
        cls,
        person: Person,
        mentions: list[PersonMention],
    ) -> Self:
        """Assemble the report payload from fetched person data."""
        return cls(
            full_name=person.normalized_name,
            mentions=[
                PersonMentionResponse.build(mention) for mention in mentions
            ],
            sources_count=len({mention.source_id for mention in mentions}),
        )
