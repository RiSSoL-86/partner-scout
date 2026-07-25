from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository
from apps.scans.repository import ScanRepository

if TYPE_CHECKING:
    from apps.companies.models import Company
    from apps.scans.models import Scan


@final
class CompanyScanService(BaseService):
    """Load one company scan by position for Telegram handlers."""

    company_repository = CompanyRepository()
    scan_repository = ScanRepository()

    @override
    async def execute(
        self,
        company_id: UUID,
        scan_index: int,
    ) -> tuple[Company | None, Scan | None, int, int]:
        """Return the company, its scan at the position, index and total."""
        (
            scan,
            scan_index,
            scans_total,
        ) = await self.scan_repository.get_by_position(
            company_id=company_id,
            scan_index=scan_index,
        )
        if scan is not None:
            return scan.company, scan, scan_index, scans_total

        company = await self.company_repository.get(company_id)
        return company, None, scan_index, scans_total
