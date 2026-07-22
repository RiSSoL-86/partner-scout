from typing import final, override

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel
from apps.sources.choices import PageType


@final
class Source(UUIDAbstractModel, TimestampedAbstractModel):
    """Store one page discovered during a scan."""

    scan = models.ForeignKey(
        "scans.Scan",
        on_delete=models.CASCADE,
        related_name="sources",
        verbose_name=_("scan"),
    )
    url = models.URLField(verbose_name=_("url"))
    title = models.CharField(verbose_name=_("title"), max_length=255)
    page_type = models.PositiveSmallIntegerField(
        verbose_name=_("page type"),
        choices=PageType.choices,
        default=PageType.OTHER,
    )
    published_timestamp = models.DateTimeField(
        _("published at"),
        blank=True,
        editable=False,
        null=True,
    )
    content = models.TextField(verbose_name=_("content"))
    content_hash = models.CharField(
        verbose_name=_("content hash"),
        max_length=64,
        unique=True,
    )

    class Meta:
        """Configure source metadata."""

        verbose_name = _("source")
        verbose_name_plural = _("sources")

    @override
    def __str__(self) -> str:
        """Return the source identifier with the company name."""
        return f"{self.id} ({self.scan.company.name})"
