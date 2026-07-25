import factory
from factory.django import DjangoModelFactory

from apps.companies.models import Company


class CompanyFactory(DjangoModelFactory[Company]):
    """Build companies with valid defaults for tests."""

    class Meta:
        """Configure the generated Django model."""

        model = Company

    name = factory.Sequence(lambda n: f"Company {n}")
    website_url = factory.Sequence(
        lambda n: f"https://company-{n}.example.com",
    )
    scan_enabled = True
