from typing import final

from apps.common.repository import BaseRepository
from apps.companies.models import Company


@final
class CompanyRepository(BaseRepository[Company, int]):
    """Persistence operations for companies."""

    model = Company
