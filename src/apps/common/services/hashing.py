import hashlib
from typing import final


@final
class HashService:
    """Build stable hashes for application data."""

    @staticmethod
    def build_sha256(value: str) -> str:
        """Return a SHA-256 hex digest for a text value."""
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
