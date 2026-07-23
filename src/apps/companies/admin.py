from typing import final

from django.contrib import admin

from apps.companies.models import Company
from apps.scans.models import Scan


@final
class ScanInline(admin.TabularInline):  # type: ignore[type-arg]
    """Show company scans inside company administration."""

    can_delete = False
    extra = 0
    fields = (
        "status",
        "pages_scanned",
        "report",
        "error",
        "created_timestamp",
        "updated_timestamp",
    )
    model = Scan
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class CompanyAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure company administration."""

    list_display = (
        "id",
        "name",
        "scan_enabled",
        "last_scanned_at",
    )
    list_display_links = ("id",)
    list_filter = ("scan_enabled", "last_scanned_at")
    ordering = ("name",)
    inlines = (ScanInline,)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = ("name",)


admin.site.register(Company, CompanyAdmin)
