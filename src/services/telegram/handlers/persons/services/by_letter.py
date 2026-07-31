from typing import Any, final, override

from django.db.models.functions import Lower

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository


@final
class PersonByLetterListService(BaseService):
    """Load a page of persons by surname initial for Telegram handlers."""

    person_repository = PersonRepository()

    @override
    async def execute(
        self,
        letter: str,
        offset: int = 0,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Return a page of persons by surname initial and their total."""
        persons, total = await self.person_repository.list(
            filters={"normalized_name__istartswith": letter},
            order_by=(Lower("normalized_name").asc(),),
            offset=offset,
            limit=limit,
        )
        return {"persons": persons, "total": total}
