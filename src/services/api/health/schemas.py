from typing import final

from services.api.common.schemas import CamelCaseModel


@final
class HealthResponse(CamelCaseModel):
    """Liveness payload confirming the API is reachable."""

    status: str
