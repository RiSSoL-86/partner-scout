import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.persons.admin import (
    PersonAdmin,
    PersonMentionAdmin,
    SourceMentionInline,
)
from apps.persons.models import Person, PersonMention
from apps.sources.admin import (
    PersonMentionInline,
    SourceAdmin,
)
from apps.sources.admin import (
    PersonSnapshotInline as SourcePersonSnapshotInline,
)
from apps.sources.admin import (
    ScanSourceInline as SourceScanSourceInline,
)
from apps.sources.models import Source


def create_person() -> Person:
    """Create a person for person mention admin tests."""
    return Person.objects.create(
        first_name="Ivan",
        last_name="Petrov",
        normalized_name="ivan petrov",
    )


def create_source() -> Source:
    """Create a source for person mention admin tests."""
    return Source.objects.create(
        url="https://example.com/team",
        title="Team",
        content="Leadership profile page.",
    )


@pytest.fixture
def admin_client() -> Client:
    """Return an authenticated admin client."""
    user_model = get_user_model()
    user = user_model.objects.create_superuser(
        email="admin@example.com",
        password="password",
        first_name="Admin",
        last_name="User",
    )
    client = Client()
    client.force_login(user)
    return client


def test_person_admin_registers_person_mention_inline() -> None:
    """Expose person mentions from the person admin page."""
    person_admin = admin.site._registry[Person]

    assert isinstance(person_admin, PersonAdmin)
    assert SourceMentionInline in person_admin.inlines


def test_source_mention_inline_configuration() -> None:
    """Configure inline editing for source mentions."""
    assert SourceMentionInline.model is PersonMention
    assert SourceMentionInline.can_delete is False
    assert SourceMentionInline.extra == 0
    assert SourceMentionInline.max_num == 0
    assert SourceMentionInline.show_change_link is True
    assert SourceMentionInline.readonly_fields == SourceMentionInline.fields
    assert SourceMentionInline.fields == (
        "source",
        "mention_type",
        "context",
        "created_timestamp",
        "updated_timestamp",
    )


def test_source_admin_registers_person_mention_inline() -> None:
    """Expose source relationships from the source admin page."""
    source_admin = admin.site._registry[Source]

    assert isinstance(source_admin, SourceAdmin)
    assert source_admin.inlines == (
        SourceScanSourceInline,
        PersonMentionInline,
        SourcePersonSnapshotInline,
    )


def test_source_person_mention_inline_configuration() -> None:
    """Configure inline editing for source person mentions."""
    assert PersonMentionInline.model is PersonMention
    assert PersonMentionInline.can_delete is False
    assert PersonMentionInline.extra == 0
    assert PersonMentionInline.max_num == 0
    assert PersonMentionInline.show_change_link is True
    assert PersonMentionInline.readonly_fields == PersonMentionInline.fields
    assert PersonMentionInline.fields == (
        "person",
        "mention_type",
        "context",
    )


def test_source_scan_source_inline_configuration() -> None:
    """Configure inline editing for source scan links."""
    assert SourceScanSourceInline.extra == 0
    assert SourceScanSourceInline.fields == ("scan",)
    assert SourceScanSourceInline.readonly_fields == ("scan",)


def test_source_person_snapshot_inline_configuration() -> None:
    """Configure read-only inline display for source snapshots."""
    assert SourcePersonSnapshotInline.can_delete is False
    assert SourcePersonSnapshotInline.extra == 0
    assert SourcePersonSnapshotInline.max_num == 0
    assert SourcePersonSnapshotInline.readonly_fields == (
        "scan",
        "person",
        "position_type",
        "role_title",
        "organizational_unit",
        "confirmation_level",
    )


def test_person_mention_admin_registration() -> None:
    """Register person mentions as a standalone admin section."""
    person_mention_admin = admin.site._registry[PersonMention]

    assert isinstance(person_mention_admin, PersonMentionAdmin)
    assert person_mention_admin.list_display == (
        "id",
        "person",
        "source",
        "mention_type",
    )
    assert person_mention_admin.list_filter == ("mention_type",)
    assert person_mention_admin.search_fields == (
        "person__normalized_name",
        "source__title",
        "source__url",
    )


@pytest.mark.django_db
def test_person_mention_admin_pages_are_available(
    admin_client: Client,
) -> None:
    """Open person mention admin pages as a superuser."""
    person = create_person()
    source = create_source()
    mention = PersonMention.objects.create(
        person=person,
        source=source,
        context="Ivan Petrov is listed as a partner.",
    )

    urls = (
        reverse("admin:persons_personmention_changelist"),
        reverse("admin:persons_personmention_add"),
        reverse("admin:persons_personmention_change", args=(mention.pk,)),
    )

    for url in urls:
        response = admin_client.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
def test_person_admin_change_page_shows_mentions_inline(
    admin_client: Client,
) -> None:
    """Open person admin change page with person mention inline."""
    person = create_person()
    source = create_source()
    PersonMention.objects.create(
        person=person,
        source=source,
        context="Ivan Petrov is listed as a partner.",
    )

    response = admin_client.get(
        reverse("admin:persons_person_change", args=(person.pk,))
    )

    assert response.status_code == 200
    inline_models = {
        formset.opts.model
        for formset in response.context_data["inline_admin_formsets"]
    }
    assert PersonMention in inline_models


@pytest.mark.django_db
def test_source_admin_change_page_shows_mentions_inline(
    admin_client: Client,
) -> None:
    """Open source admin change page with person mention inline."""
    person = create_person()
    source = create_source()
    PersonMention.objects.create(
        person=person,
        source=source,
        context="Ivan Petrov is listed as a partner.",
    )

    response = admin_client.get(
        reverse("admin:sources_source_change", args=(source.pk,))
    )

    assert response.status_code == 200
    inline_models = {
        formset.opts.model
        for formset in response.context_data["inline_admin_formsets"]
    }
    assert PersonMention in inline_models
