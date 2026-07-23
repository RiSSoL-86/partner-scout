from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.companies.models import Company


@final
class CompanyRepository(BaseRepository[Company, UUID]):
    """Persistence operations for companies."""

    model = Company
