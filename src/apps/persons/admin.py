from typing import final

from django.contrib import admin

from apps.persons.models import Person


@final
class PersonAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure person administration."""

    list_display = (
        "id",
        "normalized_name",
        "first_name",
        "middle_name",
        "last_name",
        "created_timestamp",
        "updated_timestamp",
    )
    list_display_links = ("id",)
    list_filter = ("created_timestamp",)
    ordering = ("normalized_name",)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = (
        "first_name",
        "middle_name",
        "last_name",
        "normalized_name",
    )


admin.site.register(Person, PersonAdmin)
