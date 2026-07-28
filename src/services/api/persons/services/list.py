from typing import Any, final, override

from django.db.models.functions import Lower

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository


@final
class PersonListService(BaseService):
    """Load a page of persons filtered by name."""

    person_repository = PersonRepository()

    @override
    async def execute(
        self,
        search: str = "",
        offset: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Return a page of persons and their total."""
        filters = {"normalized_name__icontains": search} if search else None
        persons, total = await self.person_repository.list(
            filters=filters,
            order_by=(Lower("normalized_name").asc(),),
            offset=offset,
            limit=limit,
        )
        return {"persons": persons, "total": total}
