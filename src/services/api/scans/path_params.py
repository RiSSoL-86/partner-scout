from uuid import UUID

from pydantic import BaseModel


class ScanPathParams(BaseModel):
    """Path parameters identifying a scan."""

    scan_id: UUID


class ScanPersonPathParams(BaseModel):
    """Path parameters identifying a person within a scan."""

    scan_id: UUID
    person_id: UUID
