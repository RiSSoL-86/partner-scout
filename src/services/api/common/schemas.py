from typing import TYPE_CHECKING, final

from pydantic import AliasGenerator, BaseModel, ConfigDict, alias_generators

if TYPE_CHECKING:
    from django.db.models import IntegerChoices


class CamelCaseModel(BaseModel):
    """Serialize model fields with camel-case aliases."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=alias_generators.to_camel,
            serialization_alias=alias_generators.to_camel,
        ),
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
    )


@final
class ReportQuery(BaseModel):
    """Query parameters carrying the signed report link token."""

    token: str


@final
class ChoiceOption(CamelCaseModel):
    """One selectable choice value with its English label."""

    value: int
    label: str


def build_choice_options(
    choices: type[IntegerChoices],
) -> list[ChoiceOption]:
    """Build choice options from an IntegerChoices enum."""
    return [
        ChoiceOption(value=int(value), label=str(label))
        for value, label in choices.choices
    ]
