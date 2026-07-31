from typing import final

from django.contrib import admin

from apps.scans.models import (
    PersonSnapshot,
    Scan,
    ScanSource,
)


@final
class ScanSourceInline(admin.TabularInline):  # type: ignore[type-arg]
    """Show scan sources inside scan administration."""

    can_delete = False
    extra = 0
    fields = ("source",)
    model = ScanSource
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class PersonSnapshotInline(admin.TabularInline):  # type: ignore[type-arg]
    """Show person snapshots inside scan administration."""

    can_delete = False
    extra = 0
    fields = (
        "person",
        "position_type",
        "work_status",
        "specialization",
        "practice_area",
        "role_title",
        "organizational_unit",
        "email",
        "phone",
        "confirmation_level",
    )
    model = PersonSnapshot
    ordering = ("person__normalized_name",)
    readonly_fields = fields
    show_change_link = True


@final
class ScanAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure scan administration."""

    autocomplete_fields = ("company",)
    list_display = (
        "id",
        "company",
        "scan_status",
        "pages_scanned",
        "aggregation_status",
    )
    list_display_links = ("id",)
    list_filter = ("scan_status", "aggregation_status")
    ordering = ("-created_timestamp",)
    inlines = (ScanSourceInline, PersonSnapshotInline)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = (
        "company__name",
        "scan_report",
        "scan_error",
        "aggregation_report",
        "aggregation_error",
    )


@final
class ScanSourceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure scan source administration."""

    autocomplete_fields = ("scan", "source")
    list_display = (
        "id",
        "scan",
        "source",
    )
    list_display_links = ("id",)
    ordering = ("-created_timestamp",)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = (
        "scan__company__name",
        "source__title",
        "source__url",
    )


@final
class PersonSnapshotAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure person snapshot administration."""

    autocomplete_fields = ("scan", "person")
    list_display = (
        "id",
        "scan",
        "person",
        "position_type",
        "work_status",
        "role_title",
        "organizational_unit",
        "confirmation_level",
    )
    list_display_links = ("id",)
    list_filter = (
        "position_type",
        "work_status",
        "specialization",
        "practice_area",
        "confirmation_level",
    )
    ordering = ("-created_timestamp",)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = (
        "scan__company__name",
        "person__first_name",
        "person__middle_name",
        "person__last_name",
        "person__normalized_name",
        "role_title",
        "organizational_unit",
        "email",
        "phone",
    )


admin.site.register(Scan, ScanAdmin)
admin.site.register(ScanSource, ScanSourceAdmin)
admin.site.register(PersonSnapshot, PersonSnapshotAdmin)
