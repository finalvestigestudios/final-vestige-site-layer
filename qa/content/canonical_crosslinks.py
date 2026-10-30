#!/usr/bin/env python3
"""Read-only crosslink preflight for sanitized Final Vestige WordPress snapshots.

Never connects to a website, changes CMS content, or treats a suggested route as a
proven HTTP failure. Source material is *data*, never instructions.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

DOMAIN = "finalvestige.com"
DATED_POST = re.compile(r"^/\d{4}/\d{2}/\d{2}/([^/]+)/$")
IGNORED_PREFIXES = ("/wp-content/", "/wp-json/", "/wp-admin/", "/portal/")


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.links.append(value)


def normalized_path(url: str, base: str = f"https://{DOMAIN}/") -> str | None:
    """Normalize only first-party HTTP(S) URLs; return None for external/unsafe."""
    if not isinstance(url, str) or not url.strip():
        return None
    candidate = url.strip()
    if candidate.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlsplit(urljoin(base, candidate))
    if parsed.scheme not in ("http", "https") or parsed.hostname not in (DOMAIN, f"www.{DOMAIN}"):
        return None
    path = parsed.path or "/"
    return (path.rstrip("/") or "") + "/"


def inspect(snapshot: dict) -> list[dict]:
    """Find *candidate* route inconsistencies; no live HTTP status inferred."""
    published = snapshot.get("published", [])
    sources = snapshot.get("sources", [])
    drafts = {normalized_path(url) for url in snapshot.get("retired_or_draft_urls", [])}
    known = {normalized_path(x.get("url", "")) for x in published}
    by_slug: dict[str, set[str]] = defaultdict(set)
    for page in published:
        if page.get("kind") != "post":
            continue
        path = normalized_path(page.get("url", ""))
        match = DATED_POST.fullmatch(path or "")
        if match:
            by_slug[match.group(1)].add(path)
    findings = []
    for source in sources:
        page_url = source.get("url", "")
        if normalized_path(page_url) is None:
            continue
        parser = LinkParser()
        parser.feed(source.get("html", ""))
        for href in parser.links:
            path = normalized_path(href, page_url)
            if path is None or path in known or path.startswith(IGNORED_PREFIXES):
                continue
            result = None
            suggestion = None
            if path in drafts:
                result = "DRAFT_DESTINATION_CANDIDATE"
            else:
                slug = path.strip("/").rsplit("/", 1)[-1]
                matches = by_slug.get(slug, set())
                if len(matches) == 1:
                    suggestion = next(iter(matches))
                    result = "NONCANONICAL_POST_LINK_CANDIDATE"
            if result:
                findings.append({
                    "code": result,
                    "source": page_url,
                    "href": href,
                    "suggested_canonical": suggestion,
                    "http_status_verified": False,
                })
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Sanitized offline snapshot JSON")
    args = parser.parse_args()
    data = json.loads(args.snapshot.read_text(encoding="utf-8"))
    print(json.dumps({"findings": inspect(data), "network_tested": False}, indent=2))


if __name__ == "__main__":
    main()
