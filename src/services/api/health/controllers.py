from http import HTTPStatus
from typing import final

from dmr import Controller, modify
from dmr.plugins.pydantic import PydanticSerializer

from services.api.health.schemas import HealthResponse


@final
class HealthController(Controller[PydanticSerializer]):
    """Report that the API is up and serving requests."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Health"])
    async def get(self) -> HealthResponse:
        """Return a liveness marker without touching the database."""
        return HealthResponse(status="ok")
