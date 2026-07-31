import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.sources.choices import PageType
from apps.sources.models import Source


@pytest.mark.django_db
def test_source_defaults() -> None:
    """Create a source without a publication timestamp."""
    source = Source.objects.create(
        url="https://example.com/team",
        title="Team",
    )

    assert source.page_type == PageType.OTHER
    assert source.published_timestamp is None
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
    )

    assert source.page_type == PageType.NEWS
    assert source.published_timestamp == published_timestamp


@pytest.mark.django_db
def test_source_url_is_unique() -> None:
    """Reject a second source that reuses an existing URL."""
    Source.objects.create(url="https://example.com/team", title="First")

    with pytest.raises(IntegrityError), transaction.atomic():
        Source.objects.create(url="https://example.com/team", title="Second")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://example.com/team/", "https://example.com/team"),
        ("https://example.com/team#staff", "https://example.com/team"),
        ("https://example.com/", "https://example.com/"),
        ("https://example.com/p?id=1", "https://example.com/p?id=1"),
    ],
)
def test_source_normalize_url(raw: str, expected: str) -> None:
    """Drop trailing slash and fragment when canonicalizing a URL."""
    assert Source.normalize_url(raw) == expected


def test_source_url_field_is_unique() -> None:
    """Expose URL as the unique identity of a source."""
    assert Source._meta.get_field("url").unique is True


def test_source_indexes_are_declared() -> None:
    """Declare indexes used by source lookup and filtering."""
    indexes = {index.name: index for index in Source._meta.indexes}

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
