from http import HTTPStatus
from typing import final

from dmr import Controller, modify
from dmr.plugins.pydantic import PydanticSerializer

from services.api.sources.schemas import SourceChoicesResponse


@final
class SourceChoicesController(Controller[PydanticSerializer]):
    """Return selectable choice values for sources."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Sources"])
    async def get(self) -> SourceChoicesResponse:
        """Return the source choice values with labels."""
        return SourceChoicesResponse.build()
