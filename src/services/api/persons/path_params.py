from uuid import UUID

from pydantic import BaseModel


class PersonPathParams(BaseModel):
    """Path parameters identifying a person."""

    person_id: UUID
