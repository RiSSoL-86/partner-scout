from dmr.routing import Router, path

from services.api.scans.controllers import (
    ScanChoicesController,
    ScanDetailController,
    ScanPersonDetailController,
)

router = Router(
    prefix="scans/",
    urls=[
        path(
            "choices/",
            ScanChoicesController.as_view(),
            name="scan_choices",
        ),
        path(
            "<uuid:scan_id>/",
            ScanDetailController.as_view(),
            name="scan_detail",
        ),
        path(
            "<uuid:scan_id>/persons/<uuid:person_id>/",
            ScanPersonDetailController.as_view(),
            name="scan_person_detail",
        ),
    ],
)
