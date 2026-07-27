from dmr.routing import Router, path

from services.api.sources.controllers import SourceChoicesController

router = Router(
    prefix="sources/",
    urls=[
        path(
            "choices",
            SourceChoicesController.as_view(),
            name="source_choices",
        ),
    ],
)
