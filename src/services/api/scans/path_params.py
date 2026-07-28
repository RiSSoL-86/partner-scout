from typing import final
from uuid import UUID

from pydantic import BaseModel


@final
class ScanPathParams(BaseModel):
    """Path parameters identifying a scan."""

    scan_id: UUID


@final
class ScanPersonPathParams(BaseModel):
    """Path parameters identifying a person within a scan."""

    scan_id: UUID
    person_id: UUID
