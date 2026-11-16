#!/usr/bin/env python3
"""Build a personal site from site.json. Standard library only.

Usage:
    python build.py --out <dir>
    python build.py --out <dir> --config <path>

Reads <out>/site.json (or --config) and writes index.html, 404.html,
assets/site.css, assets/app.js, .nojekyll into <out>.
"""
import argparse
import html
import json
import os
import re
import shutil
import sys

# Windows consoles default to a legacy code page; keep accented paths printable.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(os.path.dirname(HERE), "templates")


# ---------------------------------------------------------------- helpers

def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def tx(value, lang):
    """Pick a language from a plain string or an {"en": .., "es": ..} object."""
    if isinstance(value, dict):
        if value.get(lang):
            return value[lang]
        for key in ("en", "es"):
            if value.get(key):
                return value[key]
        for candidate in value.values():
            if candidate:
                return candidate
        return ""
    return "" if value is None else value


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", str(text).lower())
    return re.sub(r"[-\s]+", "-", text).strip("-") or "section"


def has_lang(value):
    return isinstance(value, dict) and any(k in value for k in ("en", "es"))


def any_bilingual(obj):
    if isinstance(obj, dict):
        if has_lang(obj):
            return True
        return any(any_bilingual(v) for v in obj.values())
    if isinstance(obj, list):
        return any(any_bilingual(v) for v in obj)
    return False


# ---------------------------------------------------------------- pieces

def svg_icon(kind):
    paths = {
        "pin": '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z"/>'
               '<circle cx="12" cy="10" r="2.6"/>',
        "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2.4"/>'
                '<path d="m3 6.4 9 6.1 9-6.1"/>',
        "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/>'
                    '<path d="M7.5 10.5v6M7.5 7.6v.1M11.5 16.5v-3.4a2 2 0 0 1 4 0v3.4"/>',
        "github": '<path d="M9 19c-4 1.5-4-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6'
                  'a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12 12 0 0 0-6 0'
                  'C6.7 2.8 5.6 3.1 5.6 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6'
                  '-.6.6-.6 1.2-.5 2V21"/>',
    }
    return '<svg viewBox="0 0 24 24">' + paths.get(kind, "") + "</svg>"


def render_contacts(site, lang):
    rows = []
    if site.get("location"):
        rows.append("<li>" + svg_icon("pin") + esc(tx(site["location"], lang)) + "</li>")
    if site.get("email"):
        email = tx(site["email"], lang)
        rows.append("<li>" + svg_icon("mail") + '<a href="mailto:' + esc(email) + '">' + esc(email) + "</a></li>")
    if site.get("linkedin"):
        url = tx(site["linkedin"], lang)
        rows.append("<li>" + svg_icon("linkedin") + '<a href="' + esc(url) +
                    '" target="_blank" rel="noopener">' + esc(url.replace("https://", "")) + "</a></li>")
    if site.get("github"):
        url = tx(site["github"], lang)
        rows.append("<li>" + svg_icon("github") + '<a href="' + esc(url) +
                    '" target="_blank" rel="noopener">' + esc(url.replace("https://", "")) + "</a></li>")
    if not rows:
        return ""
    return '<ul class="contacts">' + "".join(rows) + "</ul>"


def render_hero(site, lang, suffix=""):
    name = esc(tx(site.get("name", ""), lang))
    parts = name.split(" ", 1)
    heading = parts[0] + ("<em>" + parts[1] + "</em>" if len(parts) > 1 else "")

    photo = ""
    if site.get("photo"):
        photo = ('<img class="photo" src="assets/photo.jpg" alt="' + name + '" width="120" height="120">')

    tagline = site.get("tagline") or []
    if isinstance(tagline, dict):
        tagline = tx(tagline, lang) or []
    if isinstance(tagline, str):
        tagline = [tagline]
    bits = [esc(tx(t, lang)) for t in tagline if tx(t, lang)]
    tagline_html = ('<p class="tagline">' + "<span>|</span>".join(bits) + "</p>") if bits else ""

    cv_html = ""
    if site.get("cv"):
        cv_html = ('<a class="cv-inline" href="' + esc(site["cv"]) + '" target="_blank" rel="noopener">'
                   + esc(tx(site.get("cv_label", "CV"), lang)) + " ↗</a>")

    return (
        '<header class="hero" id="top' + esc(suffix) + '"><div class="hero-in">' + photo +
        '<div><h1>' + heading + "</h1>" +
        '<p class="role">' + esc(tx(site.get("role", ""), lang)) + "</p>" +
        tagline_html + cv_html + "</div></div>" + render_contacts(site, lang) + "</header>"
    )


def render_section(sec, lang, site, suffix=""):
    kind = sec.get("type", "prose")
    title = esc(tx(sec.get("title", ""), lang))
    sid = (sec.get("id") or slugify(tx(sec.get("title", kind), "en"))) + suffix
    head = "<h2>" + title + "</h2>" if title else ""

    if kind == "prose":
        paras = sec.get("paragraphs") or []
        if isinstance(paras, str):
            paras = [paras]
        body = ['<p class="' + ("lead" if i == 0 else "") + '">' + esc(tx(p, lang)) + "</p>"
                for i, p in enumerate(paras)]
        return '<section id="' + esc(sid) + '">' + head + "".join(body) + "</section>"

    if kind == "timeline":
        rows = []
        for item in sec.get("items") or []:
            bullets = "".join("<li>" + esc(tx(b, lang)) + "</li>" for b in (item.get("bullets") or []))
            rows.append(
                "<li>" +
                ('<div class="when">' + esc(tx(item.get("when", ""), lang)) + "</div>" if item.get("when") else "") +
                "<h3>" + esc(tx(item.get("title", ""), lang)) + "</h3>" +
                ('<div class="org">' + esc(tx(item.get("org", ""), lang)) + "</div>" if item.get("org") else "") +
                ("<p>" + esc(tx(item["text"], lang)) + "</p>" if item.get("text") else "") +
                ("<ul>" + bullets + "</ul>" if bullets else "") +
                "</li>"
            )
        return ('<section id="' + esc(sid) + '">' + head +
                '<ol class="timeline">' + "".join(rows) + "</ol></section>")

    if kind == "cards":
        cards = []
        for item in sec.get("items") or []:
            inner = ""
            if item.get("meta"):
                inner += '<span class="k">' + esc(tx(item["meta"], lang)) + "</span>"
            inner += "<h3>" + esc(tx(item.get("title", ""), lang)) + "</h3>"
            if item.get("text"):
                inner += "<p>" + esc(tx(item["text"], lang)) + "</p>"
            href = tx(item.get("href", ""), lang)
            if href:
                cards.append('<a class="entry" href="' + esc(href) + '" target="_blank" rel="noopener">' +
                             inner + "</a>")
            else:
                cards.append('<div class="entry">' + inner + "</div>")
        return ('<section id="' + esc(sid) + '">' + head +
                '<div class="entries">' + "".join(cards) + "</div></section>")

    if kind == "list":
        rows = []
        for item in sec.get("items") or []:
            label = esc(tx(item.get("title", ""), lang))
            href = tx(item.get("href", ""), lang)
            text = ('<a class="ptitle" href="' + esc(href) + '" target="_blank" rel="noopener">' + label + "</a>"
                    if href else '<span class="ptitle">' + label + "</span>")
            meta = tx(item.get("meta", ""), lang)
            rows.append("<li>" + text + ('<span class="pmeta">' + esc(meta) + "</span>" if meta else "") + "</li>")
        return '<section id="' + esc(sid) + '">' + head + '<ul class="feed">' + "".join(rows) + "</ul></section>"

    if kind == "contact":
        links = []
        if site.get("email"):
            email = tx(site["email"], lang)
            links.append('<li><a href="mailto:' + esc(email) + '">' + esc(email) + "</a></li>")
        for key, label in (("linkedin", "LinkedIn"), ("github", "GitHub")):
            if site.get(key):
                url = tx(site[key], lang)
                links.append('<li><a href="' + esc(url) + '" target="_blank" rel="noopener">' +
                             esc(label) + "</a></li>")
        if site.get("website"):
            url = tx(site["website"], lang)
            links.append('<li><a href="' + esc(url) + '" target="_blank" rel="noopener">' +
                         esc(re.sub(r"^https?://", "", url).rstrip("/")) + "</a></li>")
        if site.get("cv"):
            links.append('<li><a href="' + esc(site["cv"]) + '" target="_blank" rel="noopener">' +
                         esc(tx(site.get("cv_label", "CV"), lang)) + " (PDF)</a></li>")
        return ('<section id="' + esc(sid) + '">' + head +
                '<ul class="links">' + "".join(links) + "</ul></section>")

    if kind == "raw":
        return ('<section id="' + esc(sid) + '">' + head + (sec.get("html") or "") + "</section>")

    return ""


def nav_items(site, lang):
    items = []
    for sec in site.get("sections") or []:
        if sec.get("nav") is False:
            continue
        title = tx(sec.get("title", ""), lang)
        if not title:
            continue
        sid = sec.get("id") or slugify(tx(sec.get("title", ""), "en"))
        items.append((sid, title))
    return items[:6]


def render_head(site, lang, lang_attr="en"):
    name = tx(site.get("name", ""), lang)
    role = tx(site.get("role", ""), lang)
    title = tx(site.get("title"), lang) if site.get("title") else (name + " — " + role)
    desc = tx(site.get("description"), lang) if site.get("description") else (name + ". " + role + ".")
    return (
        "<!DOCTYPE html>\n<html lang=\"" + esc(lang_attr) + "\" data-theme=\"" + esc(site.get("theme", "ide")) + "\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + esc(title) + "</title>\n"
        '<meta name="description" content="' + esc(desc) + '">\n'
        '<meta property="og:title" content="' + esc(title) + '">\n'
        '<meta property="og:description" content="' + esc(desc) + '">\n'
        '<meta property="og:type" content="profile">\n'
        '<link rel="icon" href="' + favicon_data_uri(site, lang) + '">\n'
        '<link rel="stylesheet" href="assets/site.css">\n'
        "</head>\n"
    )


def render_body(site, lang, suffix=""):
    name = tx(site.get("name", ""), lang)
    role = tx(site.get("role", ""), lang)
    slug = slugify(name or "site")

    nav_html = '<a href="#top' + esc(suffix) + '" class="on">' + esc(tx(site.get("nav_home", "home"), lang)) + "</a>"
    for sid, label in nav_items(site, lang):
        nav_html += '<a href="#' + esc(sid + suffix) + '">' + esc(label) + "</a>"

    cv_pill = ""
    if site.get("cv"):
        cv_pill = ('<a class="cv" href="' + esc(site["cv"]) + '" target="_blank" rel="noopener">'
                   + esc(tx(site.get("cv_label", "CV"), lang)) + " ↗</a>")

    switch = ""
    if site.get("_bilingual"):
        switch = (
            '<span class="lang-switch" role="group" aria-label="Language">'
            '<button type="button" data-set-lang="en" class="on" aria-pressed="true">EN</button>'
            '<button type="button" data-set-lang="es" aria-pressed="false">ES</button>'
            "</span>"
        )

    sections = "".join(render_section(s, lang, site, suffix) for s in (site.get("sections") or []))
    location = esc(tx(site.get("location", ""), lang))
    footer = esc(role) + (" · " + location if location else "")

    return (
        "<body>\n\n"
        '<div class="chrome">\n'
        '  <span class="dots"><i></i><i></i><i></i></span>\n'
        '  <span class="file">' + esc(slug) + "<em>.md</em></span>\n"
        '  <nav class="nav" aria-label="Sections">' + nav_html + cv_pill + "</nav>\n"
        "  " + switch + "\n"
        "</div>\n\n"
        + render_hero(site, lang, suffix) + "\n\n"
        "<main>\n" + sections + "\n</main>\n\n"
        '<footer class="status">\n'
        '  <span><span class="dot"></span><span class="branch">main</span></span>\n'
        '  <span>' + footer + "</span>\n"
        '  <span class="right"><span class="js-year">' + esc(site.get("year", "")) + "</span></span>\n"
        "</footer>\n\n"
        '<script src="assets/app.js"></script>\n'
        "</body>\n</html>\n"
    )


def favicon_data_uri(site, lang):
    name = tx(site.get("name", "?"), lang)
    initials = "".join(part[0] for part in name.split()[:2]).upper() or "?"
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="14" fill="#0d1117"/>'
           '<text x="32" y="42" font-family="monospace" font-size="26" fill="#58a6ff" '
           'text-anchor="middle">' + html.escape(initials) + "</text></svg>")
    return "data:image/svg+xml," + quote(svg, safe="")


# ---------------------------------------------------------------- build

def build(out_dir, config_path=None):
    out_dir = os.path.abspath(out_dir)
    config_path = config_path or os.path.join(out_dir, "site.json")
    if not os.path.isfile(config_path):
        sys.exit("site.json not found: " + config_path)

    with open(config_path, encoding="utf-8") as fh:
        site = json.load(fh)

    lang = site.get("lang", "en")
    bilingual = lang == "both" or any_bilingual(site)
    site["_bilingual"] = bilingual
    site.setdefault("year", "")

    os.makedirs(os.path.join(out_dir, "assets"), exist_ok=True)

    if bilingual:
        page = (render_head(site, "en", "en") + "<body>\n"
                '<div data-lang="en">' + render_body(site, "en", "") + "</div>\n"
                '<div data-lang="es" hidden>' + render_body(site, "es", "-es") + "</div>\n"
                "</body>\n</html>\n")
    else:
        page = render_head(site, lang, lang) + render_body(site, lang)

    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)

    not_found = (
        "<!DOCTYPE html>\n<html lang=\"" + esc(lang if lang != "both" else "en") +
        "\" data-theme=\"" + esc(site.get("theme", "ide")) + "\">\n<head>\n"
        '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Not found</title>\n<meta name=\"robots\" content=\"noindex\">\n"
        '<link rel="stylesheet" href="assets/site.css">\n</head>\n<body>\n'
        '<main><section><h2>Error</h2><p class="lead">This page does not exist.</p>'
        '<p><a class="cv-inline" href="./">Back to the start</a></p></section></main>\n'
        "</body>\n</html>\n"
    )
    with open(os.path.join(out_dir, "404.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(not_found)

    shutil.copyfile(os.path.join(TEMPLATES, "site.css"), os.path.join(out_dir, "assets", "site.css"))
    shutil.copyfile(os.path.join(TEMPLATES, "app.js"), os.path.join(out_dir, "assets", "app.js"))

    if site.get("photo"):
        src = site["photo"] if os.path.isabs(site["photo"]) else os.path.join(out_dir, site["photo"])
        if os.path.isfile(src):
            shutil.copyfile(src, os.path.join(out_dir, "assets", "photo.jpg"))
        else:
            print("warning: photo not found, skipping:", src)

    if site.get("cv"):
        src = site["cv"] if os.path.isabs(site["cv"]) else os.path.join(out_dir, site["cv"])
        if not os.path.isfile(src):
            print("warning: CV file not found:", src)

    open(os.path.join(out_dir, ".nojekyll"), "w").close()
    print("built:", os.path.join(out_dir, "index.html"))


def main():
    ap = argparse.ArgumentParser(description="Build a personal site from site.json")
    ap.add_argument("--out", required=True, help="output directory (contains site.json)")
    ap.add_argument("--config", help="path to site.json (default: <out>/site.json)")
    args = ap.parse_args()
    build(args.out, args.config)


if __name__ == "__main__":
    main()
