from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository
from apps.scans.repository import ScanRepository

if TYPE_CHECKING:
    from apps.companies.models import Company
    from apps.scans.models import Scan


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
    ) -> tuple[Company, list[Scan], int] | None:
        """Return the company, a page of its scans and the scans total.

        Returns ``None`` when the company does not exist.
        """
        company = await self.company_repository.get(company_id)
        if company is None:
            return None

        scans, total = await self.scan_repository.list(
            filters={"company_id": company_id},
            order_by=("-created_timestamp",),
            offset=offset,
            limit=limit,
        )
        return company, scans, total
