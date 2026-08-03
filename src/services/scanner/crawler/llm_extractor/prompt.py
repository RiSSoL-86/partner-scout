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
- Affiliation: this page is on "{company}"'s own site, so a person presented
  here as its partner or director is employed by "{company}" by default — do
  NOT drop someone merely because the page omits an explicit "works at
  {company}" label. Reject a person ONLY when the title or surrounding text
  explicitly ties them to a DIFFERENT organization (a client, a partner
  firm, a regulator, a former employer); then they belong to that
  organization, even though they appear on this page.
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
written by a partner is 2, not 0. Always classify `page_type`, even when no
person qualifies.

For every qualifying person return:
- first/middle (may be empty)/last name;
- `role_title` — the job title copied verbatim, kept complete with any
  practice, department or specialization named in it (do not shorten or
  translate); this title is what later classifies the person;
- `mention_type`: how THIS person is presented on the page — judge it per
  person, not per page (this reflects how strongly the page establishes them):
    - 0 personal profile — the page centres on this individual: a dedicated
      bio, CV, or contact card about them (usually a `page_type` 0 profile).
    - 1 organizational-unit listing — the person appears as one entry in a
      roster of people: a team, partners, leadership or department list
      (usually a `page_type` 1 team).
    - 2 otherwise — any weaker mention: quoted in an article, credited as an
      author, or named incidentally in running text.
- `email` and `phone` (work contacts printed on the page, empty when absent —
never guess). Names may be in Russian. Extract nothing when no one qualifies.
""".strip()


def build_filter_prompt(company_name: str, website: str = "") -> str:
    """Fill the gate instruction with the firm currently being scanned."""
    company = company_name.strip() or "this firm"
    site = website.strip() or "this website"
    return FILTER_PROMPT.format(company=company, website=site)
