from typing import Literal, final

from aiogram.filters.callback_data import CallbackData


@final
class PersonCallback(CallbackData, prefix="persons"):
    """Represent navigation payloads inside the persons section."""

    action: Literal["menu", "alphabet", "back"]


@final
class PersonListCallback(CallbackData, prefix="person_list"):
    """Represent navigation payloads for the full persons list page."""

    offset: int = 0


@final
class PersonLetterCallback(CallbackData, prefix="person_letters"):
    """Represent navigation payloads for a surname-initial persons page."""

    letter: str
    offset: int = 0


@final
class PersonMentionsCallback(CallbackData, prefix="mentions"):
    """Represent the payload opening one person card."""

    person_id: str
