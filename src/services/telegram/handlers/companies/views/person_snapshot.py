from typing import TYPE_CHECKING, Any, final

from aiogram.utils.formatting import (
    Text,
    as_line,
    as_list,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

    from apps.scans.models import PersonSnapshot, Scan


@final
class PersonSnapshotView:
    """Build Telegram message payloads for scan person snapshots."""

    @staticmethod
    def build_list_message(
        keyboard: InlineKeyboardMarkup,
        scan: Scan,
        snapshots: list[PersonSnapshot],
        offset: int,
        snapshots_total: int,
    ) -> dict[str, Any]:
        """Build kwargs for displaying a page of scan person snapshots."""
        header = as_line(scan.company.name, " 📊:")
        if snapshots:
            last = offset + len(snapshots)
            content = as_list(
                header,
                as_line(f"People {offset + 1}-{last}/{snapshots_total} 👥:"),
                *(
                    as_list(
                        as_line(
                            f"{offset + index}. ",
                            snapshot.person.normalized_name,
                        ),
                        as_line("Source: ", snapshot.source.url),
                        as_line("Role: ", snapshot.role_title),
                        as_line(
                            "Unit: ",
                            snapshot.organizational_unit or "empty",
                        ),
                        as_line(
                            "Position: ",
                            snapshot.get_position_type_display(),
                        ),
                        as_line(
                            "Confirmation: ",
                            snapshot.get_confirmation_level_display(),
                        ),
                        as_line("Email: ", snapshot.email or "empty"),
                        as_line("Phone: ", snapshot.phone or "empty"),
                        as_line("\n"),
                    )
                    for index, snapshot in enumerate(snapshots, start=1)
                ),
            )
        else:
            content = as_list(
                header,
                Text("No people found in this scan 🤷‍♂️"),
            )

        return {
            **content.as_kwargs(),
            "reply_markup": keyboard,
        }
