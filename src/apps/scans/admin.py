from typing import final

from django.contrib import admin

from apps.scans.models import Scan
from apps.sources.models import Source


@final
class SourceInline(admin.TabularInline):  # type: ignore[type-arg]
    """Show scan sources inside scan administration."""

    can_delete = False
    extra = 0
    fields = (
        "id",
        "title",
        "url",
        "page_type",
        "published_timestamp",
        "content_hash",
        "created_timestamp",
        "updated_timestamp",
    )
    max_num = 0
    model = Source
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class ScanAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure scan administration."""

    autocomplete_fields = ("company",)
    list_display = (
        "id",
        "company",
        "status",
        "pages_scanned",
        "created_timestamp",
        "updated_timestamp",
    )
    list_display_links = ("id",)
    list_filter = ("status", "created_timestamp", "updated_timestamp")
    ordering = ("-created_timestamp",)
    inlines = (SourceInline,)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = ("company__name", "report", "error")


admin.site.register(Scan, ScanAdmin)
