from collections.abc import Sequence
from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.sources.models import Source


@final
class SourceRepository(BaseRepository[Source, UUID]):
    """Persistence operations for sources."""

    model = Source

    async def list_for_person(
        self,
        person_id: UUID,
        order_by: Sequence[str] = ("-created_timestamp",),
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Source], int]:
        """Return a page of distinct sources mentioning the person.

        Sources are deduplicated across every scan the person appears in,
        so the total counts unique source documents, not their mentions.
        """
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")

        queryset = (
            self.model.objects.filter(person_mentions__person_id=person_id)
            .distinct()
            .order_by(*order_by)
        )
        total = await queryset.acount()
        page = [
            instance async for instance in queryset[offset : offset + limit]
        ]
        return page, total
