from unittest.mock import AsyncMock

from apps.persons.choices import MentionType
from apps.sources.choices import PageType
from services.scanner.crawler.llm_extractor.services import (
    LlmExtractorService,
)
from services.scanner.crawler.url_scanner.schemas import PageCandidate


def make_service(blocks: object) -> LlmExtractorService:
    """Build an extractor whose gate LLM returns the given blocks."""
    service = LlmExtractorService(
        website="https://example.com", company_name="Acme"
    )
    service.strategy = AsyncMock()  # type: ignore[misc]
    service.strategy.arun.return_value = blocks
    return service


def make_candidate() -> PageCandidate:
    """Build a candidate page carrying already-fetched markdown."""
    return PageCandidate(
        url="https://example.com/team",
        title="Team",
        text="team page markdown",
    )


def person(role_title: str, last_name: str = "Petrov") -> dict[str, object]:
    """Build one extracted-person payload as the gate LLM would emit it."""
    return {
        "first_name": "Ivan",
        "last_name": last_name,
        "role_title": role_title,
        "mention_type": MentionType.PROFILE.value,
    }


def extraction(persons: list[dict[str, object]]) -> dict[str, object]:
    """Build a full gate verdict payload for a relevant page."""
    return {
        "is_relevant": True,
        "page_type": PageType.TEAM.value,
        "persons": persons,
    }


async def test_returns_none_when_the_gate_yields_no_blocks() -> None:
    """Skip the page when the gate LLM returns nothing."""
    service = make_service(blocks=[])

    assert await service.execute(candidate=make_candidate()) is None


async def test_returns_none_when_the_gate_reports_an_error() -> None:
    """Skip the page when the gate block carries an error."""
    service = make_service(blocks=[{"error": "boom"}])

    assert await service.execute(candidate=make_candidate()) is None


async def test_returns_none_on_a_malformed_payload() -> None:
    """Skip the page when the gate payload fails schema validation."""
    service = make_service(blocks=[{"not": "a page"}])

    assert await service.execute(candidate=make_candidate()) is None


async def test_keeps_only_target_position_persons() -> None:
    """Return a page carrying only its partner and director persons."""
    service = make_service(
        blocks=[
            extraction(
                [
                    person(role_title="Партнёр", last_name="Partner"),
                    person(role_title="Аналитик", last_name="Analyst"),
                ]
            )
        ]
    )

    page = await service.execute(candidate=make_candidate())

    assert page is not None
    assert page.url == "https://example.com/team"
    assert [p.last_name for p in page.extraction.persons] == ["Partner"]


async def test_returns_none_when_no_person_holds_a_target_position() -> None:
    """Skip the page when none of its people are partners or directors."""
    service = make_service(
        blocks=[extraction([person(role_title="Consultant")])]
    )

    assert await service.execute(candidate=make_candidate()) is None
