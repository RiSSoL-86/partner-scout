from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class MentionType(models.IntegerChoices):
    """List how a person appears within a single source."""

    PROFILE = 0, _("profile")
    ORG_UNIT = 1, _("organizational unit")
    OTHER = 2, _("other")
