#!/usr/bin/env python3
"""Generate a *local-only* 90-source count correction for WordPress page #1338.

Never contacts WordPress and never publishes anything. Input must be an
authenticated EDIT-context export of the currently published #1338 raw Gutenberg
content. Do NOT feed this script draft #2354, whose link/copy changes are separate.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED = {"declassified": 12, "accountability": 24, "engineering": 21,
            "archives": 25, "navigation": 8}
CHANGES = [
    ("Sixty free collections, reports, databases, maps, manuals, and archival systems",
     "Ninety free collections, reports, databases, maps, manuals, and archival systems"),
    ("<b>60</b><span>curated sources</span>", "<b>90</b><span>curated sources</span>"),
    ("Search all 60 sources", "Search all 90 sources"),
    ('data-filter="all" aria-pressed="true">All <span>60</span>',
     'data-filter="all" aria-pressed="true">All <span>90</span>'),
    ('data-filter="declassified" aria-pressed="false">Declassified &amp; decisions <span>9</span>',
     'data-filter="declassified" aria-pressed="false">Declassified &amp; decisions <span>12</span>'),
    ('data-filter="accountability" aria-pressed="false">Accountability &amp; public records <span>18</span>',
     'data-filter="accountability" aria-pressed="false">Accountability &amp; public records <span>24</span>'),
    ('data-filter="engineering" aria-pressed="false">Engineering, disaster &amp; safety <span>16</span>',
     'data-filter="engineering" aria-pressed="false">Engineering, disaster &amp; safety <span>21</span>'),
    ('data-filter="archives" aria-pressed="false">Archives, maps &amp; research <span>12</span>',
     'data-filter="archives" aria-pressed="false">Archives, maps &amp; research <span>25</span>'),
    ('data-filter="navigation" aria-pressed="false">Navigation &amp; preservation <span>5</span>',
     'data-filter="navigation" aria-pressed="false">Navigation &amp; preservation <span>8</span>'),
    ("Showing all 60 sources.", "Showing all 90 sources."),
    ("const totals={all:90,declassified:12,accountability:23,engineering:21,archives:26,navigation:8}",
     "const totals={all:90,declassified:12,accountability:24,engineering:21,archives:25,navigation:8}"),
]
CARD = re.compile(r'<article class="fv-rs-card" data-cat="([^"]+)">([\s\S]*?)</article>')

def cards(raw):
    output = []
    for match in CARD.finditer(raw):
        body = match.group(2)
        titles = re.findall(r"<h3>(.*?)</h3>", body, flags=re.S)
        links = re.findall(r'<a\b[^>]*href="([^"]+)"', body)
        # Published #1338 has exactly ONE source href per card. A later
        # experimental staging version includes nested supporting anchors.
        if len(titles) != 1 or len(links) != 1:
            raise ValueError("Missing/extra title or card anchor; expected published #1338")
        url = urlsplit(links[0])
        if url.scheme != "https" or not url.netloc:
            raise ValueError("Non-HTTPS or malformed source destination")
        output.append((match.group(1), titles[0], links[0], match.group(0)))
    return output

def validate(raw):
    rows = cards(raw)
    if len(rows) != 90:
        raise ValueError(f"Expected exactly 90 cards, got {len(rows)}")
    if len(set(row[1] for row in rows)) != 90 or len(set(row[2] for row in rows)) != 90:
        raise ValueError("Duplicate title or destination; abort")
    actual = dict(Counter(row[0] for row in rows))
    if actual != EXPECTED:
        raise ValueError(f"Wrong categories: {actual}")
    return rows

def repair(raw):
    original = validate(raw)
    for before, after in CHANGES:
        if raw.count(before) != 1:
            raise ValueError(f"Unexpected baseline marker count {raw.count(before)}: {before}")
    output = raw
    for before, after in CHANGES:
        output = output.replace(before, after, 1)
    if validate(output) != original:
        raise ValueError("Source cards changed in repair; abort")
    for _, after in CHANGES:
        if output.count(after) != 1:
            raise ValueError("Corrected marker missing or duplicated")
    restored = output
    for before, after in reversed(CHANGES):
        restored = restored.replace(after, before, 1)
    if restored != raw:
        raise ValueError("Non-count content changed; abort")
    for token in ('<!-- wp:', '<script', '<style', 'href=', 'fv-rs-card'):
        if raw.count(token) != output.count(token):
            raise ValueError(f"Structural count drift in {token}")
    return output

def checksum(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Raw Gutenberg edit-context export of published #1338")
    parser.add_argument("--write", action="store_true", help="Write local candidate; never publish")
    parser.add_argument("--out", type=Path, help="Candidate UTF-8 output path, required with --write")
    args = parser.parse_args()
    source = args.source.read_text(encoding="utf-8")
    result = repair(source)
    report = {
        "target_wordpress_page": 1338, "writes_wordpress": False,
        "source_sha256": checksum(source), "candidate_sha256": checksum(result),
        "card_count": 90, "category_counts": EXPECTED,
        "unchanged_card_html": True, "unchanged_destinations": True,
        "exact_replacement_count": len(CHANGES),
    }
    print(json.dumps(report, indent=2))
    if args.write:
        if args.out is None or args.out.resolve() == args.source.resolve():
            parser.error("--write requires a distinct --out file")
        if args.out.exists():
            parser.error("Refusing to overwrite existing candidate")
        args.out.write_text(result, encoding="utf-8")

if __name__ == "__main__":
    main()
