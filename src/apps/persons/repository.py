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

    async def list_by_surname_initial(
        self,
        initial: str,
        offset: int = 0,
        limit: int = 5,
    ) -> tuple[list[Person], int]:
        """Return a page of persons by surname initial and their total."""
        queryset = self.model.objects.filter(
            normalized_name__istartswith=initial,
        )
        total = await queryset.acount()
        ordered = queryset.order_by("normalized_name")
        page = [person async for person in ordered[offset : offset + limit]]
        return page, total


@final
class PersonMentionRepository(BaseRepository[PersonMention, UUID]):
    """Persistence operations for person mentions."""

    model = PersonMention

    async def list_for_person(
        self,
        person_id: UUID,
        offset: int = 0,
        limit: int = 5,
    ) -> tuple[list[PersonMention], int]:
        """Return a newest-first page of person mentions and their total."""
        queryset = self.model.objects.filter(person_id=person_id)
        total = await queryset.acount()
        ordered = queryset.select_related("source").order_by(
            "-created_timestamp",
        )
        page = [mention async for mention in ordered[offset : offset + limit]]
        return page, total
