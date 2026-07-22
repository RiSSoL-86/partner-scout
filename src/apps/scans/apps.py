from typing import final

from django.apps import AppConfig


@final
class ScansConfig(AppConfig):
    """Configure the scans application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.scans"
