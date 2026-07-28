from dmr.routing import Router, path

from services.api.persons.controllers import (
    PersonChoicesController,
    PersonListController,
    PersonTimelineController,
)

router = Router(
    prefix="persons/",
    urls=[
        path("", PersonListController.as_view(), name="person_list"),
        path(
            "choices/",
            PersonChoicesController.as_view(),
            name="person_choices",
        ),
        path(
            "<uuid:person_id>/timeline/",
            PersonTimelineController.as_view(),
            name="person_timeline",
        ),
    ],
)
