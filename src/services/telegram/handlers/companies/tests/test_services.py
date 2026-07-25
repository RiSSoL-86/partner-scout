import pytest
from asgiref.sync import sync_to_async

from apps.companies.tests.factories import CompanyFactory
from apps.scans.tests.factories import ScanFactory
from services.telegram.handlers.companies.services.list import (
    CompanyListService,
)
from services.telegram.handlers.companies.services.scan import (
    CompanyScanService,
)

pytestmark = pytest.mark.django_db(transaction=True)

create_company = sync_to_async(CompanyFactory)
create_scan = sync_to_async(ScanFactory)


async def test_list_service_orders_by_name_and_paginates() -> None:
    """Return a page of companies ordered by name with the total."""
    await create_company(name="Beta")
    await create_company(name="Alpha")
    await create_company(name="Gamma")

    companies, total = await CompanyListService().execute(offset=0, limit=2)

    assert total == 3
    assert [company.name for company in companies] == ["Alpha", "Beta"]


async def test_scan_service_returns_company_and_scan() -> None:
    """Return the company with its scan at the requested position."""
    company = await create_company()
    scan = await create_scan(company=company)

    (
        loaded_company,
        loaded_scan,
        index,
        total,
    ) = await CompanyScanService().execute(company_id=company.id, scan_index=0)

    assert loaded_company.id == company.id
    assert loaded_scan is not None
    assert loaded_scan.id == scan.id
    assert index == 0
    assert total == 1


async def test_scan_service_without_scans_returns_company_only() -> None:
    """Return the company and no scan when it has none."""
    company = await create_company()

    loaded_company, scan, index, total = await CompanyScanService().execute(
        company_id=company.id,
        scan_index=0,
    )

    assert loaded_company is not None
    assert loaded_company.id == company.id
    assert scan is None
    assert total == 0
