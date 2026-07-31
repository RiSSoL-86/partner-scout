import logging
from functools import partial
from typing import TYPE_CHECKING, final, override
from uuid import UUID

from django.db import IntegrityError

from apps.common.services.base import BaseService
from apps.companies.repository import CompanyRepository
from apps.persons.models import Person, PersonMention
from apps.persons.repository import PersonMentionRepository, PersonRepository
from apps.scans.choices import ScanStatus
from apps.scans.models import Scan, ScanSource
from apps.scans.repository import ScanRepository, ScanSourceRepository
from apps.sources.models import Source
from apps.sources.repository import SourceRepository
from services.scanner.crawler.engine import CrawlEngine

if TYPE_CHECKING:
    from services.scanner.crawler.llm_extractor.schemas import CrawledPage

logger = logging.getLogger(__name__)


@final
class PlanScanService(BaseService):
    """Open a pending scan for every scan-enabled company."""

    company_repository = CompanyRepository()
    scan_repository = ScanRepository()

    @override
    async def execute(self) -> list[UUID]:
        """Create pending scans and return the ids of the new ones."""
        companies = await self.company_repository.list_all(
            filters={"scan_enabled": True},
        )
        scan_ids: list[UUID] = []
        for company in companies:
            scan = None
            try:
                scan = await self.scan_repository.create(
                    Scan(company=company, scan_status=ScanStatus.PENDING),
                )
            except IntegrityError:
                logger.info(
                    msg=f"Company {company.id} already has an "
                    "active scan; skipping",
                )
            if scan is not None:
                scan_ids.append(scan.id)
        return scan_ids


@final
class CollectSourceService(BaseService):
    """Crawl a company site and persist its sources, persons and mentions."""

    company_repository = CompanyRepository()
    person_repository = PersonRepository()
    person_mention_repository = PersonMentionRepository()
    scan_repository = ScanRepository()
    scan_source_repository = ScanSourceRepository()
    source_repository = SourceRepository()

    @override
    async def execute(self, scan_id: UUID) -> Scan | None:
        """Run the crawl for a scan and return it, or None if it is gone."""
        scan = await self.scan_repository.find_one(
            filters={"id": scan_id},
            select_related=("company",),
        )
        if scan is None:
            return None

        if scan.scan_status != ScanStatus.PENDING:
            logger.info(
                msg=f"Scan {scan_id} is not pending ({scan.scan_status=}); "
                "skipping run"
            )
            return scan

        await self.scan_repository.set_scan_status(
            scan=scan, scan_status=ScanStatus.RUNNING
        )

        crawl_engine = CrawlEngine(
            url=scan.company.website_url,
            company_name=scan.company.name,
            on_page_scanned=partial(
                self.scan_repository.increment_pages_scanned, scan=scan
            ),
        )
        try:
            async for page in crawl_engine.crawl():
                await self._collect_page(scan=scan, page=page)
        except Exception as error:
            logger.exception(msg=f"Scan {scan_id} crawl failed")
            await self.scan_repository.set_scan_status(
                scan=scan,
                scan_status=ScanStatus.FAILED,
                scan_error=str(error),
            )
            return scan

        person_mentions_count = await self.person_mention_repository.count(
            filters={"scan_id": scan.id},
        )
        await self.scan_repository.set_scan_status(
            scan=scan,
            scan_status=ScanStatus.COMPLETED,
            scan_report=f"Mentions of persons: {person_mentions_count}.",
        )
        await self.company_repository.set_last_scanned_at(
            company=scan.company,
            last_scanned_at=scan.created_timestamp,
        )
        return scan

    async def _collect_page(self, scan: Scan, page: CrawledPage) -> None:
        """Persist one crawled page as a source with its persons."""
        logger.info(
            msg=f"[scan {scan.id}] {page.url} "
            f"relevant={page.extraction.is_relevant} "
            f"persons={len(page.extraction.persons)}"
        )

        url = Source.normalize_url(page.url)
        source = await self.source_repository.get_or_create(
            filters={"url": url},
            instance=Source(
                url=url,
                title=page.title,
                page_type=page.extraction.page_type,
                is_hidden=page.is_hidden,
            ),
        )
        await self.scan_source_repository.get_or_create(
            filters={"scan_id": scan.id, "source_id": source.id},
            instance=ScanSource(scan=scan, source=source),
        )
        for extracted in page.extraction.persons:
            if not extracted.first_name.strip() or (
                not extracted.last_name.strip()
            ):
                continue
            person = await self.person_repository.get_or_create(
                filters={},
                instance=Person(
                    first_name=extracted.first_name,
                    middle_name=extracted.middle_name,
                    last_name=extracted.last_name,
                ),
            )
            await self.person_mention_repository.get_or_create(
                filters={
                    "scan_id": scan.id,
                    "person_id": person.id,
                    "source_id": source.id,
                },
                instance=PersonMention(
                    scan=scan,
                    person=person,
                    source=source,
                    mention_type=extracted.mention_type,
                    role_title=extracted.role_title,
                    email=extracted.email,
                    phone=extracted.phone,
                ),
            )
