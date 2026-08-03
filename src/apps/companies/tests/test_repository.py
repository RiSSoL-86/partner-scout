import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.companies.repository import CompanyRepository
from apps.companies.tests.factories import CompanyFactory

pytestmark = pytest.mark.django_db(transaction=True)

create_company = sync_to_async(CompanyFactory)


async def test_set_last_scanned_at_persists_the_moment() -> None:
    """Persist the moment the company was last successfully scanned."""
    company = await create_company()
    moment = timezone.now()

    await CompanyRepository().set_last_scanned_at(
        company=company, last_scanned_at=moment
    )

    reloaded = await CompanyRepository().get(company.id)
    assert reloaded is not None
    assert reloaded.last_scanned_at == moment
