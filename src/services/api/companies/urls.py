from dmr.routing import Router, path

from services.api.companies.controllers import (
    CompanyListController,
    CompanyScansController,
)

router = Router(
    prefix="companies/",
    urls=[
        path("", CompanyListController.as_view(), name="company_list"),
        path(
            "<uuid:company_id>/scans/",
            CompanyScansController.as_view(),
            name="company_scans",
        ),
    ],
)
