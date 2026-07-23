from abc import ABC, abstractmethod
from typing import Any


class BaseTelegramService(ABC):
    """Base class for Telegram application services."""

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Run the Telegram business operation."""
        raise NotImplementedError
