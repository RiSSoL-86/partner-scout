from uuid import UUID

from asgiref.sync import async_to_sync
from celery import shared_task

from services.scanner.crawler.service import SourceCollectService
from services.scanner.planner.service import ScanPlanService


@shared_task(name="scans.collect_sources")
def collect_sources(scan_id: str) -> None:
    """Crawl one scan's company site in its own worker."""
    service = SourceCollectService()
    async_to_sync(awaitable=service.execute)(scan_id=UUID(scan_id))


@shared_task(name="scans.run_weekly")
def run_weekly() -> None:
    """Open the weekly scans and fan each out to its own worker."""
    service = ScanPlanService()
    scan_ids = async_to_sync(awaitable=service.execute)()
    for scan_id in scan_ids:
        collect_sources.delay(scan_id=str(scan_id))
