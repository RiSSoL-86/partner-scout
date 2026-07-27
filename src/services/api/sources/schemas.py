from typing import Self, final

from apps.sources.choices import PageType
from services.api.common.schemas import (
    CamelCaseModel,
    ChoiceOption,
    build_choice_options,
)


@final
class SourceChoices(CamelCaseModel):
    """Choice fields of the source entity."""

    page_type: list[ChoiceOption]


@final
class SourceChoicesResponse(CamelCaseModel):
    """Selectable choice values for sources."""

    source: SourceChoices

    @classmethod
    def build(cls) -> Self:
        """Assemble the source-related choice values from the enums."""
        return cls(
            source=SourceChoices(
                page_type=build_choice_options(PageType),
            ),
        )
