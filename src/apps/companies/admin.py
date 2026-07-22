from __future__ import annotations

from typing import TYPE_CHECKING, final, override

from django.contrib import admin

from apps.companies.models import Company
from apps.scans.models import Scan

if TYPE_CHECKING:
    from django.http import HttpRequest


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

    @override
    def has_add_permission(  # type: ignore[override]
        self,
        request: HttpRequest,
        obj: object,
    ) -> bool:
        """Disable creating scans from the company inline."""
        return False


@final
class CompanyAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure company administration."""

    list_display = (
        "id",
        "name",
        "website_url",
        "scan_enabled",
        "last_scanned_at",
        "created_timestamp",
        "updated_timestamp",
    )
    list_display_links = ("id",)
    list_filter = ("scan_enabled", "created_timestamp", "last_scanned_at")
    ordering = ("name",)
    inlines = (ScanInline,)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = ("name", "website_url")


admin.site.register(Company, CompanyAdmin)
