from typing import Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository
from apps.scans.repository import ScanRepository


@final
class CompanyScansService(BaseService):
    """Load a page of one company's scans."""

    company_repository = CompanyRepository()
    scan_repository = ScanRepository()

    @override
    async def execute(
        self,
        company_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> dict[str, Any] | None:
        """Return the company, a page of its scans and total, or None."""
        company = await self.company_repository.get(company_id)
        if company is None:
            return None

        scans, total = await self.scan_repository.list(
            filters={"company_id": company_id},
            order_by=("-created_timestamp",),
            offset=offset,
            limit=limit,
        )
        return {
            "company": company,
            "scans": scans,
            "total": total,
        }
