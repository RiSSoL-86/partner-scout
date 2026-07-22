from typing import final, override

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel
from apps.scans.choices import ScanStatus


@final
class Scan(UUIDAbstractModel, TimestampedAbstractModel):
    """Record one company website scan and its outcome."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="scans",
        verbose_name=_("company"),
    )
    status = models.PositiveSmallIntegerField(
        verbose_name=_("scan status"),
        choices=ScanStatus.choices,
        default=ScanStatus.PENDING,
    )
    pages_scanned = models.PositiveIntegerField(
        verbose_name=_("pages scanned"),
        default=0,
    )
    report = models.TextField(verbose_name=_("report"), blank=True, default="")
    error = models.TextField(verbose_name=_("error"), blank=True, default="")

    class Meta:
        """Configure scan metadata and active-scan uniqueness."""

        verbose_name = _("scan")
        verbose_name_plural = _("scans")

        constraints = [
            models.UniqueConstraint(
                fields=("company",),
                condition=models.Q(
                    status__in=(ScanStatus.PENDING, ScanStatus.RUNNING),
                ),
                name="unique_active_scan_per_company",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the scan identifier with the company name."""
        return f"{self.id} ({self.company.name})"
