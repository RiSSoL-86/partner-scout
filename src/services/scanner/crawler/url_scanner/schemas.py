from typing import final

from pydantic import BaseModel, ConfigDict


@final
class PageCandidate(BaseModel):
    """A page the keyword scan kept, carrying its already-fetched markdown."""

    model_config = ConfigDict(frozen=True)

    url: str
    title: str
    text: str
    is_hidden: bool = False
