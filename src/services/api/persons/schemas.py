from typing import Self, final

from apps.persons.choices import MentionType
from services.api.common.schemas import (
    CamelCaseModel,
    ChoiceOption,
    build_choice_options,
)


@final
class PersonMentionChoices(CamelCaseModel):
    """Choice fields of the person mention entity."""

    mention_type: list[ChoiceOption]


@final
class PersonChoicesResponse(CamelCaseModel):
    """Selectable choice values for person mentions."""

    person_mention: PersonMentionChoices

    @classmethod
    def build(cls) -> Self:
        """Assemble the person-related choice values from the enums."""
        return cls(
            person_mention=PersonMentionChoices(
                mention_type=build_choice_options(MentionType),
            ),
        )
