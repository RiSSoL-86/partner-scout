from typing import final

from django.conf import settings
from django.core.signing import BadSignature, TimestampSigner


@final
class ReportTokenService:
    """Sign and verify short-lived tokens for Telegram report links."""

    signer = TimestampSigner(
        key=settings.SECRET_KEY,
        salt="telegram-report",
    )

    @classmethod
    def sign(cls, value: str) -> str:
        """Return a timestamped signed token for a value."""
        return cls.signer.sign(value)

    @classmethod
    def unsign(cls, token: str) -> str | None:
        """Return the signed value if the token is valid and fresh."""
        try:
            return cls.signer.unsign(
                token,
                max_age=settings.REPORT_TOKEN_MAX_AGE_SECONDS,  # type: ignore[misc]
            )
        except BadSignature:
            return None
