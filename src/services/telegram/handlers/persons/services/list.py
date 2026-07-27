from typing import TYPE_CHECKING, final, override

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository

if TYPE_CHECKING:
    from apps.persons.models import Person


@final
class PersonListService(BaseService):
    """Load a page of all persons for Telegram handlers."""

    person_repository = PersonRepository()

    @override
    async def execute(
        self,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Person], int]:
        """Return a page of persons ordered by name and their total."""
        return await self.person_repository.list(
            order_by=("normalized_name",),
            offset=offset,
            limit=limit,
        )
