from typing import TYPE_CHECKING, Any, final

from aiogram.utils.formatting import (
    Text,
    as_line,
    as_list,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from aiogram.types import InlineKeyboardMarkup

    from apps.persons.models import Person, PersonMention


@final
class PersonMentionView:
    """Build Telegram message payloads for person mentions."""

    @staticmethod
    def build_list_message(
        keyboard: InlineKeyboardMarkup,
        person: Person,
        mentions: Sequence[PersonMention],
        offset: int,
        total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying a page of a person mentions."""
        header = as_line(person.normalized_name, " 👤:")
        if mentions:
            last = offset + len(mentions)
            content = as_list(
                header,
                as_line(f"Mentions {offset + 1}-{last}/{total} 📎:"),
                *(
                    as_list(
                        as_line(f"{offset + index}. ", mention.source.title),
                        as_line("URL: ", mention.source.url),
                        as_line("Type: ", mention.get_mention_type_display()),
                        as_line(
                            "Seen: ",
                            mention.created_timestamp.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        ),
                        as_line("Context: ", mention.context or "empty"),
                        as_line("\n"),
                    )
                    for index, mention in enumerate(mentions, start=1)
                ),
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
