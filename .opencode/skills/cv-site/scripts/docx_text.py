#!/usr/bin/env python3
"""Extract readable text from a .docx file. Standard library only.

Usage:
    python docx_text.py <file.docx> [--json]

Prints a light Markdown-ish rendering: headings become #, list paragraphs
become "-", tables become pipe rows. Copied text should be treated as the
source of truth; never invent facts that are not in this output.
"""
import argparse
import json
import re
import sys

# Windows consoles default to a legacy code page; keep accented paths printable.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def para_style(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        return ""
    st = ppr.find(W + "pStyle")
    return st.get(W + "val", "") if st is not None else ""


def para_text(p):
    chunks = []
    for node in p.iter():
        if node.tag == W + "t":
            chunks.append(node.text or "")
        elif node.tag == W + "tab":
            chunks.append("\t")
        elif node.tag == W + "br":
            chunks.append("\n")
    return "".join(chunks).strip()


def is_numbered(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        return False
    return ppr.find(W + "numPr") is not None


def table_rows(tbl):
    rows = []
    for tr in tbl.findall(W + "tr"):
        cells = []
        for tc in tr.findall(W + "tc"):
            text = " ".join(para_text(p) for p in tc.findall(W + "p") if para_text(p))
            cells.append(text.strip())
        if any(cells):
            rows.append(cells)
    return rows


def extract(path):
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find(W + "body")
    out = []
    if body is None:
        return ""

    for child in body:
        if child.tag == W + "p":
            text = para_text(child)
            if not text:
                continue
            style = para_style(child).lower()
            if style.startswith("heading") or style in ("title", "subtitle"):
                level = re.sub(r"\D", "", style) or "1"
                out.append("#" * min(int(level) if level.isdigit() else 1, 6) + " " + text)
            elif is_numbered(child):
                out.append("- " + text)
            else:
                out.append(text)
        elif child.tag == W + "tbl":
            rows = table_rows(child)
            if not rows:
                continue
            width = max(len(r) for r in rows)
            for r in rows:
                r += [""] * (width - len(r))
                out.append(" | ".join(c.strip() for c in r))
            out.append("")
    return "\n\n".join(out).strip()


def main():
    ap = argparse.ArgumentParser(description="Extract text from a .docx file")
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true", help="print JSON with path and text")
    args = ap.parse_args()
    try:
        text = extract(args.path)
    except zipfile.BadZipFile:
        sys.exit("not a .docx file (zip): " + args.path)
    except KeyError:
        sys.exit("word/document.xml missing: " + args.path)

    if args.json:
        print(json.dumps({"path": args.path, "text": text}, ensure_ascii=False, indent=2))
    else:
        print(text)


if __name__ == "__main__":
    main()
