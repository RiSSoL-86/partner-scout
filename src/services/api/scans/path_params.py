from uuid import UUID

from pydantic import BaseModel


class ScanPathParams(BaseModel):
    """Path parameters identifying a scan."""

    scan_id: UUID
