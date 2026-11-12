#!/usr/bin/env python3
"""Fetch the newest papers for a few AI-engineering topics from the arXiv API.

Writes papers.json at the repo root. Run by .github/workflows/papers.yml on a
schedule, but also safe to run by hand:

    python scripts/fetch_papers.py

No third-party dependencies: urllib + xml.etree.
"""

import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}

TOPICS = [
    {
        "name": "Agent architectures",
        "query": '(cat:cs.MA OR cat:cs.AI) AND (abs:"LLM agents" OR abs:"agent architecture" OR abs:"agentic")',
    },
    {
        "name": "Tool use & MCP",
        "query": '(cat:cs.AI OR cat:cs.CL) AND (abs:"tool use" OR abs:"tool calling" OR abs:"model context protocol")',
    },
    {
        "name": "Retrieval & RAG",
        "query": '(cat:cs.CL OR cat:cs.IR) AND (abs:"retrieval-augmented generation" OR abs:"RAG")',
    },
    {
        "name": "Evaluation & guardrails",
        "query": '(cat:cs.AI OR cat:cs.CL) AND (abs:"agent evaluation" OR abs:"LLM judge" OR abs:"guardrails")',
    },
]

PER_TOPIC = 4


def fetch(topic_query: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "search_query": topic_query,
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    req = urllib.request.Request(
        f"{API}?{params}",
        headers={"User-Agent": "chavamoon.github.io papers feed"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())

    papers = []
    for entry in root.findall("a:entry", NS):
        raw_id = entry.findtext("a:id", default="", namespaces=NS)
        short_id = raw_id.rsplit("/abs/", 1)[-1]
        authors = [
            a.findtext("a:name", default="", namespaces=NS)
            for a in entry.findall("a:author", NS)
        ]
        papers.append(
            {
                "title": " ".join(
                    entry.findtext("a:title", default="", namespaces=NS).split()
                ),
                "authors": authors,
                "published": entry.findtext("a:published", default="", namespaces=NS)[:10],
                "id": short_id,
                "url": f"https://arxiv.org/abs/{short_id}",
            }
        )
    return papers


def main() -> None:
    topics = []
    seen: set[str] = set()
    for i, topic in enumerate(TOPICS):
        if i:
            time.sleep(3)  # arXiv asks for gentle clients
        try:
            papers = fetch(topic["query"], PER_TOPIC * 2)
        except Exception as exc:  # keep the last good data instead of failing the build
            print(f"skip {topic['name']}: {exc}")
            continue
        unique = []
        for paper in papers:
            if paper["id"] in seen:
                continue
            seen.add(paper["id"])
            unique.append(paper)
            if len(unique) == PER_TOPIC:
                break
        topics.append({**topic, "papers": unique})
        print(f"{topic['name']}: {len(unique)} papers")

    if not topics:
        raise SystemExit("no topics fetched")

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "topics": topics,
    }
    out = Path(__file__).resolve().parent.parent / "papers.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
