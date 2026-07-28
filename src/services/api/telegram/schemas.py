from datetime import datetime
from math import ceil
from typing import TYPE_CHECKING, Self, final
from uuid import UUID

from services.api.common.schemas import CamelCaseModel

if TYPE_CHECKING:
    from apps.persons.models import Person, PersonMention
    from apps.scans.models import PersonSnapshot, Scan


def _paginate(page: int, page_size: int, total: int) -> dict[str, int | bool]:
    """Return pagination metadata for a page of ``total`` items."""
    total_pages = max(1, ceil(total / page_size)) if page_size else 1
    has_prev = page > 1
    has_next = page < total_pages
    return {
        "page": page,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else page,
        "next_page": page + 1 if has_next else page,
    }


@final
class SourceRefResponse(CamelCaseModel):
    """One source mention shown under a collapsible sources block."""

    title: str
    url: str
    context: str
    mention_type: int
    page_type: int
    published_at: datetime | None

    @classmethod
    def build(cls, mention: PersonMention) -> Self:
        """Assemble a source reference from a person mention instance."""
        return cls(
            title=mention.source.title,
            url=mention.source.url,
            context=mention.context,
            mention_type=mention.mention_type,
            page_type=mention.source.page_type,
            published_at=mention.source.published_timestamp,
        )


@final
class CompanyResponse(CamelCaseModel):
    """Company shown in the scan report header."""

    name: str
    website_url: str
    scan_enabled: bool


@final
class ScanResponse(CamelCaseModel):
    """Scan shown in the report."""

    status: int
    pages_scanned: int
    report: str
    error: str
    created_at: datetime


@final
class PersonSnapshotResponse(CamelCaseModel):
    """One extracted person shown in the report with their sources."""

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
    sources: list[SourceRefResponse]
    sources_count: int

    @classmethod
    def build(
        cls,
        person_snapshot: PersonSnapshot,
        sources: list[PersonMention],
    ) -> Self:
        """Assemble the response from a snapshot and its source mentions."""
        return cls(
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
            sources=[SourceRefResponse.build(mention) for mention in sources],
            sources_count=len(sources),
        )


@final
class CompanyScanResponse(CamelCaseModel):
    """Full company scan report page payload with a page of people."""

    company: CompanyResponse
    scan: ScanResponse
    scan_index: int
    scans_total: int
    person_snapshots: list[PersonSnapshotResponse]
    persons_total: int
    partner_count: int
    director_count: int
    confirmed_count: int
    sources_count: int
    page: int
    total_pages: int
    has_prev: bool
    has_next: bool
    prev_page: int
    next_page: int

    @classmethod
    def build(
        cls,
        scan: Scan,
        scan_index: int,
        scans_total: int,
        person_snapshots: list[PersonSnapshot],
        snapshot_sources: dict[UUID, list[PersonMention]],
        persons_total: int,
        partner_count: int,
        director_count: int,
        confirmed_count: int,
        sources_count: int,
        page: int,
        page_size: int,
    ) -> Self:
        """Assemble the report payload from a page of scan data."""
        return cls(
            company=CompanyResponse.model_validate(scan.company),
            scan=ScanResponse(
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
                    snapshot_sources.get(person_snapshot.person_id, []),
                )
                for person_snapshot in person_snapshots
            ],
            persons_total=persons_total,
            partner_count=partner_count,
            director_count=director_count,
            confirmed_count=confirmed_count,
            sources_count=sources_count,
            **_paginate(page, page_size, persons_total),
        )


@final
class PersonScanEntryResponse(CamelCaseModel):
    """One scan a person appeared in, with that scan's sources."""

    scan_id: str
    company_name: str
    company_website: str
    scanned_at: datetime
    role_title: str
    organizational_unit: str
    position_type: int
    confirmation_level: int
    work_status: int
    specialization: int
    practice_area: int
    email: str
    phone: str
    sources: list[SourceRefResponse]
    sources_count: int

    @classmethod
    def build(
        cls,
        snapshot: PersonSnapshot,
        sources: list[PersonMention],
    ) -> Self:
        """Assemble a scan entry from a snapshot and its source mentions."""
        return cls(
            scan_id=str(snapshot.scan_id),
            company_name=snapshot.scan.company.name,
            company_website=snapshot.scan.company.website_url,
            scanned_at=snapshot.scan.created_timestamp,
            role_title=snapshot.role_title,
            organizational_unit=snapshot.organizational_unit,
            position_type=snapshot.position_type,
            confirmation_level=snapshot.confirmation_level,
            work_status=snapshot.work_status,
            specialization=snapshot.specialization,
            practice_area=snapshot.practice_area,
            email=snapshot.email,
            phone=snapshot.phone,
            sources=[SourceRefResponse.build(mention) for mention in sources],
            sources_count=len(sources),
        )


@final
class PersonReportResponse(CamelCaseModel):
    """Full person report page payload: a page of the person's scans."""

    full_name: str
    scans_total: int
    items: list[PersonScanEntryResponse]
    page: int
    total_pages: int
    has_prev: bool
    has_next: bool
    prev_page: int
    next_page: int

    @classmethod
    def build(
        cls,
        person: Person,
        snapshots: list[PersonSnapshot],
        scan_sources: dict[UUID, list[PersonMention]],
        scans_total: int,
        page: int,
        page_size: int,
    ) -> Self:
        """Assemble the report payload from a page of the person's scans."""
        return cls(
            full_name=person.normalized_name,
            scans_total=scans_total,
            items=[
                PersonScanEntryResponse.build(
                    snapshot,
                    scan_sources.get(snapshot.scan_id, []),
                )
                for snapshot in snapshots
            ],
            **_paginate(page, page_size, scans_total),
        )
