from typing import Final

# Keywords that raise a page's relevance score during the crawl. The scorer
# uses them to visit team/leadership pages before generic ones (RU + EN).
RELEVANCE_KEYWORDS: Final[tuple[str, ...]] = (
    "команда",
    "руководство",
    "партнёры",
    "партнеры",
    "наша команда",
    "о компании",
    "о нас",
    "team",
    "about",
    "leadership",
    "partners",
    "people",
    "management",
)

# URL fragments that keep a branch in scope (matched case-insensitively).
URL_INCLUDE: Final[tuple[str, ...]] = (
    "team",
    "about",
    "people",
    "partners",
    "leadership",
    "management",
    "our-team",
    "komanda",
    "o-nas",
    "o-kompanii",
    "rukovodstvo",
)

# URL fragments that prune a branch before it is ever fetched (noise).
URL_EXCLUDE: Final[tuple[str, ...]] = (
    "news",
    "blog",
    "careers",
    "vacancies",
    "press",
    "media",
    "events",
    "privacy",
    "cookie",
    "tags",
    "search",
)

# Instruction handed to the gate LLM for every candidate page. It filters
# noise and prepares the minimal facts step 1 stores; structured person
# fields and the confirmation level are decided later, in the aggregator.
GATE_INSTRUCTION: Final[str] = """
You inspect one web page from a consulting firm's own website.

Decide `is_relevant`: mark it True ONLY when the page presents a real
human being who is a PARTNER or DIRECTOR of THIS firm.

Mark it False when the "partner" is not such a person, for example:
- a partner company, sponsor or vendor (e.g. a "delivery partner");
- a client, or someone merely named in a news item or event;
- a page with no partner or director at all.

Classify the page into `page_type`.

For every relevant person, return:
- their name split into first, middle (may be empty) and last name;
- `mention_type`: how they appear on THIS page — a personal profile
  page, an organizational-unit/team listing, or otherwise;
- `context`: one short quote from the page justifying the person.

Names may be in Russian or English. Extract nothing when not relevant.
""".strip()
