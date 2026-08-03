from typing import TYPE_CHECKING

from apps.persons.choices import MentionType
from apps.scans.choices import ConfirmationLevel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from apps.persons.models import PersonMention


def compute_confirmation_level(
    mentions: Sequence[PersonMention],
) -> ConfirmationLevel:
    """Rate how confidently a person belongs to the company."""
    source_ids = {mention.source_id for mention in mentions}
    types = {mention.mention_type for mention in mentions}

    if MentionType.PROFILE in types or MentionType.ORG_UNIT in types:
        return ConfirmationLevel.CONFIRMED
    if len(source_ids) > 2:
        return ConfirmationLevel.PROBABLE
    return ConfirmationLevel.UNLIKELY
