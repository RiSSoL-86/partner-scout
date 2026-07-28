from typing import final
from uuid import UUID

from pydantic import BaseModel


@final
class PersonPathParams(BaseModel):
    """Path parameters identifying a person."""

    person_id: UUID
