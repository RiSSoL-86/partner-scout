from datetime import datetime
from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.companies.models import Company


@final
class CompanyRepository(BaseRepository[Company, UUID]):
    """Persistence operations for companies."""

    model = Company

    @staticmethod
    async def set_last_scanned_at(
        company: Company,
        last_scanned_at: datetime,
    ) -> Company:
        """Persist the moment the company was last successfully scanned."""
        company.last_scanned_at = last_scanned_at
        await company.asave(
            update_fields=("last_scanned_at", "updated_timestamp"),
        )
        return company
