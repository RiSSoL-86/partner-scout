from typing import TYPE_CHECKING, final, override

from apps.companies.repository import CompanyRepository
from services.telegram.handlers.common.services.base import BaseTelegramService

if TYPE_CHECKING:
    from apps.companies.models import Company


@final
class CompanyListTelegramService(BaseTelegramService):
    """Load companies for Telegram handlers."""

    company_repository = CompanyRepository()

    @override
    async def execute(self) -> list[Company]:
        """Return a page of companies."""
        return await self.company_repository.list()
