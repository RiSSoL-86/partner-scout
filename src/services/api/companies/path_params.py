from uuid import UUID

from pydantic import BaseModel


class CompanyPathParams(BaseModel):
    """Path parameters identifying a company."""

    company_id: UUID
