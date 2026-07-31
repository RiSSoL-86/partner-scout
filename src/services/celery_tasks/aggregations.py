from uuid import UUID

from asgiref.sync import async_to_sync
from celery import shared_task

from services.aggregator.services import (
    AggregatePersonsService,
    PlanAggregationService,
)

# Stagger aggregations so LLM calls do not all fire at once.
AGGREGATION_STAGGER_SECONDS = 15 * 60


@shared_task(name="aggregations.aggregate_persons")
def aggregate_persons(scan_id: str) -> None:
    """Classify one completed scan's people into person snapshots."""
    service = AggregatePersonsService()
    async_to_sync(awaitable=service.execute)(scan_id=UUID(scan_id))


@shared_task(name="aggregations.run_weekly")
def run_weekly() -> None:
    """Aggregate every completed scan awaiting classification."""
    service = PlanAggregationService()
    scan_ids = async_to_sync(awaitable=service.execute)()
    for index, scan_id in enumerate(scan_ids):
        aggregate_persons.apply_async(
            kwargs={"scan_id": str(scan_id)},
            countdown=index * AGGREGATION_STAGGER_SECONDS,
        )
