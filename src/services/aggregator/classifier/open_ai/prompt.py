from typing import Final

# Instruction handed to the aggregator LLM for one company's scan.
AGGREGATE_PROMPT: Final[str] = """
You consolidate scan evidence about partners and directors of the firm
"{company}". You receive a JSON list of people; each person carries every
source mention found for them within a single scan. For EACH input person
return exactly one classification, echoing their `person_id` unchanged.

Never invent people and never drop anyone: the result must contain one entry
per input person, no more, no less.

Each input person carries:
- `full_name`: their normalized name.
- `mentions`: every source mention found for them in this scan. Each mention
  has `role_title` (the job title printed on that source, verbatim),
  `mention_type` (0 the source was a personal profile of them, 1 they were
  listed in an organizational-unit roster, 2 any other mention), and
  `source_title` (the title of that source page).
Base every field ONLY on these mentions — you do not receive their contacts.

Classify each person using only the supplied mentions:
- `position_type`: 0 partner, 1 director. Judge by the seniority of the
  titles; default to 0 partner when the titles clearly denote partnership.
- `work_status`: how the person is engaged with the firm. When you cannot
  confidently choose between 1 and 2, use 0 unknown — never guess.
  - 1 front line: works in a client-facing part of the firm — serves or
    interacts with external clients. Signals: an explicit client-service or
    advisory role named in `role_title`, or a `mention_type` 0 personal
    profile.
  - 2 back office: works in an internal function or a firm practice/unit
    that does not directly serve external clients — finance, HR, IT,
    operations, administration, a named practice or department, etc.
  - 0 unknown: the evidence does not make it clear whether the role is
    front line (1) or back office (2).
- `specialization`: the nature of the person's work.
  - 1 industrial: tied to a production/physical sector — construction,
    mining, oil & gas, manufacturing, energy, real estate, infrastructure.
  - 2 functional: tied to a non-production function — finance, tax, legal,
    audit, strategy, and anything not related to production.
  - 0 unknown: the specialization is not clear.
- `practice_area`: the dominant practice in the titles.
  - 1 audit: audit and assurance.
  - 2 tax and legal: anything about taxes or legal/law matters.
  - 3 consulting and deals: consulting, advisory, M&A, transactions, deals.
  - 0 unknown: the practice is not clear.
- `role_title`: the single most representative job title across the
  mentions, copied as printed (do not translate).
- `organizational_unit`: the department or practice unit if named,
  otherwise an empty string.

Prefer 0 unknown over guessing. Titles may be in Russian.
""".strip()


def build_aggregate_prompt(company_name: str) -> str:
    """Fill the aggregator instruction with the firm being aggregated."""
    company = company_name.strip() or "this firm"
    return AGGREGATE_PROMPT.format(company=company)
