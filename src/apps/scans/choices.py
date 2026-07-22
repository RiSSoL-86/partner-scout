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
