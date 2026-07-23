from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class MentionType(models.IntegerChoices):
    """List recognized person mention types."""

    PROFILE = 0, _("profile")
    TEAM = 1, _("team")
    AUTHOR = 2, _("author")
    INTERVIEW = 3, _("interview")
    QUOTE = 4, _("quote")
    EVENT = 5, _("event")
    OTHER = 6, _("other")
