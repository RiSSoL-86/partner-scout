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


class PersonMentionsCallback(CallbackData, prefix="mentions"):
    """Represent the payload opening one person card."""

    person_id: str
