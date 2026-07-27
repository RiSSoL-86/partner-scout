from http import HTTPStatus
from typing import final

from dmr import Controller, Path, ResponseSpec, modify
from dmr.errors import ErrorModel
from dmr.plugins.pydantic import PydanticSerializer

from services.api.scans.exceptions import ScanNotFoundError
from services.api.scans.path_params import ScanPathParams
from services.api.scans.schemas import ScanChoicesResponse, ScanDetailResponse
from services.api.scans.services.detail import ScanDetailService


@final
class ScanDetailController(Controller[PydanticSerializer]):
    """Return one scan with its person snapshots."""

    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Scans"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.NOT_FOUND),
        ],
    )
    async def get(
        self,
        parsed_path: Path[ScanPathParams],
    ) -> ScanDetailResponse:
        """Return the scan detail or a 404 error when it does not exist."""
        service = ScanDetailService()
        result = await service.execute(scan_id=parsed_path.scan_id)
        if result is None:
            raise ScanNotFoundError

        (
            scan,
            scan_index,
            scans_total,
            person_snapshots,
            sources_count,
        ) = result
        return ScanDetailResponse.build(
            scan=scan,
            scan_index=scan_index,
            scans_total=scans_total,
            person_snapshots=person_snapshots,
            sources_count=sources_count,
        )


@final
class ScanChoicesController(Controller[PydanticSerializer]):
    """Return selectable choice values for scans and snapshots."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Scans"])
    async def get(self) -> ScanChoicesResponse:
        """Return the scan and snapshot choice values with labels."""
        return ScanChoicesResponse.build()
