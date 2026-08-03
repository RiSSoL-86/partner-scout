from uuid import UUID

from asgiref.sync import async_to_sync
from celery import shared_task

from services.scanner.services import CollectSourceService, PlanScanService

# Stagger scan starts so heavy crawls do not all run at once.
SCAN_STAGGER_SECONDS = 30 * 60


@shared_task(name="scans.collect_sources")
def collect_sources(scan_id: str) -> None:
    """Crawl one scan's company site in its own worker."""
    service = CollectSourceService()
    async_to_sync(awaitable=service.execute)(scan_id=UUID(scan_id))


@shared_task(name="scans.run_weekly")
def run_weekly() -> None:
    """Open the weekly scans, staggering each start to spread the load."""
    service = PlanScanService()
    scan_ids = async_to_sync(awaitable=service.execute)()
    for index, scan_id in enumerate(scan_ids):
        collect_sources.apply_async(
            kwargs={"scan_id": str(scan_id)},
            countdown=index * SCAN_STAGGER_SECONDS,
        )
