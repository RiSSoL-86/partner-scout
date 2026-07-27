from dmr.routing import Router, path

from services.api.persons.controllers import PersonChoicesController

router = Router(
    prefix="persons/",
    urls=[
        path(
            "choices",
            PersonChoicesController.as_view(),
            name="person_choices",
        ),
    ],
)
