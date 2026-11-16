---
name: cv-site
description: Interview someone about their CV or résumé and build a personal website from it, then publish it to GitHub Pages. Use when a user wants a portfolio / CV site generated, asks to turn a résumé into a web page, or wants help publishing one.
---

# CV → Site

You are running a short interview that ends with a published personal
website. The user brings a CV; you ask a few questions, write a config
file, build the HTML, check it, and publish it. Everything here is
standard-library Python and static HTML — no npm, no frameworks, no
accounts beyond GitHub.

## What the result looks like

A single-page site: dark IDE-style top bar with the person's name as a
file name, a hero with name / role / photo / contact links, then sections
(about, experience, projects, writing, education, contact…), and a status
bar at the bottom. Light document body, monospace section labels, works on
mobile, no JavaScript required to read it. Optional English/Spanish
versions with a toggle.

Script paths below (`scripts/build.py`…) are relative to **this skill's
directory**, not the user's project. Run them with the full path, for
example:

```sh
python3 ~/.config/opencode/skills/cv-site/scripts/build.py --out ./my-site
```

On Windows use `python` and `%USERPROFILE%\.config\opencode\skills\cv-site\scripts\build.py`.

This file follows the open Agent Skills format (`SKILL.md` with `name`
and `description`), so it also loads in Claude Code, Codex CLI, Gemini CLI
and Cursor once the folder sits in their skills directory — see
`README.md`. With an agent that has no skills support, point it at this
file and tell it to follow it. Tool names below are OpenCode's; use the
equivalent in your host (`question` ≈ `AskUserQuestion`, `read` ≈ `Read`).

## Non-negotiables

1. **Facts come from the user.** Never invent an employer, date, title,
   degree, metric or link. You may shorten and rephrase what the CV says.
   If something is missing, ask or leave it out — do not fill gaps.
2. **Never publish a phone number, home address or personal ID.** Email,
   GitHub, LinkedIn and city are fine. If the CV has a phone, drop it and
   say so once.
3. **Never overwrite an existing repository.** `publish.py` refuses by
   default; only pass `--force` after the user explicitly says the repo is
   theirs and may be replaced.
4. **At most four questions per round.** Use a multiple-choice question
   tool when you have one (`question` in OpenCode, `AskUserQuestion` in
   Claude Code), otherwise numbered options in prose. Always make the
   first option a sensible default so "you decide" is a valid answer.
5. **Interview in the user's language.** Write the site in the language
   they choose (default: the language of the CV). Keep this document and
   your code comments in English.
6. **Don't ask for anything you can read.** If the CV has it, confirm it
   instead of asking.

## Workflow

### 0. Get the CV

Ask for one of: a file path, pasted text, or a link.

| Input | How to read it |
| --- | --- |
| PDF | your file-reader handles PDFs (OpenCode `read`, Claude Code `Read`) — do not write a parser |
| DOCX | `python3 scripts/docx_text.py "<file.docx>"` |
| ODT/RTF/TXT | `read`, or ask them to paste |
| A URL | ask them to download it or paste the text; do not scrape |
| LinkedIn | ask them to export the PDF; scraping usually fails |

Use `python3` on macOS/Linux and `python` on Windows. If neither works,
say so and ask for pasted text instead of stalling.

If they have no CV, switch to interview-only mode: run the same rounds
but ask for each fact instead of reading it.

### 1. Read, then confirm (round 1)

Read the CV fully. Then show a compact fact table — name, headline,
location, current role, employers and dates, education, links — and ask
them to correct it in one message. In the same round ask:

- Which three things should a stranger remember? (default: current role,
  strongest project, what they want next)
- What contact details may go on a public page? (default: email + GitHub
  + LinkedIn, no phone)

For a photo, ask for a square image at least 400px wide, saved next to
the future `site.json`. Do not crop or download a photo from LinkedIn.

### 2. Sections (round 2)

Offer the menu in `references/sections.md` and let them pick. Default for
a CV site: About, Experience, Projects, Contact. Add Writing, Talks,
Education, Skills, Now or a custom section only if they want it.

Then ask at most three follow-ups total, not per section. For projects,
ask for one line each on what it is and why it matters.

### 3. Style and language (round 3)

- **Language:** English, Spanish, or both. "Both" doubles the content and
  adds a toggle; only offer it if they seem bilingual.
- **Theme:** `ide` (dark chrome, the default) or `paper` (all light,
  serif). Show both in one sentence; don't describe CSS.
- **Publish target:** `<user>.github.io` (site at the root domain) or a
  project repo (site at `/<repo>/`). Ask whether `gh` is installed only if
  publishing is the next step.

### 4. Write the content

Work in a fresh directory the user can keep, e.g. `./<slug>-site/`. Put
`site.json`, the photo if any, and the CV PDF inside it.

Start from `examples/site.json` (a complete bilingual example) or from
this shape, and fill it in (full schema in `references/sections.md`):

```json
{
  "lang": "en",
  "theme": "ide",
  "name": "Ada Lovelace",
  "role": "Software engineer",
  "tagline": ["analytical engines", "algorithms"],
  "location": "London, UK",
  "photo": "photo.jpg",
  "cv": "cv.pdf",
  "email": "ada@example.com",
  "github": "https://github.com/ada",
  "linkedin": "https://www.linkedin.com/in/ada",
  "sections": [
    { "type": "prose", "id": "about", "title": "About", "paragraphs": ["…"] },
    { "type": "timeline", "id": "experience", "title": "Experience", "items": [
      { "when": "2023 — now", "title": "Senior engineer", "org": "Analytical Engines Ltd",
        "bullets": ["Shipped …", "Led …"] }
    ]},
    { "type": "cards", "id": "projects", "title": "Projects", "items": [
      { "title": "Note engine", "text": "Turns notes into …", "href": "https://…" }
    ]},
    { "type": "contact", "id": "contact", "title": "Contact" }
  ]
}
```

Rules for the writing itself are in `references/rules.md`. The short
version: CV facts, plain sentences, no adjectives doing the work of
evidence, no skill chips, paragraphs that use the full column.

### 5. Build and look at it

```sh
python3 scripts/build.py --out ./<slug>-site
cd ./<slug>-site && python3 -m http.server 8135 --bind 127.0.0.1
```

Open `http://127.0.0.1:8135/` and check it at desktop width and at 390px.
If you have browser tools, screenshot both; otherwise tell the user what
to look at and what to send you. Never open the page with `file://` —
root-relative and relative paths behave differently there.

Then:

```sh
python3 scripts/verify.py --dir ./<slug>-site
```

Fix every error. Warnings about missing meta descriptions, thin text or
possible phone numbers are real: read them.

### 6. Iterate

Rebuild after each change. Content edits go in `site.json`, never in
`index.html` — the builder overwrites it. Show the user a screenshot or a
short description of what changed, not the HTML.

### 7. Publish

Ask once, explicitly: *"Create the public repo `<owner>/<repo>` and
publish?"* Then:

```sh
python3 scripts/publish.py --dir ./<slug>-site --repo <repo>
```

Add `--owner` for an org, `--dry-run` to show the commands without
running them. If `gh` is missing the script prints the manual steps and
exits 2 — relay those steps, don't try to install software for them.

Details, including custom domains and project pages, are in
`references/publishing.md`.

## Files in this skill

| Path | Purpose |
| --- | --- |
| `scripts/build.py` | renders `site.json` → `index.html`, `404.html`, assets |
| `scripts/verify.py` | structure, links, anchors, alt text, phone leak |
| `scripts/publish.py` | git + `gh repo create` + Pages, refuses overwrite |
| `scripts/docx_text.py` | dependency-free `.docx` text extraction |
| `templates/site.css` | the whole visual design, two themes |
| `templates/app.js` | language toggle, year, active nav link |
| `examples/site.json` | a complete bilingual example to copy |
| `references/interview.md` | question bank, round by round |
| `references/sections.md` | `site.json` schema and section types |
| `references/rules.md` | writing, privacy, accessibility rules |
| `references/publishing.md` | Pages, custom domains, troubleshooting |

## When something goes wrong

- **Build fails on JSON** — the most common cause is a trailing comma or
  an unescaped quote. Read the message, fix `site.json`, rerun.
- **Photo doesn't appear** — the file must sit next to `site.json` and be
  named in `photo`; the builder copies it to `assets/photo.jpg`.
- **Pages shows 404** — check that Pages is set to the `main` branch, root
  folder, and that `.nojekyll` exists (the builder writes it).
- **Accented characters look wrong** — you edited a file with a tool that
  rewrote the encoding. Rebuild instead of patching HTML by hand.
