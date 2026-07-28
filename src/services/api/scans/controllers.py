from http import HTTPStatus
from typing import final

from dmr import Controller, Path, ResponseSpec, modify
from dmr.errors import ErrorModel
from dmr.plugins.pydantic import PydanticSerializer

from services.api.scans.exceptions import (
    PersonNotInScanError,
    ScanNotFoundError,
)
from services.api.scans.path_params import (
    ScanPathParams,
    ScanPersonPathParams,
)
from services.api.scans.schemas import (
    ScanChoicesResponse,
    ScanDetailResponse,
    ScanPersonDetailResponse,
)
from services.api.scans.services.detail import ScanDetailService
from services.api.scans.services.person_detail import ScanPersonDetailService


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
            total_sources_count,
            person_source_counts,
        ) = result
        return ScanDetailResponse.build(
            scan=scan,
            scan_index=scan_index,
            scans_total=scans_total,
            person_snapshots=person_snapshots,
            total_sources_count=total_sources_count,
            person_source_counts=person_source_counts,
        )


@final
class ScanPersonDetailController(Controller[PydanticSerializer]):
    """Return one person within a scan with its source mentions."""

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
        parsed_path: Path[ScanPersonPathParams],
    ) -> ScanPersonDetailResponse:
        """Return the scan person detail or a 404 when absent."""
        service = ScanPersonDetailService()
        result = await service.execute(
            scan_id=parsed_path.scan_id,
            person_id=parsed_path.person_id,
        )
        if result is None:
            raise PersonNotInScanError

        person_snapshot, person_mentions = result
        return ScanPersonDetailResponse.build(
            person_snapshot=person_snapshot,
            person_mentions=person_mentions,
        )


@final
class ScanChoicesController(Controller[PydanticSerializer]):
    """Return selectable choice values for scans and snapshots."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Scans"])
    async def get(self) -> ScanChoicesResponse:
        """Return the scan and snapshot choice values with labels."""
        return ScanChoicesResponse.build()
