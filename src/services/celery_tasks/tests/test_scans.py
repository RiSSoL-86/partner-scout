from unittest.mock import AsyncMock, patch
from uuid import uuid4

from services.celery_tasks import scans
from services.celery_tasks.scans import (
    SCAN_STAGGER_SECONDS,
    collect_sources,
    run_weekly,
)


@patch.object(scans, "CollectSourceService")
def test_collect_sources_runs_the_service_with_a_uuid(service_cls) -> None:
    """Run the collect service for the given scan id as a UUID."""
    service_cls.return_value.execute = AsyncMock(return_value=None)
    scan_id = uuid4()

    collect_sources(scan_id=str(scan_id))

    service_cls.return_value.execute.assert_awaited_once_with(scan_id=scan_id)


@patch.object(scans.collect_sources, "apply_async")
@patch.object(scans, "PlanScanService")
def test_run_weekly_schedules_a_staggered_task_per_scan(
    plan_cls,
    apply_async,
) -> None:
    """Fan out one staggered collect task per planned scan."""
    scan_ids = [uuid4(), uuid4()]
    plan_cls.return_value.execute = AsyncMock(return_value=scan_ids)

    run_weekly()

    assert apply_async.call_count == len(scan_ids)
    for index, (scan_id, call) in enumerate(
        zip(scan_ids, apply_async.call_args_list, strict=True)
    ):
        assert call.kwargs["kwargs"] == {"scan_id": str(scan_id)}
        assert call.kwargs["countdown"] == index * SCAN_STAGGER_SECONDS


@patch.object(scans.collect_sources, "apply_async")
@patch.object(scans, "PlanScanService")
def test_run_weekly_schedules_nothing_without_scans(
    plan_cls,
    apply_async,
) -> None:
    """Schedule no tasks when there is nothing to scan."""
    plan_cls.return_value.execute = AsyncMock(return_value=[])

    run_weekly()

    apply_async.assert_not_called()
