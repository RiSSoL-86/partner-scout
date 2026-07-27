from typing import TYPE_CHECKING

from django.urls import reverse

from apps.persons.choices import MentionType

if TYPE_CHECKING:
    from django.test import Client


def person_choices_url() -> str:
    """Return the person choices url."""
    return reverse("api:persons:person_choices")


def test_person_choices_expose_mention_type(client: Client) -> None:
    """Expose the mention type choices with value and label."""
    response = client.get(person_choices_url())

    assert response.status_code == 200
    options = response.json()["personMention"]["mentionType"]
    assert {option["value"] for option in options} == set(MentionType.values)
    profile = next(
        option for option in options if option["value"] == MentionType.PROFILE
    )
    assert profile["label"] == "profile"
