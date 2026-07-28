from dmr.routing import Router, path

from services.api.persons.controllers import (
    PersonChoicesController,
    PersonListController,
    PersonSourcesController,
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
            "<uuid:person_id>/sources/",
            PersonSourcesController.as_view(),
            name="person_sources",
        ),
    ],
)
