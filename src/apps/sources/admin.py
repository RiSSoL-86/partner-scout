from typing import final

from django.contrib import admin

from apps.persons.models import PersonMention
from apps.scans.models import PersonSnapshot, ScanSource
from apps.sources.models import Source


@final
class PersonMentionInline(admin.TabularInline):  # type: ignore[type-arg]
    """Manage person mentions inside source administration."""

    can_delete = False
    extra = 0
    fields = (
        "person",
        "mention_type",
        "context",
    )
    max_num = 0
    model = PersonMention
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class ScanSourceInline(admin.TabularInline):  # type: ignore[type-arg]
    """Manage scan links inside source administration."""

    can_delete = False
    extra = 0
    fields = ("scan",)
    model = ScanSource
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class PersonSnapshotInline(admin.TabularInline):  # type: ignore[type-arg]
    """Show person snapshots using this source as evidence."""

    can_delete = False
    extra = 0
    fields = (
        "scan",
        "person",
        "position_type",
        "role_title",
        "organizational_unit",
        "confirmation_level",
    )
    max_num = 0
    model = PersonSnapshot
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class SourceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure source administration."""

    list_display = (
        "id",
        "title",
        "url",
        "page_type",
        "published_timestamp",
    )
    list_display_links = ("id",)
    list_filter = (
        "page_type",
        "published_timestamp",
    )
    inlines = (
        ScanSourceInline,
        PersonMentionInline,
        PersonSnapshotInline,
    )
    ordering = ("-created_timestamp",)
    readonly_fields = (
        "id",
        "content_hash",
        "created_timestamp",
        "updated_timestamp",
    )
    search_fields = (
        "title",
        "url",
        "content_hash",
    )


admin.site.register(Source, SourceAdmin)
