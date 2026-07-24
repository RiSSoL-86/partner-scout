from typing import Literal

from aiogram.filters.callback_data import CallbackData


class MainCallback(CallbackData, prefix="main"):
    """Represent callback payloads from the main menu."""

    section: Literal["companies", "persons", "close"]
