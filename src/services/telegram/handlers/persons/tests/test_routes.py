from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async

from apps.persons.tests.factories import PersonFactory
from services.telegram.handlers.persons import routes
from services.telegram.handlers.persons.callbacks import (
    PersonLetterCallback,
    PersonListCallback,
    PersonMentionsCallback,
)

pytestmark = pytest.mark.django_db(transaction=True)

create_person = sync_to_async(PersonFactory)


async def test_show_persons_menu_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render the persons menu and acknowledge the callback."""
    await routes.show_persons_menu(callback_query)

    message.edit_text.assert_awaited_once()
    assert "Persons menu" in message.edit_text.await_args.kwargs["text"]
    callback_query.answer.assert_awaited_once_with()


async def test_show_persons_list_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render a page of all persons from the database."""
    await create_person(last_name="Ivanov")

    await routes.show_persons_list(
        callback_query,
        callback_data=PersonListCallback(offset=0),
    )

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()


async def test_show_persons_alphabet_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render the surname alphabet index from the database."""
    await create_person(last_name="Ivanov")

    await routes.show_persons_alphabet(callback_query)

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()


async def test_show_persons_by_letter_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render a page of persons for one surname initial."""
    await create_person(last_name="Ivanov")

    await routes.show_persons_by_letter(
        callback_query,
        callback_data=PersonLetterCallback(letter="I", offset=0),
    )

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()


async def test_show_person_mentions_renders_found_person(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render a person card when the person exists."""
    person = await create_person()

    await routes.show_person_mentions(
        callback_query,
        callback_data=PersonMentionsCallback(person_id=str(person.id)),
    )

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()


async def test_show_person_mentions_answers_when_person_missing(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Answer with a notice when the person does not exist."""
    await routes.show_person_mentions(
        callback_query,
        callback_data=PersonMentionsCallback(person_id=str(uuid4())),
    )

    message.edit_text.assert_not_awaited()
    callback_query.answer.assert_awaited_once_with("Person not found")


async def test_return_to_main_menu_edits_message(
    callback_query: AsyncMock,
    message: AsyncMock,
) -> None:
    """Render the main menu when leaving the persons section."""
    await routes.return_to_main_menu(callback_query)

    message.edit_text.assert_awaited_once()
    callback_query.answer.assert_awaited_once_with()
