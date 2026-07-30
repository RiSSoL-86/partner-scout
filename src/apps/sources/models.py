from typing import Any, final, override

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel
from apps.common.services.hashing import HashService
from apps.sources.choices import PageType


@final
class Source(UUIDAbstractModel, TimestampedAbstractModel):
    """Store one canonical source document discovered by scans."""

    url = models.URLField(verbose_name=_("url"))
    title = models.CharField(verbose_name=_("title"), max_length=255)
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
    content = models.TextField(verbose_name=_("content"))
    content_hash = models.CharField(
        verbose_name=_("content hash"),
        editable=False,
        max_length=64,
        unique=True,
    )

    class Meta:
        """Configure source metadata."""

        verbose_name = _("source")
        verbose_name_plural = _("sources")
        indexes = [
            models.Index(fields=("url",), name="source_url_idx"),
            models.Index(
                fields=("page_type", "created_timestamp"),
                name="source_page_type_created_idx",
            ),
        ]

    @override
    def clean(self) -> None:
        """Validate source content uniqueness by its generated hash."""
        super().clean()
        self.content_hash = HashService.build_sha256(self.content)

        duplicate_sources = type(self).objects.filter(
            content_hash=self.content_hash,
        )
        if self.pk is not None:
            duplicate_sources = duplicate_sources.exclude(pk=self.pk)

        if duplicate_sources.exists():
            raise ValidationError(
                {
                    "content": _("Source with this content already exists."),
                }
            )

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Store a content hash before saving the source."""
        self.content_hash = HashService.build_sha256(self.content)

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "content" in update_fields:
            kwargs["update_fields"] = {*update_fields, "content_hash"}

        super().save(*args, **kwargs)

    @override
    def __str__(self) -> str:
        """Return the source title and URL."""
        return f"{self.title} ({self.url})"
