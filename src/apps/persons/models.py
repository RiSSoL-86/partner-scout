from typing import final, override

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimestampedAbstractModel, UUIDAbstractModel
from apps.persons.choices import MentionType


@final
class Person(UUIDAbstractModel, TimestampedAbstractModel):
    """Store a canonical person identity shared across scans."""

    first_name = models.CharField(_("first name"), max_length=100)
    middle_name = models.CharField(
        _("middle name"),
        blank=True,
        default="",
        max_length=100,
    )
    last_name = models.CharField(_("last name"), max_length=100)
    normalized_name = models.CharField(_("normalized name"), max_length=255)

    class Meta:
        """Configure person metadata."""

        verbose_name = _("person")
        verbose_name_plural = _("persons")

        constraints = [
            models.UniqueConstraint(
                Lower("normalized_name"),
                name="unique_normalized_name_name",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the normalized name."""
        return self.normalized_name


@final
class PersonMention(UUIDAbstractModel, TimestampedAbstractModel):
    """Connect a person to a source where they were mentioned."""

    person = models.ForeignKey(
        "persons.Person",
        on_delete=models.CASCADE,
        related_name="source_mentions",
        verbose_name=_("person"),
    )
    source = models.ForeignKey(
        "sources.Source",
        on_delete=models.CASCADE,
        related_name="person_mentions",
        verbose_name=_("source"),
    )
    mention_type = models.PositiveSmallIntegerField(
        verbose_name=_("mention type"),
        choices=MentionType.choices,
        default=MentionType.OTHER,
    )
    context = models.TextField(verbose_name=_("context"))

    class Meta:
        """Configure person mention metadata."""

        verbose_name = _("person mention")
        verbose_name_plural = _("persons mentions")
        constraints = [
            models.UniqueConstraint(
                fields=("person", "source"),
                name="unique_person_source_mention",
            ),
        ]

    @override
    def __str__(self) -> str:
        """Return the person and source link."""
        return f"{self.person} in {self.source}"
