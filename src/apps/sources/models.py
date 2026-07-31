from typing import final, override
from urllib.parse import urlsplit, urlunsplit

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel
from apps.sources.choices import PageType


@final
class Source(UUIDAbstractModel, TimestampedAbstractModel):
    """Store one canonical source document, identified by its URL."""

    url = models.URLField(verbose_name=_("url"), unique=True)
    title = models.CharField(verbose_name=_("title"), max_length=512)
    page_type = models.PositiveSmallIntegerField(
        verbose_name=_("page type"),
        choices=PageType.choices,
        default=PageType.OTHER,
    )
    is_hidden = models.BooleanField(
        verbose_name=_("is hidden"),
        default=False,
    )
    published_timestamp = models.DateTimeField(
        _("published at"),
        blank=True,
        editable=False,
        null=True,
    )

    class Meta:
        """Configure source metadata."""

        verbose_name = _("source")
        verbose_name_plural = _("sources")

    @staticmethod
    def normalize_url(url: str) -> str:
        """Return a canonical URL for dedup: no fragment, no trailing slash."""
        parts = urlsplit(url.strip())
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme, parts.netloc, path, parts.query, ""))

    @override
    def __str__(self) -> str:
        """Return the source title and URL."""
        return f"{self.title} ({self.url})"
