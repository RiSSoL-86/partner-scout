from dmr.routing import Router, path

from services.api.telegram.controllers import (
    CompanyScanDetailController,
    PersonDetailController,
)

router = Router(
    prefix="telegram/",
    urls=[
        path(
            "companies/scans/<uuid:scan_id>",
            CompanyScanDetailController.as_view(),
            name="telegram_company_scan_detail",
        ),
        path(
            "persons/<uuid:person_id>",
            PersonDetailController.as_view(),
            name="telegram_person_detail",
        ),
    ],
)
