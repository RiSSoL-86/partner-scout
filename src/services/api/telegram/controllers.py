from http import HTTPStatus
from typing import final

from django.http import HttpResponse
from django.template.loader import render_to_string
from dmr import (
    Controller,
    Path,
    Query,
    ResponseSpec,
    validate,
)
from dmr.plugins.pydantic import PydanticSerializer
from dmr.renderers import FileRenderer

from apps.common.services.report_token import ReportTokenService
from services.api.telegram.path_params import (
    TelegramCompanyPathParams,
    TelegramPersonPathParams,
)
from services.api.telegram.schemas import TelegramReportQuery
from services.api.telegram.services.company_detail import (
    TelegramCompanyDetailService,
)
from services.api.telegram.services.person_detail import (
    TelegramPersonDetailService,
)


def _html_response(body: str, status: HTTPStatus) -> HttpResponse:
    """Return an HTML response with the given body and status."""
    return HttpResponse(
        body,
        status=status,
        content_type="text/html; charset=utf-8",
    )


@final
class TelegramCompanyDetailController(Controller[PydanticSerializer]):
    """Render one company report as HTML for a Telegram Mini App."""

    auth = None

    @validate(
        ResponseSpec(
            str,
            status_code=HTTPStatus.OK,
            limit_to_content_types={"text/html"},
            description="Company report rendered as HTML",
        ),
        ResponseSpec(
            str,
            status_code=HTTPStatus.FORBIDDEN,
            limit_to_content_types={"text/html"},
            description="Invalid or expired report link",
        ),
        ResponseSpec(
            str,
            status_code=HTTPStatus.NOT_FOUND,
            limit_to_content_types={"text/html"},
            description="Company not found",
        ),
        tags=["Telegram"],
        renderers=[FileRenderer("text/html")],
        validate_responses=False,
    )
    async def get(
        self,
        parsed_path: Path[TelegramCompanyPathParams],
        parsed_query: Query[TelegramReportQuery],
    ) -> HttpResponse:
        """Return the company report page for a valid signed token."""
        company_id = str(parsed_path.company_id)
        if ReportTokenService.unsign(parsed_query.token) != company_id:
            return _html_response(
                "<h1>403 Forbidden</h1><p>Invalid or expired link.</p>",
                HTTPStatus.FORBIDDEN,
            )

        service = TelegramCompanyDetailService()
        company = await service.execute(company_id=parsed_path.company_id)
        if company is None:
            return _html_response(
                "<h1>404 Not Found</h1><p>Company not found.</p>",
                HTTPStatus.NOT_FOUND,
            )

        html = render_to_string(
            "telegram/company_report.html",
            context={"company": company},
        )
        return _html_response(html, HTTPStatus.OK)


@final
class TelegramPersonDetailController(Controller[PydanticSerializer]):
    """Render one person report as HTML for a Telegram Mini App."""

    auth = None

    @validate(
        ResponseSpec(
            str,
            status_code=HTTPStatus.OK,
            limit_to_content_types={"text/html"},
            description="Person report rendered as HTML",
        ),
        ResponseSpec(
            str,
            status_code=HTTPStatus.FORBIDDEN,
            limit_to_content_types={"text/html"},
            description="Invalid or expired report link",
        ),
        ResponseSpec(
            str,
            status_code=HTTPStatus.NOT_FOUND,
            limit_to_content_types={"text/html"},
            description="Person not found",
        ),
        tags=["Telegram"],
        renderers=[FileRenderer("text/html")],
        validate_responses=False,
    )
    async def get(
        self,
        parsed_path: Path[TelegramPersonPathParams],
        parsed_query: Query[TelegramReportQuery],
    ) -> HttpResponse:
        """Return the person report page for a valid signed token."""
        person_id = str(parsed_path.person_id)
        if ReportTokenService.unsign(parsed_query.token) != person_id:
            return _html_response(
                "<h1>403 Forbidden</h1><p>Invalid or expired link.</p>",
                HTTPStatus.FORBIDDEN,
            )

        service = TelegramPersonDetailService()
        person = await service.execute(person_id=parsed_path.person_id)
        if person is None:
            return _html_response(
                "<h1>404 Not Found</h1><p>Person not found.</p>",
                HTTPStatus.NOT_FOUND,
            )

        html = render_to_string(
            "telegram/person_report.html",
            context={"person": person},
        )
        return _html_response(html, HTTPStatus.OK)
