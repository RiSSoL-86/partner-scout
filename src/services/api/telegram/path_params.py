from uuid import UUID

from pydantic import BaseModel


class TelegramCompanyPathParams(BaseModel):
    """Path parameters identifying a company report."""

    company_id: UUID


class TelegramPersonPathParams(BaseModel):
    """Path parameters identifying a person report."""

    person_id: UUID
