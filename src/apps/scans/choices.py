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
    """List recognized partner-level position types."""

    PARTNER = 0, _("partner")
    DIRECTOR = 1, _("director")


@final
class WorkStatus(models.IntegerChoices):
    """List employment states in client priority order."""

    UNKNOWN = 0, _("unknown")
    FRONT_ACTIVE = 1, _("frontline active")
    FRONT_INACTIVE = 2, _("frontline inactive")
    BACK_OFFICE = 3, _("back office")
    NOT_EMPLOYEE = 4, _("not employee")


@final
class Specialization(models.IntegerChoices):
    """List recognized person specializations."""

    UNKNOWN = 0, _("unknown")
    INDUSTRIAL = 1, _("industrial")
    FUNCTIONAL = 2, _("functional")


@final
class PracticeArea(models.IntegerChoices):
    """List recognized organizational practice areas."""

    UNKNOWN = 0, _("unknown")
    AUDIT = 1, _("audit")
    TAX_LEGAL = 2, _("tax and legal")
    CONSULTING_DEALS = 3, _("consulting and deals")


@final
class ConfirmationLevel(models.IntegerChoices):
    """List confidence levels for a person working at the company."""

    CONFIRMED = 0, _("confirmed")
    PROBABLE = 1, _("probable")
    UNLIKELY = 2, _("unlikely")
