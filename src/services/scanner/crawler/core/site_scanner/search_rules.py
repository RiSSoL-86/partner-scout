import re

# Deterministic post-filter over the title the gate LLM copies into `position`.
POSITION_ALLOW = re.compile(
    r"партн[её]р|директор|partner|director",
    re.IGNORECASE,
)


def is_target_position(position: str) -> bool:
    """Tell whether a job title is a partner or director rank we keep."""
    return bool(POSITION_ALLOW.search(position))


def mentions_partner_or_director(text: str) -> bool:
    """Cheap pre-gate: does the page body mention a partner/director word?"""
    return bool(POSITION_ALLOW.search(text))
