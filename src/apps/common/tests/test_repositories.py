from apps.companies.models import Company
from apps.companies.repository import CompanyRepository
from apps.persons.models import Person, PersonMention
from apps.persons.repository import PersonMentionRepository, PersonRepository
from apps.scans.models import PersonSnapshot, Scan, ScanSource
from apps.scans.repository import (
    PersonSnapshotRepository,
    ScanRepository,
    ScanSourceRepository,
)
from apps.sources.models import Source
from apps.sources.repository import SourceRepository


def test_domain_repositories_bind_expected_models() -> None:
    """Bind every domain repository to the model it persists."""
    assert CompanyRepository.model is Company
    assert ScanRepository.model is Scan
    assert ScanSourceRepository.model is ScanSource
    assert PersonSnapshotRepository.model is PersonSnapshot
    assert SourceRepository.model is Source
    assert PersonRepository.model is Person
    assert PersonMentionRepository.model is PersonMention
