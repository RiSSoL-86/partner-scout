from typing import TYPE_CHECKING
from uuid import UUID

from aiogram import F, Router
from django.conf import settings

from services.telegram.handlers.common.decorators import require_message
from services.telegram.handlers.common.messaging import safe_edit_text
from services.telegram.handlers.common.reports import build_report_url
from services.telegram.handlers.companies.callbacks import (
    CompanyCallback,
    CompanyListCallback,
    PersonSnapshotCallback,
    ScanCallback,
)
from services.telegram.handlers.companies.keyboards.company import (
    CompanyKeyboard,
)
from services.telegram.handlers.companies.keyboards.person_snapshot import (
    PersonSnapshotKeyboard,
)
from services.telegram.handlers.companies.services.list import (
    CompanyListTelegramService,
)
from services.telegram.handlers.companies.services.person_snapshots import (
    PersonSnapshotListTelegramService,
)
from services.telegram.handlers.companies.services.scan import (
    CompanyScanTelegramService,
)
from services.telegram.handlers.companies.views.company import CompanyView
from services.telegram.handlers.companies.views.person_snapshot import (
    PersonSnapshotView,
)
from services.telegram.handlers.main.callbacks import MainCallback
from services.telegram.handlers.main.keyboards import MainKeyboard
from services.telegram.handlers.main.views import MainView

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, Message

PAGE_SIZE: int = settings.TELEGRAM_PAGE_SIZE  # type: ignore[misc]

router = Router(name="companies")


@router.callback_query(MainCallback.filter(F.section == "companies"))
@require_message
async def show_companies_menu(
    callback_query: CallbackQuery,
    message: Message,
) -> None:
    """Show the companies section menu."""
    keyboard = CompanyKeyboard.build_menu_keyboard()
    content = CompanyView.build_menu_message(keyboard=keyboard)
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(CompanyListCallback.filter())
@require_message
async def show_companies_list(
    callback_query: CallbackQuery,
    message: Message,
    callback_data: CompanyListCallback,
) -> None:
    """Show a page of the companies list from the database."""
    service = CompanyListTelegramService()
    companies, total = await service.execute(
        offset=callback_data.offset,
        limit=PAGE_SIZE,
    )

    keyboard = CompanyKeyboard.build_list_keyboard(
        companies=companies,
        offset=callback_data.offset,
        page_size=PAGE_SIZE,
        total=total,
    )
    content = CompanyView.build_list_message(
        keyboard=keyboard,
        companies=companies,
        offset=callback_data.offset,
        total=total,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(ScanCallback.filter())
@require_message
async def show_company_scan(
    callback_query: CallbackQuery,
    message: Message,
    callback_data: ScanCallback,
) -> None:
    """Show one company scan with navigation to adjacent scans."""
    service = CompanyScanTelegramService()
    company, scan, scan_index, scans_total = await service.execute(
        company_id=UUID(callback_data.company_id),
        scan_index=callback_data.scan_index,
    )
    if company is None:
        await callback_query.answer("Company not found")
        return

    keyboard = CompanyKeyboard.build_scan_keyboard(
        company_id=callback_data.company_id,
        scan_index=scan_index,
        scans_total=scans_total,
        report_url=build_report_url("companies", callback_data.company_id),
    )
    content = CompanyView.build_scan_message(
        keyboard=keyboard,
        company=company,
        scan=scan,
        scan_index=scan_index,
        scans_total=scans_total,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(PersonSnapshotCallback.filter())
@require_message
async def show_scan_person_snapshots(
    callback_query: CallbackQuery,
    message: Message,
    callback_data: PersonSnapshotCallback,
) -> None:
    """Show a page of person snapshots found in one company scan."""
    service = PersonSnapshotListTelegramService()
    scan, scan_index, snapshots, snapshots_total = await service.execute(
        company_id=UUID(callback_data.company_id),
        scan_index=callback_data.scan_index,
        offset=callback_data.offset,
        limit=PAGE_SIZE,
    )
    if scan is None:
        await callback_query.answer("Scan not found")
        return

    keyboard = PersonSnapshotKeyboard.build_list_keyboard(
        company_id=callback_data.company_id,
        scan_index=scan_index,
        offset=callback_data.offset,
        page_size=PAGE_SIZE,
        total=snapshots_total,
    )
    content = PersonSnapshotView.build_list_message(
        keyboard=keyboard,
        scan=scan,
        snapshots=snapshots,
        offset=callback_data.offset,
        snapshots_total=snapshots_total,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(CompanyCallback.filter(F.action == "back"))
@require_message
async def return_to_main_menu(
    callback_query: CallbackQuery,
    message: Message,
) -> None:
    """Return from the companies section to the main menu."""
    keyboard = MainKeyboard.build_menu_keyboard()
    content = MainView.build_menu_message(keyboard=keyboard)
    await safe_edit_text(message, **content)
    await callback_query.answer()
