from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.sources.models import Source


@final
class SourceRepository(BaseRepository[Source, UUID]):
    """Persistence operations for sources."""

    model = Source
