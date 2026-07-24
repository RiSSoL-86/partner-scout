from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.companies.repository import CompanyRepository
from services.api.common.services.base import BaseService

if TYPE_CHECKING:
    from apps.companies.models import Company


@final
class TelegramCompanyDetailService(BaseService):
    """Load one company for the Telegram report page."""

    company_repository = CompanyRepository()

    @override
    async def execute(self, company_id: UUID) -> Company | None:
        """Return one company by id."""
        return await self.company_repository.get(primary_key=company_id)
