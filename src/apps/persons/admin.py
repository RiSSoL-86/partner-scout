from typing import final

from django.contrib import admin

from apps.persons.models import Person, PersonMention
from apps.scans.models import PersonSnapshot


@final
class SourceMentionInline(admin.TabularInline):  # type: ignore[type-arg]
    """Manage source mentions inside person administration."""

    can_delete = False
    extra = 0
    fields = (
        "scan",
        "source",
        "mention_type",
        "context",
        "created_timestamp",
        "updated_timestamp",
    )
    max_num = 0
    model = PersonMention
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class PersonSnapshotInline(admin.TabularInline):  # type: ignore[type-arg]
    """Show scan snapshots inside person administration."""

    can_delete = False
    extra = 0
    fields = (
        "scan",
        "position_type",
        "work_status",
        "specialization",
        "practice_area",
        "role_title",
        "organizational_unit",
        "email",
        "phone",
        "confirmation_level",
        "created_timestamp",
        "updated_timestamp",
    )
    max_num = 0
    model = PersonSnapshot
    ordering = ("-created_timestamp",)
    readonly_fields = fields
    show_change_link = True


@final
class PersonAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure person administration."""

    list_display = ("id", "normalized_name")
    list_display_links = ("id",)
    inlines = (SourceMentionInline, PersonSnapshotInline)
    ordering = ("normalized_name",)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = ("normalized_name",)


@final
class PersonMentionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Configure person mention administration."""

    list_display = (
        "id",
        "person",
        "scan",
        "source",
        "mention_type",
    )
    list_display_links = ("id",)
    list_filter = ("mention_type",)
    ordering = ("-created_timestamp",)
    readonly_fields = ("id", "created_timestamp", "updated_timestamp")
    search_fields = (
        "person__normalized_name",
        "scan__company__name",
        "source__title",
        "source__url",
    )


admin.site.register(Person, PersonAdmin)
admin.site.register(PersonMention, PersonMentionAdmin)
