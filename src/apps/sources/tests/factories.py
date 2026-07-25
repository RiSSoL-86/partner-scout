import factory
from factory.django import DjangoModelFactory

from apps.sources.choices import PageType
from apps.sources.models import Source


class SourceFactory(DjangoModelFactory[Source]):
    """Build sources with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = Source

    url = factory.Sequence(lambda n: f"https://src{n}.example.com/page")
    title = factory.Sequence(lambda n: f"Source page #{n}")
    page_type = PageType.PROFILE
    content = factory.Sequence(lambda n: f"Source content {n}")
