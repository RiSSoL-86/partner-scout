from http import HTTPStatus
from typing import final

from django.conf import settings
from django.http import HttpResponse
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
from services.api.common.schemas import ReportQuery
from services.api.telegram.path_params import (
    CompanyScanPathParams,
    PersonPathParams,
)
from services.api.telegram.schemas import (
    CompanyScanResponse,
    PersonReportResponse,
)
from services.api.telegram.services.company_scan_detail import (
    CompanyScanDetailService,
)
from services.api.telegram.services.person_detail import (
    PersonDetailService,
)
from services.api.telegram.utils import render_html

PAGE_SIZE: int = settings.TELEGRAM_PAGE_SIZE  # type: ignore[misc]


@final
class CompanyScanDetailController(Controller[PydanticSerializer]):
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
        parsed_path: Path[CompanyScanPathParams],
        parsed_query: Query[ReportQuery],
    ) -> HttpResponse:
        """Return the company scan report page for a valid signed token."""
        scan_id = str(parsed_path.scan_id)
        if ReportTokenService.unsign(parsed_query.token) != scan_id:
            status = HTTPStatus.FORBIDDEN
            context = {
                "code": status.value,
                "title": status.phrase,
                "message": "Invalid or expired link.",
            }
            return await render_html(
                status=status,
                context=context,
                template_name="telegram/report_error.html",
            )

        service = CompanyScanDetailService()
        result = await service.execute(
            scan_id=parsed_path.scan_id,
            offset=(parsed_query.page - 1) * PAGE_SIZE,
            limit=PAGE_SIZE,
        )
        if result is None:
            status = HTTPStatus.NOT_FOUND
            context = {
                "code": status.value,
                "title": status.phrase,
                "message": "Scan not found.",
            }
            return await render_html(
                status=status,
                context=context,
                template_name="telegram/report_error.html",
            )

        report = CompanyScanResponse.build(
            scan=result["scan"],
            scan_index=result["scan_index"],
            scans_total=result["scans_total"],
            person_snapshots=result["person_snapshots"],
            mentions_by_person=result["mentions_by_person"],
            persons_total=result["persons_total"],
            partner_count=result["partner_count"],
            director_count=result["director_count"],
            confirmed_count=result["confirmed_count"],
            total_sources_count=result["total_sources_count"],
            page=parsed_query.page,
            page_size=PAGE_SIZE,
        )
        return await render_html(
            status=HTTPStatus.OK,
            context={
                "report": report,
                "token": ReportTokenService.sign(scan_id),
            },
            template_name="telegram/company_report.html",
        )


@final
class PersonDetailController(Controller[PydanticSerializer]):
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
        parsed_path: Path[PersonPathParams],
        parsed_query: Query[ReportQuery],
    ) -> HttpResponse:
        """Return the person report page for a valid signed token."""
        person_id = str(parsed_path.person_id)
        if ReportTokenService.unsign(parsed_query.token) != person_id:
            status = HTTPStatus.FORBIDDEN
            context = {
                "code": status.value,
                "title": status.phrase,
                "message": "Invalid or expired link.",
            }
            return await render_html(
                status=status,
                context=context,
                template_name="telegram/report_error.html",
            )

        service = PersonDetailService()
        result = await service.execute(
            person_id=parsed_path.person_id,
            offset=(parsed_query.page - 1) * PAGE_SIZE,
            limit=PAGE_SIZE,
        )
        if result is None:
            status = HTTPStatus.NOT_FOUND
            context = {
                "code": status.value,
                "title": status.phrase,
                "message": "Person not found.",
            }
            return await render_html(
                status=status,
                context=context,
                template_name="telegram/report_error.html",
            )

        report = PersonReportResponse.build(
            person=result["person"],
            snapshots=result["snapshots"],
            mentions_by_scan=result["mentions_by_scan"],
            scans_total=result["scans_total"],
            page=parsed_query.page,
            page_size=PAGE_SIZE,
        )
        return await render_html(
            status=HTTPStatus.OK,
            context={
                "report": report,
                "token": ReportTokenService.sign(person_id),
            },
            template_name="telegram/person_report.html",
        )
