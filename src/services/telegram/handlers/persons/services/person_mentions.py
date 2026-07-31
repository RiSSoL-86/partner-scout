from typing import Any, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.persons.repository import PersonRepository
from apps.scans.repository import PersonSnapshotRepository


@final
class PersonMentionsService(BaseService):
    """Load a person and how many scans they appear in for Telegram."""

    person_repository = PersonRepository()
    person_snapshot_repository = PersonSnapshotRepository()

    @override
    async def execute(
        self,
        person_id: UUID,
    ) -> dict[str, Any]:
        """Return the person and how many scans they appear in."""
        person = await self.person_repository.get(person_id)
        if person is None:
            return {"person": None, "total": 0}

        total = await self.person_snapshot_repository.count(
            filters={"person_id": person_id},
        )
        return {"person": person, "total": total}
