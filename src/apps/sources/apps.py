from typing import final

from django.apps import AppConfig


@final
class SourcesConfig(AppConfig):
    """Configure the sources application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sources"
