from http import HTTPStatus
from typing import final

from dmr import Controller, modify
from dmr.plugins.pydantic import PydanticSerializer

from services.api.persons.schemas import PersonChoicesResponse


@final
class PersonChoicesController(Controller[PydanticSerializer]):
    """Return selectable choice values for person mentions."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Persons"])
    async def get(self) -> PersonChoicesResponse:
        """Return the person mention choice values with labels."""
        return PersonChoicesResponse.build()
