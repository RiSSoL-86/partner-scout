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
    from apps.scans.models import PersonSnapshot, Scan


@final
class ScanResponse(CamelCaseModel):
    """Full scan payload shown in the scan detail."""

    id: UUID
    status: str
    status_value: int
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
            person_id=person_snapshot.person_id,
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
        """Assemble the detail payload from fetched scan data."""
        return cls(
            company=CompanyResponse.build(scan.company),
            scan=ScanResponse(
                id=scan.id,
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
