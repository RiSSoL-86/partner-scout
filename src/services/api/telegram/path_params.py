from uuid import UUID

from pydantic import BaseModel


class CompanyScanPathParams(BaseModel):
    """Path parameters identifying a company scan report."""

    scan_id: UUID


class PersonPathParams(BaseModel):
    """Path parameters identifying a person report."""

    person_id: UUID
