from typing import final

from apps.common.repository import BaseRepository
from apps.persons.models import Person


@final
class PersonRepository(BaseRepository[Person, int]):
    """Persistence operations for persons."""

    model = Person
