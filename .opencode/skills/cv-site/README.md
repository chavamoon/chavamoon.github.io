# cv-site

An [OpenCode](https://opencode.ai) skill that interviews someone about
their CV and turns the answers into a small personal website, then
publishes it to GitHub Pages.

No frameworks, no build chain, no accounts beyond GitHub. Python standard
library only, static HTML out.

## Requirements

- OpenCode
- Python 3.8+ (`python3` on macOS/Linux, `python` on Windows)
- `git`
- GitHub CLI (`gh`) — optional, only for one-command publishing

## Install

Skills live in a `skills/<name>/` folder with a `SKILL.md` inside.

**Everyone on this machine** (recommended):

```
~/.config/opencode/skills/cv-site/
```

On Windows that is:

```
%USERPROFILE%\.config\opencode\skills\cv-site\
```

**Only this project:**

```
<project>/.opencode/skills/cv-site/
```

Copy the whole folder — `SKILL.md`, `references/`, `scripts/`,
`templates/` — keeping the structure. Nothing else to install; verify with:

```sh
opencode --version
ls ~/.config/opencode/skills/cv-site/SKILL.md
```

## Use it

In OpenCode, say something like:

> I want a personal site from my CV. It's at ~/Desktop/cv.pdf

or invoke the skill directly:

> @cv-site

It will ask for the CV, confirm what it read, offer a menu of sections,
ask three style questions, build the site, show you what it looks like,
and publish when you say yes.

## What you get

- `site.json` — the content, in one readable file
- `index.html`, `404.html`, `assets/` — generated, do not edit by hand
- `.nojekyll` — so Pages serves the files as they are
- Optional bilingual EN/ES version with a toggle in the top bar

Two themes: `ide` (dark top bar, monospace labels, light body) and
`paper` (all light, serif).

## Without OpenCode

The scripts work on their own:

```sh
python3 scripts/docx_text.py cv.docx > cv.txt     # if the CV is a docx
python3 scripts/build.py --out ./my-site          # reads ./my-site/site.json
python3 scripts/verify.py --dir ./my-site         # structure + links
python3 scripts/publish.py --dir ./my-site --repo my-site --dry-run
```

`site.json` is documented in `references/sections.md`.

## Layout

```
SKILL.md                  what the agent reads and follows
references/
  interview.md            question bank, round by round
  sections.md             site.json schema and section types
  rules.md                writing, privacy, accessibility
  publishing.md           Pages, custom domains, troubleshooting
scripts/
  build.py                site.json → HTML
  verify.py               structure, links, alt text, phone leak
  publish.py              git + gh + Pages, refuses to overwrite
  docx_text.py            dependency-free .docx extraction
templates/
  site.css                the whole design, both themes
  app.js                  language toggle, year, active nav
examples/
  site.json               a complete bilingual site to copy
LICENSE                   MIT
```

## Design decisions worth knowing

- **Single page, anchored sections.** A CV site is read in 90 seconds;
  multiple pages add navigation without adding information.
- **Relative paths.** The same build works at a root domain and under
  `/<repo>/`, so project pages need no configuration.
- **No JavaScript for content.** Only the language toggle and the year
  need it; both fail gracefully.
- **The builder owns the HTML.** Content changes go in `site.json`,
  which keeps the design consistent and the diff reviewable.
- **Publishing refuses to overwrite.** `publish.py` stops if the repo
  exists unless `--force` is explicit.

## Licence

MIT — copy it, fork it, hand it to a friend.
