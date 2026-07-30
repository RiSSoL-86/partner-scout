from typing import Final

# Instruction handed to the gate LLM for every candidate page.
FILTER_PROMPT: Final[str] = """
You inspect one web page from {website}, the site of the firm "{company}".
Find every real person who is a PARTNER or DIRECTOR of "{company}" itself.
Set `is_relevant` to True only when at least one such person qualifies.

A person qualifies ONLY if ALL hold:
- Rank: partner or director level (Партнёр, Управляющий партнёр, Директор,
  Partner, Managing Partner, Director — any variation). Skip lower ranks
  (менеджер, консультант, советник, аналитик, специалист, associate,
  counsel), however senior they sound.
- Affiliation: the person must be employed by "{company}" itself. Whenever
  the title or surrounding text names an organization other than
  "{company}", they belong to that organization — reject them, even though
  they appear on this page. Keep a person only when their tie to
  "{company}" is explicit; if you cannot tell which firm employs them, skip
  them.
- Full name: both a first name AND a last name are printed on the page.
  A bare given name mentioned in running text does NOT qualify; never
  invent or leave the surname empty — if it is missing, skip them.

Skip entries that are not individuals: partner companies, sponsors,
vendors, clients.

Classify `page_type` by the page's PRIMARY purpose (choose one code):
- 0 profile — built around ONE named person (bio, CV, contacts).
- 1 team — a listing of MANY people (team, partners, leadership roster).
- 2 publication — authored article, report, research note or blog post.
- 3 interview — a Q&A or conversation format.
- 4 news — a dated news item or press release about the firm or its people.
- 5 event — a conference, webinar or seminar announcement or recap.
- 6 document — a downloadable file wrapper (PDF, presentation, brochure).
- 7 other — none of the above fits.
Prefer the main purpose: a partner quoted in news is 4, not 0; an article
written by a partner is 2, not 0.

For every qualifying person return: first/middle (may be empty)/last name;
`position` (job title copied verbatim); `mention_type` (0 personal profile,
1 organizational-unit listing, 2 otherwise); `context` (one short quote
justifying the person). Names may be in Russian. Extract nothing when no
one qualifies.
""".strip()


def build_filter_prompt(company_name: str, website: str = "") -> str:
    """Fill the gate instruction with the firm currently being scanned."""
    company = company_name.strip() or "this firm"
    site = website.strip() or "this website"
    return FILTER_PROMPT.format(company=company, website=site)
