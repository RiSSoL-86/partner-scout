from typing import final

from apps.common.repository import BaseRepository
from apps.scans.models import Scan


@final
class ScanRepository(BaseRepository[Scan, int]):
    """Persistence operations for scans."""

    model = Scan
