from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository
from apps.sources.repository import SourceRepository

if TYPE_CHECKING:
    from apps.persons.models import Person
    from apps.sources.models import Source


@final
class PersonSourcesService(BaseService):
    """Load a page of every source known for one person."""

    person_repository = PersonRepository()
    source_repository = SourceRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Person, list[Source], int] | None:
        """Return the person, a page of their sources and the total.

        Sources are collected across every scan and deduplicated, so the
        result is independent of any single scan. Returns ``None`` when
        the person does not exist.
        """
        person = await self.person_repository.get(person_id)
        if person is None:
            return None

        sources, total = await self.source_repository.list_for_person(
            person_id=person_id,
            order_by=("-created_timestamp",),
            offset=offset,
            limit=limit,
        )
        return person, sources, total
