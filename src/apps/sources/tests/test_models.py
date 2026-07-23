import hashlib

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.sources.choices import PageType
from apps.sources.models import Source


def build_content_hash(content: str) -> str:
    """Return the expected SHA-256 hash for source content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


@pytest.mark.django_db
def test_source_defaults() -> None:
    """Create a source without a publication timestamp."""
    source = Source.objects.create(
        url="https://example.com/team",
        title="Team",
        content="Leadership profile page.",
    )

    assert source.page_type == PageType.OTHER
    assert source.published_timestamp is None
    assert source.content_hash == build_content_hash(
        "Leadership profile page."
    )
    assert source.created_timestamp is not None
    assert source.updated_timestamp is not None
    assert str(source) == "Team (https://example.com/team)"


@pytest.mark.django_db
def test_source_accepts_publication_timestamp() -> None:
    """Store a known publication timestamp when one is discovered."""
    published_timestamp = timezone.now()

    source = Source.objects.create(
        url="https://example.com/news",
        title="News",
        page_type=PageType.NEWS,
        published_timestamp=published_timestamp,
        content="Company news page.",
    )

    assert source.page_type == PageType.NEWS
    assert source.published_timestamp == published_timestamp


@pytest.mark.django_db
def test_source_content_hash_updates_when_content_changes() -> None:
    """Refresh the stored content hash when source content changes."""
    source = Source.objects.create(
        url="https://example.com/first",
        title="First",
        content="First page.",
    )

    source.content = "Updated page."
    source.save(update_fields={"content"})

    source.refresh_from_db()
    assert source.content_hash == build_content_hash("Updated page.")


@pytest.mark.django_db
def test_source_content_hash_is_unique_for_same_content() -> None:
    """Reject duplicate source content through the generated hash."""
    Source.objects.create(
        url="https://example.com/first",
        title="First",
        content="Duplicate page.",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        Source.objects.create(
            url="https://example.com/second",
            title="Second",
            content="Duplicate page.",
        )


def test_source_content_hash_field_is_generated() -> None:
    """Expose content hash as a generated unique field."""
    content_field = Source._meta.get_field("content")
    content_hash_field = Source._meta.get_field("content_hash")

    assert content_field.unique is False
    assert content_hash_field.unique is True
    assert content_hash_field.editable is False


def test_source_indexes_are_declared() -> None:
    """Declare indexes used by source lookup and filtering."""
    indexes = {index.name: index for index in Source._meta.indexes}

    assert indexes["source_url_idx"].fields == ["url"]
    assert indexes["source_page_type_created_idx"].fields == [
        "page_type",
        "created_timestamp",
    ]


def test_page_type_values() -> None:
    """Expose stable source page type values."""
    assert PageType.PROFILE == 0
    assert PageType.TEAM == 1
    assert PageType.PUBLICATION == 2
    assert PageType.INTERVIEW == 3
    assert PageType.NEWS == 4
    assert PageType.EVENT == 5
    assert PageType.DOCUMENT == 6
    assert PageType.OTHER == 7
