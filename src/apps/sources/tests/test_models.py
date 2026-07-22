import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.companies.models import Company
from apps.scans.models import Scan
from apps.sources.choices import PageType
from apps.sources.models import Source


def create_scan() -> Scan:
    """Create a scan for source model tests."""
    company = Company.objects.create(
        name="Example Consulting",
        website_url="https://example.com",
    )
    return Scan.objects.create(company=company)


@pytest.mark.django_db
def test_source_defaults() -> None:
    """Create a source without a publication timestamp."""
    scan = create_scan()

    source = Source.objects.create(
        scan=scan,
        url="https://example.com/team",
        title="Team",
        content="Leadership profile page.",
        content_hash="hash-team-page",
    )

    assert source.page_type == PageType.OTHER
    assert source.published_timestamp is None
    assert source.created_timestamp is not None
    assert source.updated_timestamp is not None
    assert str(source) == f"{source.id} (Example Consulting)"
    assert list(scan.sources.all()) == [source]


@pytest.mark.django_db
def test_source_accepts_publication_timestamp() -> None:
    """Store a known publication timestamp when one is discovered."""
    scan = create_scan()
    published_timestamp = timezone.now()

    source = Source.objects.create(
        scan=scan,
        url="https://example.com/news",
        title="News",
        page_type=PageType.NEWS,
        published_timestamp=published_timestamp,
        content="Company news page.",
        content_hash="hash-news-page",
    )

    assert source.page_type == PageType.NEWS
    assert source.published_timestamp == published_timestamp


@pytest.mark.django_db
def test_source_content_hash_is_unique() -> None:
    """Reject duplicate content hashes across sources."""
    scan = create_scan()
    Source.objects.create(
        scan=scan,
        url="https://example.com/first",
        title="First",
        content="First page.",
        content_hash="duplicate-hash",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        Source.objects.create(
            scan=scan,
            url="https://example.com/second",
            title="Second",
            content="Second page.",
            content_hash="duplicate-hash",
        )


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
