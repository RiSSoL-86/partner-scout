from typing import TYPE_CHECKING, Any, final

from aiogram.utils.formatting import (
    Text,
    as_line,
    as_list,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

    from apps.persons.models import Person


@final
class PersonMentionsView:
    """Build Telegram message payloads for the person card."""

    @staticmethod
    def build_person_message(
        keyboard: InlineKeyboardMarkup,
        person: Person,
        total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying one person card."""
        header = as_line(person.normalized_name, " 👤:")
        if total:
            content = as_list(
                header,
                as_line(f"Mentions {total} 📎"),
            )
        else:
            content = as_list(
                header,
                Text("No mentions found for this person 🤷‍♂️"),
            )

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }
