from typing import TYPE_CHECKING

from django.urls import reverse

from apps.sources.choices import PageType

if TYPE_CHECKING:
    from django.test import Client


def source_choices_url() -> str:
    """Return the source choices url."""
    return reverse("api:sources:source_choices")


def test_source_choices_expose_page_type(client: Client) -> None:
    """Expose the page type choices with value and label."""
    response = client.get(source_choices_url())

    assert response.status_code == 200
    options = response.json()["source"]["pageType"]
    assert {option["value"] for option in options} == set(PageType.values)
    profile = next(
        option for option in options if option["value"] == PageType.PROFILE
    )
    assert profile["label"] == "profile"
