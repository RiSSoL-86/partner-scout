from typing import Any, final, override

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository


@final
class PersonListService(BaseService):
    """Load a page of all persons for Telegram handlers."""

    person_repository = PersonRepository()

    @override
    async def execute(
        self,
        offset: int = 0,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Return a page of persons ordered by name and their total."""
        persons, total = await self.person_repository.list(
            order_by=("normalized_name",),
            offset=offset,
            limit=limit,
        )
        return {"persons": persons, "total": total}
