from typing import final
from uuid import UUID

from pydantic import BaseModel


@final
class CompanyScanPathParams(BaseModel):
    """Path parameters identifying a company scan report."""

    scan_id: UUID


@final
class PersonPathParams(BaseModel):
    """Path parameters identifying a person report."""

    person_id: UUID
