from typing import final

from django.apps import AppConfig


@final
class CompaniesConfig(AppConfig):
    """Configure the companies application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.companies"
