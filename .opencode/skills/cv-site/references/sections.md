# `site.json` reference

One file describes the whole site. `build.py` reads it and writes
`index.html`, `404.html`, `assets/site.css`, `assets/app.js` and
`.nojekyll` next to it.

## Top level

| Key | Type | Notes |
| --- | --- | --- |
| `name` | string | Full name. Rendered as first word + accent colour for the rest |
| `role` | string | One line under the name: "Backend engineer", "PhD student" |
| `tagline` | string[] | Optional. 2–3 short fragments, separated by `\|` in the hero |
| `location` | string | City and country. Never a street address |
| `email` | string | Shown as a `mailto:` link |
| `github` | string | Full URL |
| `linkedin` | string | Full URL |
| `website` | string | Optional, used only by the `contact` section |
| `photo` | string | File name next to `site.json`, e.g. `photo.jpg`. Optional |
| `cv` | string | Relative path of a PDF inside the output folder, e.g. `cv.pdf` |
| `cv_label` | string | Label for the CV link. Default `"CV"` |
| `lang` | `"en"` \| `"es"` \| `"both"` | Default `"en"`. `"both"` emits two full pages and a toggle |
| `theme` | `"ide"` \| `"paper"` | Default `"ide"` (dark chrome + light body). `"paper"` is all light and serif |
| `title` | string | `<title>` and `og:title`. Default: `"<name> — <role>"` |
| `description` | string | Meta description. Default: `"<name>. <role>."` |
| `nav_home` | string | Label of the first nav item. Default `"home"` |
| `year` | string | Fallback year in the status bar; `app.js` sets the current year |
| `sections` | array | Rendered in order, and used for the nav |

Unknown keys are ignored, so you can keep notes for yourself in the file.

## Sections

Every section needs `type`; most need `title` and `id`. `id` is the anchor
(`#experience`) — lowercase, no spaces. If omitted it is derived from the
English title. Long titles are truncated in the nav; the first six
sections appear there. Set `"nav": false` to keep a section off the nav.

### `prose`

Paragraphs. The first one is slightly larger.

```json
{ "type": "prose", "id": "about", "title": "About",
  "paragraphs": ["First paragraph.", "Second paragraph."] }
```

### `timeline`

Jobs, studies, anything with a date. `when` is a free string, so
`"2021 — 2023"`, `"2024"` and `"since 2020"` all work.

```json
{ "type": "timeline", "id": "experience", "title": "Experience", "items": [
  { "when": "2023 — now", "title": "Senior engineer", "org": "Company",
    "text": "Optional one-line context.",
    "bullets": ["What you did.", "What changed because of it."] }
] }
```

Use `bullets` for 2–4 concrete results; skip `text` if the bullets say
enough. Keep each bullet under ~120 characters.

### `cards`

Projects, services, publications with links. Two columns on desktop.
Without `href` the card is not a link.

```json
{ "type": "cards", "id": "projects", "title": "Projects", "items": [
  { "meta": "2025", "title": "Note engine",
    "text": "Turns scattered notes into a searchable index.",
    "href": "https://github.com/user/note-engine" }
] }
```

### `list`

A compact feed: writing, talks, awards, press. Right-aligned metadata.

```json
{ "type": "list", "id": "writing", "title": "Writing", "items": [
  { "title": "Why static sites age well", "meta": "2025 · Blog",
    "href": "https://example.com/post" }
] }
```

Only link to pages that exist **at the time of publishing**. If a link is
uncertain, use the plain-text form (no `href`); a dead link is worse than
no link.

### `contact`

Builds itself from `email`, `linkedin`, `github`, `website` and `cv`.
No `items`. Use it as the last section.

```json
{ "type": "contact", "id": "contact", "title": "Contact" }
```

### `raw`

Escape hatch: raw HTML, used verbatim. Only use it when the other types
cannot express the idea, and never to inject third-party scripts.

```json
{ "type": "raw", "id": "now", "title": "Now",
  "html": "<p>Building <a href=\"https://example.com\">a thing</a> in Lisbon.</p>" }
```

## Bilingual content

Set `"lang": "both"`. Then **every string** may be either a plain string
or an object with `en` and `es`:

```json
{
  "lang": "both",
  "role": { "en": "Software engineer", "es": "Ingeniera de software" },
  "sections": [
    { "type": "prose", "id": "about",
      "title": { "en": "About", "es": "Sobre mí" },
      "paragraphs": [
        { "en": "I build tools.", "es": "Construyo herramientas." }
      ] }
  ]
}
```

Missing translations fall back to English, so you can translate
incrementally — but run `verify.py` afterwards, which warns when one
language is much thinner than the other.

With `"lang": "en"` or `"es"`, objects are still accepted and the matching
language is picked. That makes it cheap to add Spanish later.

## Minimal valid file

```json
{
  "name": "Ada Lovelace",
  "role": "Software engineer",
  "email": "ada@example.com",
  "sections": [
    { "type": "prose", "id": "about", "title": "About", "paragraphs": ["I build things."] }
  ]
}
```

Build it, look at it, then grow it. A site with two honest sections beats
one with eight thin ones.
