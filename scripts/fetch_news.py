#!/usr/bin/env python3
"""Fetch the newest AI news headlines from a few RSS/Atom feeds.

Writes news.json at the repo root. Run by .github/workflows/feeds.yml, but also
safe to run by hand:

    python scripts/fetch_news.py

Anthropic has no RSS feed, so its news index is scraped instead.

No third-party dependencies: urllib + xml.etree + re.
"""

import html
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin

FEEDS = [
    ("OpenAI", "https://openai.com/news/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss/"),
    ("DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("Sebastian Raschka", "https://sebastianraschka.com/rss_feed.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
]

PER_SOURCE = 2
TOTAL = 10
UA = "chavamoon.github.io news feed (+https://chavamoon.github.io/)"


def text_of(node, *names: str) -> str:
    for name in names:
        for child in node:
            if child.tag.split("}")[-1] == name:
                return " ".join((child.text or "").split())
    return ""


def link_of(node) -> str:
    for child in node:
        if child.tag.split("}")[-1] == "link":
            return (child.get("href") or child.text or "").strip()
    return ""


def parse_date(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    try:
        return parsedate_to_datetime(raw).date().isoformat()
    except Exception:
        pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return ""


def read(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read()


def fetch(source: str, url: str) -> list[dict]:
    root = ET.fromstring(read(url))

    nodes = root.findall(".//item")
    if not nodes:
        nodes = [n for n in root.iter() if n.tag.split("}")[-1] == "entry"]

    out = []
    for node in nodes[: PER_SOURCE * 3]:
        title = re.sub(r"\s+", " ", text_of(node, "title")).strip()
        link = link_of(node)
        if not title or not link:
            continue
        out.append(
            {
                "title": title,
                "url": link,
                "source": source,
                "published": parse_date(
                    text_of(node, "pubDate", "published", "updated", "date")
                ),
            }
        )
        if len(out) == PER_SOURCE:
            break
    return out


def fetch_anthropic() -> list[dict]:
    """Scrape anthropic.com/news: it has no RSS, but the index markup is stable.

    Each <article> holds a category link, a <time> and one anchor wrapping the
    headline. The headline anchor is the last href before the headline text, so a
    post URL can be /news/... or a bare slug like /claude-opus-5-5.
    """
    page = read("https://www.anthropic.com/news").decode("utf-8", "replace")
    out = []
    for block in page.split('<article class="W1FydW_')[1:]:
        headline = re.search(
            r'data-component="Headline"[^>]*>(.*?)</h[23]>', block, re.S
        )
        if not headline:
            continue
        pos = headline.start()

        anchor = None
        for match in re.finditer(r'<a\b[^>]*href="([^"]+)"', block):
            if match.start() >= pos:
                break
            anchor = match
        stamp = None
        for match in re.finditer(r"<time>([^<]+)</time>", block):
            if match.start() >= pos:
                break
            stamp = match
        if not (anchor and stamp):
            continue

        title = html.unescape(re.sub(r"<[^>]+>", "", headline.group(1))).strip()
        title = " ".join(title.split())
        try:
            published = datetime.strptime(
                stamp.group(1).strip(), "%b %d, %Y"
            ).date().isoformat()
        except ValueError:
            published = ""
        if not title:
            continue
        out.append(
            {
                "title": title,
                "url": urljoin("https://www.anthropic.com/news", anchor.group(1)),
                "source": "Anthropic",
                "published": published,
            }
        )
        if len(out) == PER_SOURCE:
            break
    return out


def main() -> None:
    items: list[dict] = []
    for i, (source, url) in enumerate(FEEDS):
        if i:
            time.sleep(1)
        try:
            got = fetch(source, url)
        except Exception as exc:  # a dead feed should not break the build
            print(f"skip {source}: {exc}")
            continue
        items.extend(got)
        print(f"{source}: {len(got)} items")

    try:
        got = fetch_anthropic()
        items.extend(got)
        print(f"Anthropic: {len(got)} items")
    except Exception as exc:
        print(f"skip Anthropic: {exc}")

    if not items:
        raise SystemExit("no feeds fetched")

    seen: set[str] = set()
    unique = []
    for item in items:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        unique.append(item)

    # Guarantee one headline per source, then fill the rest by date, so a quiet
    # week from one blog never makes it disappear from the list.
    by_source: dict[str, list[dict]] = {}
    for item in unique:
        by_source.setdefault(item["source"], []).append(item)
    for group in by_source.values():
        group.sort(key=lambda i: i["published"], reverse=True)

    picked = [group[0] for group in by_source.values()]
    rest = [item for group in by_source.values() for item in group[1:]]
    rest.sort(key=lambda i: i["published"], reverse=True)
    picked.extend(rest[: max(0, TOTAL - len(picked))])
    picked.sort(key=lambda i: i["published"], reverse=True)

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "items": picked,
    }
    out = Path(__file__).resolve().parent.parent / "news.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(payload['items'])} items)")


if __name__ == "__main__":
    main()
