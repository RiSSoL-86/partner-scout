from typing import TYPE_CHECKING

from django.urls import reverse

if TYPE_CHECKING:
    from django.test import Client


def health_url() -> str:
    """Return the health check url."""
    return reverse("api:health:health")


def test_health_returns_ok(client: Client) -> None:
    """Report a liveness marker for a working API."""
    response = client.get(health_url())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
