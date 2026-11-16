#!/usr/bin/env python3
"""Check a generated site before publishing. Standard library only.

Usage:
    python verify.py --dir <site-dir>
    python verify.py --dir <site-dir> --no-net
    python verify.py --dir <site-dir> --json

Checks structure, internal links, anchors, image alt text, bilingual
parity, duplicate ids and an accidental phone number. External links are
requested with a short timeout; 403/405/429 count as "reachable but
blocking bots", not as broken.

Exit code 1 when there is at least one error.
"""
import argparse
import json
import os
import re
import sys

# Windows consoles default to a legacy code page; keep accented paths printable.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import urllib.error
import urllib.request
from html.parser import HTMLParser

PHONE = re.compile(r"(?<!\d)(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}(?!\d)")
SOCIAL = ("linkedin.com", "github.com", "x.com", "twitter.com", "mastodon", "bsky.app")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []       # (tag, attr, value)
        self.imgs = []        # dicts
        self.titles = []
        self._in_title = False
        self._in_a = []
        self.text = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(("a", a["href"]))
        if tag in ("link", "script") and (a.get("href") or a.get("src")):
            self.links.append((tag, a.get("href") or a.get("src")))
        if tag == "img":
            self.imgs.append(a)
        if tag == "title":
            self._in_title = True
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.titles.append(data)
        if not self._skip:
            self.text.append(data)


def parse(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    c = Collector()
    c.feed(raw)
    return c, raw


def external_ok(url, timeout=8):
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; cv-site-verify/1.0)",
            "Accept": "text/html,application/pdf,*/*",
            "Range": "bytes=0-2048",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as exc:
        return exc.code, str(exc.reason)
    except Exception as exc:  # noqa: BLE001 - network failures are reported, not raised
        return 0, str(exc)


def check(root, net=True, timeout=8):
    errors = []
    warnings = []
    notes = []

    def err(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    index = os.path.join(root, "index.html")
    if not os.path.isfile(index):
        return ["index.html missing — run build.py first"], [], []

    for rel in ("404.html", "assets/site.css", "assets/app.js", "site.json"):
        if not os.path.isfile(os.path.join(root, rel)):
            err("missing file: " + rel)

    try:
        with open(os.path.join(root, "site.json"), encoding="utf-8") as fh:
            site = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        return ["site.json is not valid JSON: " + str(exc)], warnings, notes

    total = check_doc(root, index, site, err, warn, notes, net, timeout, "index.html")

    nf = os.path.join(root, "404.html")
    if os.path.isfile(nf):
        c, raw = parse(nf)
        for tag, href in c.links:
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target = href.split("#")[0].lstrip("./")
            if target and not os.path.exists(os.path.join(root, target)):
                err("404.html links to a missing file: " + href)

    if len(c_text(nf)) < 10:
        warn("404.html has almost no text")

    if net:
        seen = set()
        for url in sorted({h for h in total if h.startswith("http")}):
            if url in seen:
                continue
            seen.add(url)
            if "example.com" in url:
                notes.append("placeholder link (not checked): " + url)
                continue
            status, reason = external_ok(url, timeout)
            if status == 0:
                warn("unreachable (network): " + url + " — " + reason)
            elif status in (401, 403, 405, 429):
                notes.append("blocked to bots (" + str(status) + "): " + url)
            elif status >= 400:
                err("broken link (" + str(status) + "): " + url)
            else:
                notes.append("ok (" + str(status) + "): " + url)
    return errors, warnings, notes


def c_text(path):
    if not os.path.isfile(path):
        return ""
    c, _ = parse(path)
    return "".join(c.text).strip()


def check_doc(root, path, site, err, warn, notes, net, timeout, label):
    c, raw = parse(path)

    if not c.titles or not "".join(c.titles).strip():
        err(label + ": empty <title>")
    if not re.search(r"<meta[^>]+name=[\"']description[\"']", raw):
        warn(label + ": no meta description")
    if not re.search(r"<h1[\s>]", raw):
        err(label + ": no <h1>")

    dupes = {i for i in c.ids if c.ids.count(i) > 1}
    for d in sorted(dupes):
        warn(label + ": duplicate id " + d)

    for img in c.imgs:
        if "alt" not in img:
            err(label + ": <img> without alt: " + (img.get("src") or "?"))
        src = img.get("src", "")
        if src and not src.startswith(("http", "data:")):
            if not os.path.exists(os.path.join(root, src)):
                err(label + ": missing image " + src)

    externals = []
    seen_local = set()
    for tag, href in c.links:
        if href.startswith(("mailto:", "tel:", "data:")):
            if href.startswith("tel:"):
                warn(label + ": phone number exposed via tel: link")
            continue
        if href.startswith(("http://", "https://")):
            externals.append(href)
            continue
        if href.startswith("#"):
            if href != "#" and href[1:] not in c.ids:
                err(label + ": anchor target missing: " + href)
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        if not os.path.exists(os.path.join(root, target.lstrip("/"))):
            if target not in seen_local:
                seen_local.add(target)
                err(label + ": missing local file: " + href)

    if os.path.isfile(os.path.join(root, "assets", "photo.jpg")) and not any(
        (i.get("class") or "") == "photo" for i in c.imgs
    ):
        warn(label + ": assets/photo.jpg exists but is not used")

    text = "".join(c.text)
    if len(text) < 200:
        warn(label + ": very little text (" + str(len(text)) + " chars)")

    if PHONE.search(text):
        for m in PHONE.finditer(text):
            digits = re.sub(r"\D", "", m.group(0))
            if 9 <= len(digits) <= 15:
                warn(label + ": possible phone number in text: " + m.group(0).strip())
                break

    if site.get("cv"):
        cv = os.path.join(root, site["cv"])
        if os.path.isfile(cv) and os.path.getsize(cv) < 5000:
            warn("CV file looks too small: " + site["cv"])

    if site.get("lang") == "both":
        en = raw.count('data-lang="en"')
        es = raw.count('data-lang="es"')
        if not (en and es):
            err(label + ": lang is 'both' but a language block is missing")
        else:
            for lang in ("en", "es"):
                block = extract_block(raw, lang)
                if len(block) < 400:
                    warn(label + ": " + lang + " version looks thin (" + str(len(block)) + " chars)")
            if abs(len(extract_block(raw, "en")) - len(extract_block(raw, "es"))) > 0.5 * max(
                1, len(extract_block(raw, "en"))
            ):
                warn(label + ": EN and ES versions differ a lot in length")

    if net and not externals:
        notes.append(label + ": no external links")

    return externals


def extract_block(raw, lang):
    marker = 'data-lang="' + lang + '"'
    i = raw.find(marker)
    if i < 0:
        return ""
    j = raw.find('data-lang="', i + len(marker))
    return raw[i : j if j > 0 else len(raw)]


def main():
    ap = argparse.ArgumentParser(description="Verify a generated personal site")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--no-net", action="store_true", help="skip external link checks")
    ap.add_argument("--timeout", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.dir)
    errors, warnings, notes = check(root, net=not args.no_net, timeout=args.timeout)

    if args.json:
        print(json.dumps({"errors": errors, "warnings": warnings, "notes": notes}, indent=2))
    else:
        for msg in errors:
            print("ERROR  " + msg)
        for msg in warnings:
            print("WARN   " + msg)
        for msg in notes:
            print("note   " + msg)
        print()
        print(str(len(errors)) + " error(s), " + str(len(warnings)) + " warning(s)")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
