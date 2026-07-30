import logging
from typing import TYPE_CHECKING, final, override

from crawl4ai import (
    LLMConfig,
    LLMExtractionStrategy,
)
from django.conf import settings
from pydantic import ValidationError

from apps.common.services.base import BaseService
from services.scanner.crawler.llm_extractor.prompt import (
    build_filter_prompt,
)
from services.scanner.crawler.llm_extractor.schemas import (
    CrawledPage,
    ExtractedPerson,
    PageExtraction,
)
from services.scanner.crawler.url_scanner.search_rules import (
    is_target_position,
)

if TYPE_CHECKING:
    from services.scanner.crawler.url_scanner.schemas import (
        PageCandidate,
    )

logger = logging.getLogger(__name__)


@final
class LlmExtractorService(BaseService):
    """Turn one candidate page into a verdict with a single LLM call."""

    def __init__(self, website: str, company_name: str) -> None:
        """Build the gate LLM strategy for the firm being scanned."""
        self.strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider=settings.CRAWLER_LLM_MODEL,  # type: ignore[misc]
                api_token=settings.OPENAI_API_KEY,  # type: ignore[misc]
                temperature=settings.CRAWLER_LLM_TEMPERATURE,  # type: ignore[misc]
            ),
            instruction=build_filter_prompt(
                company_name=company_name, website=website
            ),
            schema=PageExtraction.model_json_schema(),
            extraction_type="schema",
            input_format="markdown",
            apply_chunking=False,
        )

    @override
    async def execute(self, candidate: PageCandidate) -> CrawledPage | None:
        """Ask the gate LLM about one page, or return None to skip it."""
        try:
            blocks = await self.strategy.arun(
                url=candidate.url, sections=[candidate.text]
            )
        except Exception:
            logger.exception(msg=f"Gate LLM failed for {candidate.url}")
            return None

        if not blocks:
            return None

        data = blocks[0]
        if data.get("error"):
            logger.warning(msg=f"Gate reported an error for {candidate.url}")
            return None

        try:
            extraction = PageExtraction.model_validate(data)
        except ValidationError:
            logger.warning(msg="Gate payload did not match the page schema")
            return None

        kept: list[ExtractedPerson] = []
        for person in extraction.persons:
            if is_target_position(person.role_title):
                kept.append(person)
                continue
            logger.info(
                msg=(
                    f"[{candidate.url}] dropped "
                    f"{person.last_name} {person.first_name} "
                    f"by position (role_title={person.role_title!r})"
                )
            )
        if not kept:
            return None
        extraction.persons = kept

        return CrawledPage(
            url=candidate.url,
            title=candidate.title,
            is_hidden=candidate.is_hidden,
            extraction=extraction,
        )

    def log_usage(self, domain: str) -> None:
        """Log the gate LLM token spend accumulated over this crawl."""
        usage = getattr(self.strategy, "total_usage", None)
        if usage is None:
            return
        prompt_tokens = getattr(usage, "prompt_tokens", 0)
        completion_tokens = getattr(usage, "completion_tokens", 0)
        total_tokens = getattr(usage, "total_tokens", 0) or (
            prompt_tokens + completion_tokens
        )
        calls = len(getattr(self.strategy, "usages", []) or [])
        logger.info(
            msg=(
                f"Gate LLM usage for {domain}: {calls} calls, "
                f"prompt={prompt_tokens}, completion={completion_tokens}, "
                f"total={total_tokens} tokens"
            )
        )
