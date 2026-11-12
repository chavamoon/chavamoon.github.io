#!/usr/bin/env python3
"""Fetch the newest AI news headlines from a few RSS/Atom feeds.

Writes news.json at the repo root. Run by .github/workflows/feeds.yml, but also
safe to run by hand:

    python scripts/fetch_news.py

No third-party dependencies: urllib + xml.etree.
"""

import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

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


def fetch(source: str, url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as resp:
        root = ET.fromstring(resp.read())

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
