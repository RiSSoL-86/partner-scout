from typing import Any, final, override

from django.db.models.functions import Lower

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository


@final
class CompanyListService(BaseService):
    """Load a page of companies filtered by name."""

    company_repository = CompanyRepository()

    @override
    async def execute(
        self,
        search: str = "",
        offset: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Return a page of companies and their total."""
        filters = {"name__icontains": search} if search else None
        companies, total = await self.company_repository.list(
            filters=filters,
            order_by=(Lower("name").asc(),),
            offset=offset,
            limit=limit,
        )
        return {"companies": companies, "total": total}
