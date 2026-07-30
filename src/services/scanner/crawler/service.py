import logging
from typing import TYPE_CHECKING, final, override
from uuid import UUID

from apps.common.services.base import BaseService
from apps.common.services.hashing import HashService
from apps.persons.models import Person, PersonMention
from apps.persons.repository import PersonMentionRepository, PersonRepository
from apps.scans.choices import ScanStatus
from apps.scans.models import Scan, ScanSource
from apps.scans.repository import ScanRepository, ScanSourceRepository
from apps.sources.models import Source
from apps.sources.repository import SourceRepository
from services.scanner.crawler.core.engine import CrawlEngine

if TYPE_CHECKING:
    from services.scanner.crawler.core.llm_extractor.schemas import (
        CrawledPage,
    )

logger = logging.getLogger(__name__)


@final
class SourceCollectService(BaseService):
    """Crawl a company site and persist its sources, persons and mentions."""

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

        if scan.status != ScanStatus.PENDING:
            logger.info(
                msg=f"Scan {scan_id} is not pending ({scan.status=}); "
                "skipping run"
            )
            return scan

        await self.scan_repository.set_status(
            scan=scan, status=ScanStatus.RUNNING
        )

        crawl_engine = CrawlEngine(
            url=scan.company.website_url,
            company_name=scan.company.name,
        )
        try:
            async for page in crawl_engine.crawl():
                await self._collect_page(scan=scan, page=page)
        except Exception as error:
            logger.exception(msg=f"Scan {scan_id} crawl failed")
            await self.scan_repository.set_status(
                scan=scan,
                status=ScanStatus.FAILED,
                error=str(error),
            )
            return scan

        await self.scan_repository.set_status(
            scan=scan, status=ScanStatus.COMPLETED
        )
        return scan

    async def _collect_page(self, scan: Scan, page: CrawledPage) -> None:
        """Count one crawled page and persist it when it is relevant."""
        logger.info(
            msg=f"[scan {scan.id}] {page.url} "
            f"relevant={page.extraction.is_relevant} "
            f"persons={len(page.extraction.persons)}"
        )
        await self.scan_repository.increment_pages_scanned(scan=scan)

        if not page.extraction.is_relevant:
            return

        content_hash = HashService.build_sha256(value=page.content)
        source = await self.source_repository.get_or_create(
            filters={"content_hash": content_hash},
            instance=Source(
                url=page.url,
                title=page.title,
                page_type=page.extraction.page_type,
                is_hidden=page.is_hidden,
                content=page.content,
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
                    context=extracted.context,
                ),
            )
