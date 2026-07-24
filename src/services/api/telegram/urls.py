from dmr.routing import Router, path

from services.api.telegram.controllers import (
    TelegramCompanyDetailController,
    TelegramPersonDetailController,
)

router = Router(
    prefix="telegram/",
    urls=[
        path(
            "companies/<uuid:company_id>",
            TelegramCompanyDetailController.as_view(),
            name="telegram_company_detail",
        ),
        path(
            "persons/<uuid:person_id>",
            TelegramPersonDetailController.as_view(),
            name="telegram_person_detail",
        ),
    ],
)
