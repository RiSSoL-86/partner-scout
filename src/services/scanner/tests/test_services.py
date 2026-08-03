from collections.abc import AsyncIterator
from unittest.mock import patch
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async

from apps.companies.tests.factories import CompanyFactory
from apps.persons.choices import MentionType
from apps.persons.repository import PersonMentionRepository, PersonRepository
from apps.scans.choices import ScanStatus
from apps.scans.models import Scan
from apps.scans.tests.factories import ScanFactory
from apps.sources.choices import PageType
from apps.sources.repository import SourceRepository
from services.scanner.crawler.llm_extractor.schemas import (
    CrawledPage,
    ExtractedPerson,
    PageExtraction,
)
from services.scanner.services import CollectSourceService, PlanScanService

pytestmark = pytest.mark.django_db(transaction=True)

create_company = sync_to_async(CompanyFactory)
create_scan = sync_to_async(ScanFactory)


def make_page(**overrides: object) -> CrawledPage:
    """Build a crawled page carrying one partner-level person."""
    persons = overrides.pop(
        "persons",
        [
            ExtractedPerson(
                first_name="Ivan",
                last_name="Petrov",
                role_title="Партнёр",
                mention_type=MentionType.PROFILE,
                email="ivan@example.com",
                phone="+7 900 000-00-00",
            )
        ],
    )
    return CrawledPage(
        url="https://example.com/team",
        title="Team",
        extraction=PageExtraction(
            is_relevant=True,
            page_type=PageType.TEAM,
            persons=persons,  # type: ignore[arg-type]
        ),
    )


def fake_engine(pages: list[CrawledPage] | None = None, *, boom: bool = False):
    """Build a CrawlEngine stand-in yielding pages or raising mid-crawl."""

    class _FakeEngine:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def crawl(self) -> AsyncIterator[CrawledPage]:
            for page in pages or []:
                yield page
            if boom:
                raise RuntimeError("crawl boom")

    return _FakeEngine


# --- PlanScanService -------------------------------------------------------


async def test_plan_opens_a_pending_scan_for_enabled_companies() -> None:
    """Open a pending scan for every scan-enabled company."""
    enabled = await create_company(scan_enabled=True)
    await create_company(scan_enabled=False)

    scan_ids = await PlanScanService().execute()

    assert len(scan_ids) == 1
    scan = await Scan.objects.aget(id=scan_ids[0])
    assert scan.company_id == enabled.id
    assert scan.scan_status == ScanStatus.PENDING


async def test_plan_skips_a_company_with_an_active_scan() -> None:
    """Skip a company that already has an active scan open."""
    company = await create_company(scan_enabled=True)
    await create_scan(company=company, scan_status=ScanStatus.PENDING)

    scan_ids = await PlanScanService().execute()

    assert scan_ids == []


# --- CollectSourceService --------------------------------------------------


async def test_collect_returns_none_for_a_missing_scan() -> None:
    """Return None when the scan no longer exists."""
    assert await CollectSourceService().execute(scan_id=uuid4()) is None


async def test_collect_skips_a_scan_that_is_not_pending() -> None:
    """Leave a non-pending scan untouched."""
    scan = await create_scan(scan_status=ScanStatus.COMPLETED)

    with patch("services.scanner.services.CrawlEngine", fake_engine()):
        result = await CollectSourceService().execute(scan_id=scan.id)

    assert result is not None
    assert result.scan_status == ScanStatus.COMPLETED


async def test_collect_persists_sources_persons_and_mentions() -> None:
    """Persist a crawled page as a source with its person and mention."""
    company = await create_company()
    scan = await create_scan(company=company, scan_status=ScanStatus.PENDING)

    with patch(
        "services.scanner.services.CrawlEngine",
        fake_engine([make_page()]),
    ):
        await CollectSourceService().execute(scan_id=scan.id)

    assert await SourceRepository().count() == 1
    assert await PersonRepository().count() == 1
    assert (
        await PersonMentionRepository().count(filters={"scan_id": scan.id})
        == 1
    )
    reloaded = await Scan.objects.select_related("company").aget(id=scan.id)
    assert reloaded.scan_status == ScanStatus.COMPLETED
    assert "1" in reloaded.scan_report
    assert reloaded.company.last_scanned_at is not None


async def test_collect_ignores_persons_without_a_full_name() -> None:
    """Drop extracted persons missing a first or last name."""
    scan = await create_scan(scan_status=ScanStatus.PENDING)
    nameless = ExtractedPerson(
        first_name="",
        last_name="",
        role_title="Партнёр",
        mention_type=MentionType.PROFILE,
    )

    with patch(
        "services.scanner.services.CrawlEngine",
        fake_engine([make_page(persons=[nameless])]),
    ):
        await CollectSourceService().execute(scan_id=scan.id)

    assert (
        await PersonMentionRepository().count(filters={"scan_id": scan.id})
        == 0
    )


async def test_collect_marks_the_scan_failed_when_the_crawl_raises() -> None:
    """Record the failure when the crawl raises mid-run."""
    scan = await create_scan(scan_status=ScanStatus.PENDING)

    with patch(
        "services.scanner.services.CrawlEngine",
        fake_engine(boom=True),
    ):
        await CollectSourceService().execute(scan_id=scan.id)

    reloaded = await Scan.objects.aget(id=scan.id)
    assert reloaded.scan_status == ScanStatus.FAILED
    assert "crawl boom" in reloaded.scan_error
