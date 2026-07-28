from typing import Any, final, override

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository


@final
class CompanyListService(BaseService):
    """Load companies for Telegram handlers."""

    company_repository = CompanyRepository()

    @override
    async def execute(
        self,
        offset: int = 0,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Return a page of companies and their total."""
        companies, total = await self.company_repository.list(
            order_by=("name",),
            offset=offset,
            limit=limit,
        )
        return {"companies": companies, "total": total}
