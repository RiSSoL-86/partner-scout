from typing import TYPE_CHECKING, final, override

from django.db.models.functions import Lower

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository

if TYPE_CHECKING:
    from apps.companies.models import Company


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
    ) -> tuple[list[Company], int]:
        """Return a page of companies and their total."""
        filters = {"name__icontains": search} if search else None
        return await self.company_repository.list(
            filters=filters,
            order_by=(Lower("name").asc(),),
            offset=offset,
            limit=limit,
        )
