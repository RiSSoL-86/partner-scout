from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.scans.models import PersonSnapshot, Scan, ScanSource


@final
class ScanRepository(BaseRepository[Scan, UUID]):
    """Persistence operations for scans."""

    model = Scan


@final
class ScanSourceRepository(BaseRepository[ScanSource, UUID]):
    """Persistence operations for scan-source links."""

    model = ScanSource


@final
class PersonSnapshotRepository(BaseRepository[PersonSnapshot, UUID]):
    """Persistence operations for person snapshots."""

    model = PersonSnapshot
