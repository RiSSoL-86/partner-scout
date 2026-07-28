from typing import final
from uuid import UUID

from django.db.models import Count
from django.db.models.functions import Substr, Upper

from apps.common.repository import BaseRepository
from apps.persons.models import Person, PersonMention


@final
class PersonRepository(BaseRepository[Person, UUID]):
    """Persistence operations for persons."""

    model = Person

    async def list_surname_initials(self) -> list[tuple[str, int]]:
        """Return surname initials with their person counts, ordered."""
        rows = (
            self.model.objects.annotate(
                initial=Upper(Substr("normalized_name", 1, 1)),
            )
            .values("initial")
            .annotate(total=Count("pk"))
            .order_by("initial")
        )
        return [(row["initial"], row["total"]) async for row in rows]


@final
class PersonMentionRepository(BaseRepository[PersonMention, UUID]):
    """Persistence operations for person mentions."""

    model = PersonMention

    async def count_sources_by_person_for_scan(
        self,
        scan_id: UUID,
    ) -> dict[UUID, int]:
        """Return per-person source counts found within one scan."""
        rows = (
            self.model.objects.filter(scan_id=scan_id)
            .values("person_id")
            .annotate(total=Count("pk"))
        )
        return {row["person_id"]: row["total"] async for row in rows}
