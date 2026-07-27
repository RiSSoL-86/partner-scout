from typing import final, override

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel
from apps.scans.choices import (
    ConfirmationLevel,
    PositionType,
    PracticeArea,
    ScanStatus,
    Specialization,
    WorkStatus,
)


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
        indexes = [
            models.Index(
                fields=("company", "created_timestamp"),
                name="scan_company_created_idx",
            ),
            models.Index(
                fields=("status", "created_timestamp"),
                name="scan_status_created_idx",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the scan identifier with the company name."""
        return f"{self.id} ({self.company.name})"


@final
class ScanSource(UUIDAbstractModel, TimestampedAbstractModel):
    """Connect a scan with a source discovered during that scan."""

    scan = models.ForeignKey(
        "scans.Scan",
        on_delete=models.CASCADE,
        related_name="source_links",
        verbose_name=_("scan"),
    )
    source = models.ForeignKey(
        "sources.Source",
        on_delete=models.CASCADE,
        related_name="scan_links",
        verbose_name=_("source"),
    )

    class Meta:
        """Configure scan source metadata and constraints."""

        verbose_name = _("scan source")
        verbose_name_plural = _("scan sources")
        constraints = [
            models.UniqueConstraint(
                fields=("scan", "source"),
                name="unique_source_per_scan",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the scan and source link."""
        return f"{self.scan} -> {self.source}"


@final
class PersonSnapshot(UUIDAbstractModel, TimestampedAbstractModel):
    """Store one partner or director state for a company scan."""

    scan = models.ForeignKey(
        "scans.Scan",
        on_delete=models.CASCADE,
        related_name="person_snapshots",
        verbose_name=_("scan"),
    )
    person = models.ForeignKey(
        "persons.Person",
        on_delete=models.CASCADE,
        related_name="snapshots",
        verbose_name=_("person"),
    )
    position_type = models.PositiveSmallIntegerField(
        verbose_name=_("position type"),
        choices=PositionType.choices,
    )
    work_status = models.PositiveSmallIntegerField(
        verbose_name=_("work status"),
        choices=WorkStatus.choices,
        default=WorkStatus.UNKNOWN,
    )
    specialization = models.PositiveSmallIntegerField(
        verbose_name=_("specialization"),
        choices=Specialization.choices,
        default=Specialization.UNKNOWN,
    )
    practice_area = models.PositiveSmallIntegerField(
        verbose_name=_("practice area"),
        choices=PracticeArea.choices,
        default=PracticeArea.UNKNOWN,
    )
    role_title = models.CharField(verbose_name=_("role title"), max_length=255)
    organizational_unit = models.CharField(
        verbose_name=_("organizational unit"),
        blank=True,
        default="",
        max_length=255,
    )
    email = models.EmailField(verbose_name=_("email"), blank=True, default="")
    phone = models.CharField(
        verbose_name=_("phone number"),
        blank=True,
        default="",
        max_length=50,
    )
    confirmation_level = models.PositiveSmallIntegerField(
        verbose_name=_("confirmation level"),
        choices=ConfirmationLevel.choices,
        default=ConfirmationLevel.UNLIKELY,
    )

    class Meta:
        """Configure person snapshot metadata and constraints."""

        verbose_name = _("person snapshot")
        verbose_name_plural = _("person snapshots")
        constraints = [
            models.UniqueConstraint(
                fields=("scan", "person"),
                name="unique_person_snapshot_per_scan",
            ),
        ]
        indexes = [
            models.Index(
                fields=("scan", "created_timestamp"),
                name="snapshot_scan_created_idx",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the scanned person role."""
        return f"{self.person} - {self.role_title} ({self.scan.company.name})"
