from typing import Literal, final

from aiogram.filters.callback_data import CallbackData


@final
class MainCallback(CallbackData, prefix="main"):
    """Represent callback payloads from the main menu."""

    section: Literal["companies", "persons", "close"]
