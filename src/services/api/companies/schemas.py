from datetime import datetime
from typing import TYPE_CHECKING, Self, final
from uuid import UUID

from pydantic import BaseModel, Field

from services.api.common.schemas import CamelCaseModel

if TYPE_CHECKING:
    from apps.companies.models import Company
    from apps.scans.models import Scan


@final
class CompanyListQuery(BaseModel):
    """Query parameters for the paginated company list."""

    search: str = ""
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


@final
class PageQuery(BaseModel):
    """Query parameters for a generic paginated list."""

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


@final
class CompanyResponse(CamelCaseModel):
    """Single company payload."""

    id: UUID
    name: str
    website_url: str
    scan_enabled: bool
    last_scanned_at: datetime | None
    created_at: datetime

    @classmethod
    def build(cls, company: Company) -> Self:
        """Assemble the response from a company instance."""
        return cls(
            id=company.id,
            name=company.name,
            website_url=company.website_url,
            scan_enabled=company.scan_enabled,
            last_scanned_at=company.last_scanned_at,
            created_at=company.created_timestamp,
        )


@final
class CompanyListResponse(CamelCaseModel):
    """Paginated page of companies."""

    items: list[CompanyResponse]
    total: int
    offset: int
    limit: int


@final
class ScanSummaryResponse(CamelCaseModel):
    """Scan shown in a company's scan list."""

    id: UUID
    status: str
    status_value: int
    pages_scanned: int
    has_error: bool
    created_at: datetime

    @classmethod
    def build(cls, scan: Scan) -> Self:
        """Assemble the summary from a scan instance."""
        return cls(
            id=scan.id,
            status=str(scan.get_status_display()),
            status_value=scan.status,
            pages_scanned=scan.pages_scanned,
            has_error=bool(scan.error),
            created_at=scan.created_timestamp,
        )


@final
class CompanyScansResponse(CamelCaseModel):
    """Paginated page of a company's scans with the company header."""

    company: CompanyResponse
    items: list[ScanSummaryResponse]
    total: int
    offset: int
    limit: int

    @classmethod
    def build(
        cls,
        company: Company,
        scans: list[Scan],
        total: int,
        offset: int,
        limit: int,
    ) -> Self:
        """Assemble the response from fetched company and scan data."""
        return cls(
            company=CompanyResponse.build(company),
            items=[ScanSummaryResponse.build(scan) for scan in scans],
            total=total,
            offset=offset,
            limit=limit,
        )
