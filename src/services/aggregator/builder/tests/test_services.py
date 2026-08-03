import pytest
from asgiref.sync import sync_to_async

from apps.persons.choices import MentionType
from apps.persons.tests.factories import PersonFactory, PersonMentionFactory
from apps.scans.choices import (
    ConfirmationLevel,
    PositionType,
    PracticeArea,
    Specialization,
    WorkStatus,
)
from apps.scans.tests.factories import ScanFactory
from services.aggregator.builder.services import (
    BuilderPersonSnapshotService,
)
from services.aggregator.schemas import AiClassification, ScanPersonMentions

pytestmark = pytest.mark.django_db(transaction=True)

create_scan = sync_to_async(ScanFactory)
create_person = sync_to_async(PersonFactory)
create_mention = sync_to_async(PersonMentionFactory)


def make_classification(
    person_id: str, **overrides: object
) -> AiClassification:
    """Build an LLM classification with valid defaults for one person."""
    fields: dict[str, object] = {
        "person_id": person_id,
        "position_type": PositionType.PARTNER,
        "work_status": WorkStatus.FRONT_LINE,
        "specialization": Specialization.FUNCTIONAL,
        "practice_area": PracticeArea.AUDIT,
        "role_title": "Partner",
    }
    fields.update(overrides)
    return AiClassification(**fields)  # type: ignore[arg-type]


async def test_builds_one_snapshot_per_classified_person() -> None:
    """Map each person's classification onto a persisted-ready snapshot."""
    scan = await create_scan()
    person = await create_person()
    mention = await create_mention(
        scan=scan, person=person, mention_type=MentionType.PROFILE
    )
    scan_person_mentions = ScanPersonMentions(
        person_by_id={person.id: person},
        mentions_by_person={person.id: [mention]},
    )
    classification = make_classification(
        str(person.id),
        position_type=PositionType.DIRECTOR,
        role_title="Managing Director",
        organizational_unit="Audit",
    )

    snapshots = await BuilderPersonSnapshotService().execute(
        scan=scan,
        scan_person_mentions=scan_person_mentions,
        classifications={str(person.id): classification},
    )

    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.person_id == person.id
    assert snapshot.position_type == PositionType.DIRECTOR
    assert snapshot.role_title == "Managing Director"
    assert snapshot.organizational_unit == "Audit"
    assert snapshot.confirmation_level == ConfirmationLevel.CONFIRMED


async def test_picks_first_non_empty_email_and_phone() -> None:
    """Take the first non-empty email and phone across the mentions."""
    scan = await create_scan()
    person = await create_person()
    blank = await create_mention(scan=scan, person=person, email="", phone="")
    filled = await create_mention(
        scan=scan,
        person=person,
        email="p@example.com",
        phone="+7 900 000-00-00",
    )
    scan_person_mentions = ScanPersonMentions(
        person_by_id={person.id: person},
        mentions_by_person={person.id: [blank, filled]},
    )

    snapshots = await BuilderPersonSnapshotService().execute(
        scan=scan,
        scan_person_mentions=scan_person_mentions,
        classifications={str(person.id): make_classification(str(person.id))},
    )

    assert snapshots[0].email == "p@example.com"
    assert snapshots[0].phone == "+7 900 000-00-00"


async def test_skips_a_person_without_a_classification() -> None:
    """Drop people the LLM returned no classification for."""
    scan = await create_scan()
    person = await create_person()
    mention = await create_mention(scan=scan, person=person)
    scan_person_mentions = ScanPersonMentions(
        person_by_id={person.id: person},
        mentions_by_person={person.id: [mention]},
    )

    snapshots = await BuilderPersonSnapshotService().execute(
        scan=scan,
        scan_person_mentions=scan_person_mentions,
        classifications={},
    )

    assert snapshots == []
