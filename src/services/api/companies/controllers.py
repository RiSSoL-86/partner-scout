from http import HTTPStatus
from typing import final

from dmr import Controller, Path, Query, ResponseSpec, modify
from dmr.errors import ErrorModel
from dmr.plugins.pydantic import PydanticSerializer

from services.api.companies.exceptions import CompanyNotFoundError
from services.api.companies.path_params import CompanyPathParams
from services.api.companies.schemas import (
    CompanyListQuery,
    CompanyListResponse,
    CompanyResponse,
    CompanyScansResponse,
    PageQuery,
)
from services.api.companies.services.list import CompanyListService
from services.api.companies.services.scans import CompanyScansService


@final
class CompanyListController(Controller[PydanticSerializer]):
    """List companies with optional name filtering."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Companies"])
    async def get(
        self,
        parsed_query: Query[CompanyListQuery],
    ) -> CompanyListResponse:
        """Return a page of companies filtered by name."""
        service = CompanyListService()
        companies, total = await service.execute(
            search=parsed_query.search,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )
        return CompanyListResponse(
            items=[CompanyResponse.build(company) for company in companies],
            total=total,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )


@final
class CompanyScansController(Controller[PydanticSerializer]):
    """List one company's scans newest-first."""

    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Companies"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.NOT_FOUND),
        ],
    )
    async def get(
        self,
        parsed_path: Path[CompanyPathParams],
        parsed_query: Query[PageQuery],
    ) -> CompanyScansResponse:
        """Return a page of the company's scans or a 404 error."""
        service = CompanyScansService()
        result = await service.execute(
            company_id=parsed_path.company_id,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )
        if result is None:
            raise CompanyNotFoundError

        company, scans, total = result
        return CompanyScansResponse.build(
            company=company,
            scans=scans,
            total=total,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )
