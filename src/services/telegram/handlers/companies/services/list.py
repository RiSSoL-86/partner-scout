from typing import TYPE_CHECKING, final, override

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository

if TYPE_CHECKING:
    from apps.companies.models import Company


@final
class CompanyListService(BaseService):
    """Load companies for Telegram handlers."""

    company_repository = CompanyRepository()

    @override
    async def execute(
        self,
        offset: int = 0,
        limit: int = 5,
    ) -> tuple[list[Company], int]:
        """Return a page of companies and their total."""
        return await self.company_repository.list(
            order_by=("name",),
            offset=offset,
            limit=limit,
        )
