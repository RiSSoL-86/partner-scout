from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async

from apps.companies.tests.factories import CompanyFactory
from apps.scans.tests.factories import ScanFactory
from services.telegram.handlers.companies import routes
from services.telegram.handlers.companies.callbacks import (
    CompanyListCallback,
    ScanCallback,
)

pytestmark = pytest.mark.django_db(transaction=True)

create_company = sync_to_async(CompanyFactory)
create_scan = sync_to_async(ScanFactory)


async def test_show_companies_menu_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render the companies menu and acknowledge the callback."""
    await routes.show_companies_menu(callback_query)

    message.edit_text.assert_awaited_once()
    assert "Companies menu" in message.edit_text.await_args.kwargs["text"]
    callback_query.answer.assert_awaited_once_with()


async def test_show_companies_list_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render a page of companies from the database."""
    await create_company(name="Alpha")

    await routes.show_companies_list(
        callback_query,
        callback_data=CompanyListCallback(offset=0),
    )

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()


async def test_show_company_scan_renders_found_scan(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render a company scan when the company exists."""
    company = await create_company()
    await create_scan(company=company)

    await routes.show_company_scan(
        callback_query,
        callback_data=ScanCallback(company_id=str(company.id), scan_index=0),
    )

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()


async def test_show_company_scan_answers_when_company_missing(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Answer with a notice when the company does not exist."""
    await routes.show_company_scan(
        callback_query,
        callback_data=ScanCallback(company_id=str(uuid4()), scan_index=0),
    )

    message.edit_text.assert_not_awaited()
    callback_query.answer.assert_awaited_once_with("Company not found")


async def test_return_to_main_menu_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render the main menu when leaving the companies section."""
    await routes.return_to_main_menu(callback_query)

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()
