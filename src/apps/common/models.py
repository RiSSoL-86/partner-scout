import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDAbstractModel(models.Model):
    """Provide a UUID primary key for inherited models."""

    id = models.UUIDField(
        _("ID"), editable=False, default=uuid.uuid7, primary_key=True
    )

    class Meta:
        """Configure the model as abstract."""

        abstract = True


class TimeStampedAbstractModel(models.Model):
    """Shortcut for adding up creation and update timestamps."""

    created_timestamp = models.DateTimeField(
        _("created at"), auto_now_add=True, editable=False
    )
    updated_timestamp = models.DateTimeField(
        _("updated at"), auto_now=True, editable=False
    )

    class Meta:
        """Configure the model as abstract."""

        abstract = True
