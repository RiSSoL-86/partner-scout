from typing import final
from uuid import UUID

from pydantic import BaseModel


@final
class CompanyPathParams(BaseModel):
    """Path parameters identifying a company."""

    company_id: UUID
