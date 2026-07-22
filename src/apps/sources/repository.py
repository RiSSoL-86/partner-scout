from typing import final

from apps.common.repository import BaseRepository
from apps.sources.models import Source


@final
class SourceRepository(BaseRepository[Source, int]):
    """Persistence operations for sources."""

    model = Source
