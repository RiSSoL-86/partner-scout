from typing import final

from django.contrib import admin

from apps.persons.models import PersonMention
from apps.scans.models import ScanSource
from apps.sources.models import Source


@final
class PersonMentionInline(admin.TabularInline):  # type: ignore[type-arg]
    """Manage person mentions inside source administration."""

    can_delete = False
    extra = 0
    fields = (
        "scan",
        "person",
        "mention_type",
        "role_title",
        "email",
        "phone",
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
class SourceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure source administration."""

    list_display = (
        "id",
        "title",
        "url",
        "page_type",
        "is_hidden",
        "published_timestamp",
    )
    list_display_links = ("id",)
    list_filter = (
        "page_type",
        "is_hidden",
        "published_timestamp",
    )
    inlines = (
        ScanSourceInline,
        PersonMentionInline,
    )
    ordering = ("-created_timestamp",)
    readonly_fields = (
        "id",
        "created_timestamp",
        "updated_timestamp",
    )
    search_fields = (
        "title",
        "url",
    )


admin.site.register(Source, SourceAdmin)
