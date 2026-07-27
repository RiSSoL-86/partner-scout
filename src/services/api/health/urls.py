from dmr.routing import Router, path

from services.api.health.controllers import HealthController

router = Router(
    prefix="health/",
    urls=[path("", HealthController.as_view(), name="health")],
)
