from typing import Literal

from aiogram.filters.callback_data import CallbackData


class PersonCallback(CallbackData, prefix="persons"):
    """Represent navigation payloads inside the persons section."""

    action: Literal["menu", "alphabet", "back"]


class PersonListCallback(CallbackData, prefix="person_list"):
    """Represent navigation payloads for the full persons list page."""

    offset: int = 0


class PersonLetterCallback(CallbackData, prefix="person_letters"):
    """Represent navigation payloads for a surname-initial persons page."""

    letter: str
    offset: int = 0


class PersonMentionCallback(CallbackData, prefix="mentions"):
    """Represent navigation payloads for a person mentions page."""

    person_id: str
    offset: int = 0
