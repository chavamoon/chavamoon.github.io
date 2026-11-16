# Rules for the content

These are the rules that keep the site from reading like a LinkedIn
inspiration post. They apply to every section you write.

## Sourcing

- Every factual claim traces back to the CV or to an answer the user gave.
- Do not add numbers ("reduced latency 40%") unless they said them.
- Do not upgrade a title, a date, a company size or a seniority level.
- If the CV contradicts itself, ask — do not pick the nicer version.
- "Familiar with" and "used" are allowed. "Expert" needs evidence.

## Voice

Write like a competent person explaining their work, not like a brand.

| Don't | Do |
| --- | --- |
| "Passionate about leveraging cutting-edge AI" | "I build retrieval systems for messy internal documents." |
| "Results-driven professional with 10+ years" | "Ten years building backends, mostly in Python." |
| "Spearheaded a transformative initiative" | "Led the migration from X to Y; it removed a nightly job." |
| "Adept at cross-functional collaboration" | "Worked with design and support to ship the new onboarding." |

Specific rules:

- Short sentences. One idea each.
- Verbs first: build, ship, migrate, maintain, teach, review.
- Cut adverbs. If a sentence needs "significantly", it needs a number.
- No metaphors about journeys, rockets, ninjas or rockstars.
- No exclamation marks.
- Avoid "I am passionate about"; say what you actually do on a Tuesday.

## Shape

- **Paragraphs fill the column.** No floating pull quotes, no narrow text
  blocks, no sentences broken for visual rhythm.
- **No skill chips or badge walls.** Skills belong in a sentence or a
  short list with context: "Python (8 years), Postgres, some Rust."
- **Two to four bullets per role.** More is a CV, not a website.
- **Sections in order of what you want read first**, not chronological
  autobiography. About → Experience → Projects → Contact is a good spine.
- **One screen per idea.** If About is longer than four short paragraphs,
  it is doing too much.

## Privacy

Never put on the page:

- phone numbers, home address, national ID, date of birth;
- work email addresses you do not control;
- client names under NDA, unreleased product names, internal metrics;
- photos of other people without their consent;
- anything about health, religion, politics or family unless the person
  explicitly asked for it and it is the point of the page.

Safe by default: name, city, personal email, GitHub, LinkedIn, personal
site, a professional photo the person chose.

Say one sentence about the phone when you drop it, and move on:

> "I left your phone number off — the page is public and scraped. Email
> and LinkedIn cover the same ground."

## Links

- Only link to what exists **now**. Check with `verify.py`, which requests
  every external URL.
- Prefer stable destinations: a personal site, a repository, an official
  page. Avoid link shorteners, tracking parameters (`?utm_...`) and
  "link in bio" pages.
- Anchor text says where it goes: "the paper" not "click here".
- No link is better than a dead link. If a post is gone, keep the title as
  plain text.

## Accessibility

The template handles most of this; do not undo it.

- `alt` on every image. A decorative image still needs `alt=""`.
- Contrast: the template's palette is tested. Don't hand-edit colours.
- Never rely on colour alone. The language toggle also uses weight and
  `aria-pressed`.
- The page must be readable with JavaScript off. Only the language toggle
  and the year need JS.
- Don't remove the `:focus` outlines or the reduced-motion block.
- Headings in order: one `<h1>` (the name), `<h2>` per section, `<h3>` for
  items. The builder does this; `raw` sections are your responsibility.

## Bilingual pages

If the site is bilingual:

- Translate meaning, not words. A Spanish version that reads like a
  translation is worse than English only.
- Keep names, product names and job titles in their original form unless
  there is a standard translation.
- Dates and ranges can stay numeric ("2023 — now" / "2023 — actualidad").
- Run `verify.py` after translating; it flags a version that is much
  shorter than the other.

## The last read

Before publishing, read the page as if you were the hiring manager who has
90 seconds and 40 tabs open. If the first paragraph does not say what this
person does and why it matters, rewrite it.
