from collections.abc import Mapping, Sequence
from typing import final, override
from uuid import UUID

from django.db import IntegrityError
from django.db.models import Count
from django.db.models.functions import Substr, Upper

from apps.common.repository import BaseRepository
from apps.persons.models import Person, PersonMention


@final
class PersonRepository(BaseRepository[Person, UUID]):
    """Persistence operations for persons."""

    model = Person

    @override
    async def get_or_create(
        self,
        filters: Mapping[str, object],
        instance: Person,
    ) -> Person:
        """Resolve the person by name identity, creating or enriching it."""
        key = Person.build_identity_key(
            first_name=instance.first_name, last_name=instance.last_name
        )
        middle = instance.middle_name.strip()
        candidates = await self.list_all(
            filters={"identity_key": key},
            order_by=("created_timestamp",),
        )

        if middle:
            for candidate in candidates:
                if (
                    candidate.middle_name.strip().casefold()
                    == middle.casefold()
                ):
                    return candidate
            for candidate in candidates:
                if not candidate.middle_name.strip():
                    return await self._enrich_name(
                        person=candidate, instance=instance
                    )
        elif candidates:
            return candidates[0]

        try:
            return await self.create(instance)
        except IntegrityError:
            # A concurrent page created this identity first; re-resolve.
            return await self.get_or_create(filters=filters, instance=instance)

    async def _enrich_name(self, person: Person, instance: Person) -> Person:
        """Adopt the more complete name variant onto an existing record."""
        person.first_name = instance.first_name
        person.middle_name = instance.middle_name
        person.last_name = instance.last_name
        try:
            await person.asave(
                update_fields=(
                    "first_name",
                    "middle_name",
                    "last_name",
                    "updated_timestamp",
                ),
            )
        except IntegrityError:
            # A concurrent writer already crystallized this patronymic.
            return await self.get_or_create(filters={}, instance=instance)
        return person

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

    async def count_by_person_for_scan(
        self,
        scan_id: UUID,
    ) -> dict[UUID, int]:
        """Return per-person mention counts found within one scan."""
        rows = (
            self.model.objects.filter(scan_id=scan_id)
            .values("person_id")
            .annotate(total=Count("pk"))
        )
        return {row["person_id"]: row["total"] async for row in rows}

    async def count_by_scan_for_person(
        self,
        person_id: UUID,
        scan_ids: Sequence[UUID],
    ) -> dict[UUID, int]:
        """Return per-scan mention counts for one person across scans."""
        rows = (
            self.model.objects.filter(
                person_id=person_id,
                scan_id__in=list(scan_ids),
            )
            .values("scan_id")
            .annotate(total=Count("pk"))
        )
        return {row["scan_id"]: row["total"] async for row in rows}

    async def list_by_persons_for_scan(
        self,
        scan_id: UUID,
        person_ids: Sequence[UUID],
    ) -> dict[UUID, list[PersonMention]]:
        """Group a scan's person mentions by person for the given people."""
        rows = (
            self.model.objects.filter(
                scan_id=scan_id,
                person_id__in=list(person_ids),
            )
            .select_related("source")
            .order_by("mention_type", "source__title")
        )
        grouped: dict[UUID, list[PersonMention]] = {}
        async for mention in rows:
            grouped.setdefault(mention.person_id, []).append(mention)
        return grouped

    async def list_by_scans_for_person(
        self,
        person_id: UUID,
        scan_ids: Sequence[UUID],
    ) -> dict[UUID, list[PersonMention]]:
        """Group a person's mentions by scan across the given scans."""
        rows = (
            self.model.objects.filter(
                person_id=person_id,
                scan_id__in=list(scan_ids),
            )
            .select_related("source")
            .order_by("mention_type", "source__title")
        )
        grouped: dict[UUID, list[PersonMention]] = {}
        async for mention in rows:
            grouped.setdefault(mention.scan_id, []).append(mention)
        return grouped
