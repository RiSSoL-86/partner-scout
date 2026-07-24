from typing import TYPE_CHECKING
from uuid import UUID

from aiogram import F, Router
from django.conf import settings

from services.telegram.handlers.common.decorators import require_message
from services.telegram.handlers.common.messaging import safe_edit_text
from services.telegram.handlers.main.callbacks import MainCallback
from services.telegram.handlers.main.keyboards import MainKeyboard
from services.telegram.handlers.main.views import MainView
from services.telegram.handlers.persons.callbacks import (
    PersonCallback,
    PersonLetterCallback,
    PersonListCallback,
    PersonMentionCallback,
)
from services.telegram.handlers.persons.keyboards.person import PersonKeyboard
from services.telegram.handlers.persons.keyboards.person_mention import (
    PersonMentionKeyboard,
)
from services.telegram.handlers.persons.services.alphabet import (
    PersonAlphabetTelegramService,
)
from services.telegram.handlers.persons.services.by_letter import (
    PersonByLetterListTelegramService,
)
from services.telegram.handlers.persons.services.list import (
    PersonListTelegramService,
)
from services.telegram.handlers.persons.services.person_mention import (
    PersonMentionListTelegramService,
)
from services.telegram.handlers.persons.views.person import PersonView
from services.telegram.handlers.persons.views.person_mention import (
    PersonMentionView,
)

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, Message

PAGE_SIZE: int = settings.TELEGRAM_PAGE_SIZE  # type: ignore[misc]

router = Router(name="persons")


@router.callback_query(MainCallback.filter(F.section == "persons"))
@router.callback_query(PersonCallback.filter(F.action == "menu"))
@require_message
async def show_persons_menu(
    callback_query: CallbackQuery,
    message: Message,
) -> None:
    """Show the persons section menu."""
    keyboard = PersonKeyboard.build_menu_keyboard()
    content = PersonView.build_menu_message(keyboard=keyboard)
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(PersonListCallback.filter())
@require_message
async def show_persons_list(
    callback_query: CallbackQuery,
    message: Message,
    callback_data: PersonListCallback,
) -> None:
    """Show a page of all persons ordered by name."""
    service = PersonListTelegramService()
    persons, total = await service.execute(
        offset=callback_data.offset,
        limit=PAGE_SIZE,
    )

    keyboard = PersonKeyboard.build_list_keyboard(
        persons=persons,
        offset=callback_data.offset,
        page_size=PAGE_SIZE,
        total=total,
    )
    content = PersonView.build_list_message(
        keyboard=keyboard,
        persons=persons,
        offset=callback_data.offset,
        total=total,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(PersonCallback.filter(F.action == "alphabet"))
@require_message
async def show_persons_alphabet(
    callback_query: CallbackQuery,
    message: Message,
) -> None:
    """Show the persons surname alphabet index."""
    service = PersonAlphabetTelegramService()
    initials = await service.execute()

    keyboard = PersonKeyboard.build_alphabet_keyboard(initials=initials)
    content = PersonView.build_alphabet_message(
        keyboard=keyboard,
        initials=initials,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(PersonLetterCallback.filter())
@require_message
async def show_persons_by_letter(
    callback_query: CallbackQuery,
    message: Message,
    callback_data: PersonLetterCallback,
) -> None:
    """Show a page of persons for one surname initial."""
    service = PersonByLetterListTelegramService()
    persons, total = await service.execute(
        letter=callback_data.letter,
        offset=callback_data.offset,
        limit=PAGE_SIZE,
    )

    keyboard = PersonKeyboard.build_letter_keyboard(
        persons=persons,
        letter=callback_data.letter,
        offset=callback_data.offset,
        page_size=PAGE_SIZE,
        total=total,
    )
    content = PersonView.build_letter_message(
        keyboard=keyboard,
        persons=persons,
        letter=callback_data.letter,
        offset=callback_data.offset,
        total=total,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(PersonMentionCallback.filter())
@require_message
async def show_person_mentions(
    callback_query: CallbackQuery,
    message: Message,
    callback_data: PersonMentionCallback,
) -> None:
    """Show a page of one person mentions ordered by time."""
    service = PersonMentionListTelegramService()
    person, mentions, total = await service.execute(
        person_id=UUID(callback_data.person_id),
        offset=callback_data.offset,
        limit=PAGE_SIZE,
    )
    if person is None:
        await callback_query.answer("Person not found")
        return

    keyboard = PersonMentionKeyboard.build_list_keyboard(
        person_id=callback_data.person_id,
        offset=callback_data.offset,
        page_size=PAGE_SIZE,
        total=total,
    )
    content = PersonMentionView.build_list_message(
        keyboard=keyboard,
        person=person,
        mentions=mentions,
        offset=callback_data.offset,
        total=total,
    )
    await safe_edit_text(message, **content)
    await callback_query.answer()


@router.callback_query(PersonCallback.filter(F.action == "back"))
@require_message
async def return_to_main_menu(
    callback_query: CallbackQuery,
    message: Message,
) -> None:
    """Return from the persons section to the main menu."""
    keyboard = MainKeyboard.build_menu_keyboard()
    content = MainView.build_menu_message(keyboard=keyboard)
    await safe_edit_text(message, **content)
    await callback_query.answer()
