import pytest

from services.scanner.crawler.url_scanner.search_rules import (
    is_target_position,
    mentions_partner_or_director,
)


@pytest.mark.parametrize(
    "position",
    [
        "Партнёр",
        "Партнер практики",
        "Директор по аудиту",
        "Managing Partner",
        "DIRECTOR",
    ],
)
def test_is_target_position_keeps_partner_and_director_ranks(
    position: str,
) -> None:
    """Keep any title naming a partner or director rank."""
    assert is_target_position(position) is True


@pytest.mark.parametrize(
    "position",
    ["Аналитик", "Consultant", "Senior Manager", ""],
)
def test_is_target_position_drops_other_ranks(position: str) -> None:
    """Drop titles that do not name a partner or director rank."""
    assert is_target_position(position) is False


def test_pre_gate_matches_a_partner_word_in_the_body() -> None:
    """Pass a page whose body mentions a partner or director."""
    text = "Наша команда: Иван Петров, партнёр практики аудита."

    assert mentions_partner_or_director(text) is True


def test_pre_gate_rejects_a_body_without_target_words() -> None:
    """Reject a page body with no partner or director word."""
    text = "Company news: we opened a new office this spring."

    assert mentions_partner_or_director(text) is False
