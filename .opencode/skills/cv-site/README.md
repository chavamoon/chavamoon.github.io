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

It is a skill folder: `SKILL.md` with YAML frontmatter, plus
`references/`, `scripts/` and `templates/`. Copy the whole folder (keeping
its structure) into your agent's skills directory. If it already has the
`name`/`description` frontmatter, it is discovered automatically — you do
not have to tell the agent anything.

| Agent | Folder |
| --- | --- |
| OpenCode | `~/.config/opencode/skills/cv-site/` or `<project>/.opencode/skills/cv-site/` |
| Claude Code | `~/.claude/skills/cv-site/` or `<project>/.claude/skills/cv-site/` |
| Codex CLI | `~/.agents/skills/cv-site/` (`~/.codex/skills/` also works) |
| Gemini CLI | `~/.gemini/skills/cv-site/` |
| Cursor | `<project>/.cursor/skills/cv-site/` |

On Windows, `~` is `%USERPROFILE%`, e.g.
`%USERPROFILE%\.claude\skills\cv-site\`.

You can keep one copy and link it instead of duplicating:

```sh
# macOS / Linux, OpenCode + Claude Code + the shared .agents folder
ln -s ~/code/cv-site ~/.config/opencode/skills/cv-site
ln -s ~/code/cv-site ~/.claude/skills/cv-site
ln -s ~/code/cv-site ~/.agents/skills/cv-site
```

```powershell
# Windows, same idea
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\cv-site" -Target "C:\code\cv-site"
```

Restart the agent (or reload skills) after copying. Check it is visible
with its `/skills` command, or just ask for a CV site and see whether it
picks it up.

### Agents with no skills support

Anything that can read files and run shell commands can use this without
the mechanism: point it at `SKILL.md`.

> Read `C:\code\cv-site\SKILL.md` and follow it. The paths in it are
> relative to that folder. My CV is at `C:\Users\me\cv.pdf`.

For ChatGPT/Codex `AGENTS.md`, Gemini's `GEMINI.md` or a Cursor rule, one
line is enough:

```markdown
## CV site

To build or update a personal site from a CV, read
`skills/cv-site/SKILL.md` and follow it.
```

## Use it

Say something like:

> I want a personal site from my CV. It's at ~/Desktop/cv.pdf

or invoke the skill directly (`@cv-site` in OpenCode, `/cv-site` in
Claude Code).

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

## Without an agent

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
