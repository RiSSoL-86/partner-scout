from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class PageType(models.IntegerChoices):
    """List recognized source page types."""

    PROFILE = 0, _("profile")
    TEAM = 1, _("team")
    PUBLICATION = 2, _("publication")
    INTERVIEW = 3, _("interview")
    NEWS = 4, _("news")
    EVENT = 5, _("event")
    DOCUMENT = 6, _("document")
    OTHER = 7, _("other")
