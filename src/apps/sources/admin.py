from typing import final

from django.contrib import admin

from apps.sources.models import Source


@final
class SourceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure source administration."""

    autocomplete_fields = ("scan",)
    list_display = (
        "id",
        "title",
        "url",
        "scan",
        "page_type",
        "published_timestamp",
        "created_timestamp",
        "updated_timestamp",
    )
    list_display_links = ("id",)
    list_filter = ("page_type", "published_timestamp", "created_timestamp")
    ordering = ("-created_timestamp",)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = (
        "title",
        "url",
        "content_hash",
        "scan__company__name",
    )


admin.site.register(Source, SourceAdmin)
