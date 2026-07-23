from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class ScanStatus(models.IntegerChoices):
    """List scan lifecycle statuses."""

    PENDING = 0, _("pending")
    RUNNING = 1, _("running")
    COMPLETED = 2, _("completed")
    FAILED = 3, _("failed")


@final
class PositionType(models.IntegerChoices):
    """List recognized company role types."""

    PARTNER = 0, _("partner")
    DIRECTOR = 1, _("director")
    OTHER = 2, _("other")


@final
class ConfirmationLevel(models.IntegerChoices):
    """List confidence levels for extracted scan facts."""

    CONFIRMED = 0, _("confirmed")
    HIGH = 1, _("high")
    LOW = 2, _("low")
