from typing import final
from uuid import UUID

from apps.common.repository import BaseRepository
from apps.persons.models import Person, PersonMention


@final
class PersonRepository(BaseRepository[Person, UUID]):
    """Persistence operations for persons."""

    model = Person


@final
class PersonMentionRepository(BaseRepository[PersonMention, UUID]):
    """Persistence operations for person mentions."""

    model = PersonMention
