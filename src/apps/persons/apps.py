from typing import final

from django.apps import AppConfig


@final
class PersonsConfig(AppConfig):
    """Configure the persons application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.persons"
