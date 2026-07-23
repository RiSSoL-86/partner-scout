from typing import final, override

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel


@final
class Company(UUIDAbstractModel, TimestampedAbstractModel):
    """Represent a company monitored by the scouting service."""

    name = models.CharField(_("name"), max_length=255)
    website_url = models.URLField(_("website URL"))
    scan_enabled = models.BooleanField(_("scan enabled"), default=True)
    last_scanned_at = models.DateTimeField(
        _("last scanned at"),
        blank=True,
        default=None,
        null=True,
    )

    class Meta:
        """Configure company metadata and constraints."""

        verbose_name = _("company")
        verbose_name_plural = _("companies")

        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_company_name",
            ),
            models.UniqueConstraint(
                Lower("website_url"),
                name="unique_company_website_url",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the company name."""
        return self.name
