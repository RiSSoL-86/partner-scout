from typing import final

from pydantic import BaseModel


@final
class TelegramReportQuery(BaseModel):
    """Query parameters carrying the signed report link token."""

    token: str
