from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    """Base class for application services."""

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Run the service business operation."""
        raise NotImplementedError
