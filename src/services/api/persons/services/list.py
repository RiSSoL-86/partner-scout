from typing import TYPE_CHECKING, final, override

from django.db.models.functions import Lower

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository

if TYPE_CHECKING:
    from apps.persons.models import Person


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
    ) -> tuple[list[Person], int]:
        """Return a page of persons and their total."""
        filters = {"normalized_name__icontains": search} if search else None
        return await self.person_repository.list(
            filters=filters,
            order_by=(Lower("normalized_name").asc(),),
            offset=offset,
            limit=limit,
        )
