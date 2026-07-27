from dmr.routing import Router, path

from services.api.scans.controllers import (
    ScanChoicesController,
    ScanDetailController,
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
    ],
)
