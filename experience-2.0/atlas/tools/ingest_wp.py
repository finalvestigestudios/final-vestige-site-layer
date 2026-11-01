#!/usr/bin/env python3
"""Ingest published Final Vestige posts into candidate Atlas investigation records.

Read-only: uses the public WordPress REST API (GET) and never writes to the site. The output is a snapshot with a
content hash per post, so a later run can report which posts changed and need editorial re-review.

  python ingest_wp.py --fetch                 # fetch live, write atlas/data/wp_snapshot.json
  python ingest_wp.py --from-file snap.json   # re-use a saved REST response (offline / tests)
  python ingest_wp.py --check                 # compare the committed snapshot with the live site (network)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ATLAS = Path(__file__).resolve().parent.parent
SNAPSHOT = ATLAS / "data" / "wp_snapshot.json"
SITE = "https://finalvestige.com"
POST_IDS = [434, 621, 370, 269, 37, 433]
FIELDS = "id,link,slug,date,modified,title,excerpt,content,categories,tags"

# Hosts we can name an institution for. Anything else is recorded as an unclassified outbound link, never guessed.
INSTITUTION_BY_HOST = {
    "nasa.gov": "NASA", "images-assets.nasa.gov": "NASA", "loc.gov": "Library of Congress", "nypl.org": "New York Public Library",
    "digitalcollections.nypl.org": "New York Public Library", "archives.gov": "U.S. National Archives", "catalog.archives.gov": "U.S. National Archives",
    "history.navy.mil": "U.S. Navy Naval History and Heritage Command", "novascotia.ca": "Province of Nova Scotia",
    "whc.unesco.org": "UNESCO World Heritage Centre", "britannica.com": "Encyclopaedia Britannica",
}


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append({"url": self._href, "text": " ".join("".join(self._text).split())[:140]})
            self._href = None


def outbound_links(content_html: str) -> list[dict]:
    parser = _Links()
    parser.feed(content_html)
    seen, out = set(), []
    for link in parser.links:
        parts = urlsplit(link["url"])
        host = (parts.hostname or "").removeprefix("www.")
        if parts.scheme != "https" or not host or host == "finalvestige.com" or link["url"] in seen:
            continue
        seen.add(link["url"])
        root = ".".join(host.split(".")[-2:]) if host.endswith(".gov") or host.endswith(".org") or host.endswith(".com") else host
        institution = INSTITUTION_BY_HOST.get(host) or INSTITUTION_BY_HOST.get(root)
        out.append({"url": link["url"], "host": host, "text": link["text"], "institution": institution})
    return out


def _get(url: str, attempts: int = 3):
    """GET JSON, honouring Retry-After on 429/503 so a rate limit is waited out instead of hammered."""
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, headers={"User-Agent": "FinalVestige-Atlas-Ingest/0.1 (read-only)"})
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 503) or attempt == attempts:
                raise
            wait = min(int(exc.headers.get("Retry-After", "20") or 20), 90)
            print(f"HTTP {exc.code}; waiting {wait}s before retry {attempt}/{attempts - 1}", file=sys.stderr)
            time.sleep(wait)


def fetch_live() -> tuple[list[dict], dict[int, dict]]:
    ids = ",".join(str(i) for i in POST_IDS)
    posts = _get(f"{SITE}/wp-json/wp/v2/posts?include={ids}&per_page=20&_fields={FIELDS}")
    cat_ids = sorted({c for p in posts for c in p.get("categories", [])})
    cats = {}
    if cat_ids:
        for c in _get(f"{SITE}/wp-json/wp/v2/categories?include={','.join(map(str, cat_ids))}&per_page=50&_fields=id,name,slug"):
            cats[c["id"]] = {"name": c["name"], "slug": c["slug"]}
    return posts, cats


def normalise(posts: list[dict], cats: dict[int, dict]) -> dict:
    items = []
    for post in sorted(posts, key=lambda p: p["id"]):
        content = post["content"]["rendered"]
        items.append({
            "wordpress_post_id": post["id"],
            "url": post["link"],
            "slug": post["slug"],
            "title": post["title"]["rendered"],
            "published": post["date"],
            "modified": post["modified"],
            "categories": [cats.get(c, {"name": f"category-{c}", "slug": str(c)}) for c in post.get("categories", [])],
            "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "content_chars": len(content),
            "outbound_sources": outbound_links(content),
            "review_status": "unreviewed",
        })
    return {"snapshot_of": SITE, "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "posts": items}


def diff(committed: dict, fresh: dict) -> list[str]:
    old = {p["wordpress_post_id"]: p for p in committed["posts"]}
    notes = []
    for p in fresh["posts"]:
        o = old.get(p["wordpress_post_id"])
        if o is None:
            notes.append(f"NEW post {p['wordpress_post_id']} {p['title']}")
        elif o["content_sha256"] != p["content_sha256"]:
            notes.append(f"CHANGED post {p['wordpress_post_id']} {p['title']} (modified {o['modified']} -> {p['modified']}): re-review required")
        elif o["url"] != p["url"]:
            notes.append(f"URL CHANGED post {p['wordpress_post_id']}: {o['url']} -> {p['url']}")
    for pid in old:
        if pid not in {p["wordpress_post_id"] for p in fresh["posts"]}:
            notes.append(f"MISSING post {pid}: no longer published at that id")
    return notes


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fetch", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--from-file")
    args = ap.parse_args()
    if args.from_file:
        raw = json.loads(Path(args.from_file).read_text(encoding="utf-8"))
        cats = {int(k): v for k, v in raw.get("categories", {}).items()}
        snap = normalise(raw["posts"], cats)
    else:
        try:
            posts, cats = fetch_live()
        except Exception as exc:  # network failure is reported, never treated as success
            print(f"FAIL: could not read {SITE}: {exc}", file=sys.stderr)
            return 2
        snap = normalise(posts, cats)
    if args.check:
        notes = diff(json.loads(SNAPSHOT.read_text(encoding="utf-8")), snap)
        print("\n".join(notes) if notes else "OK: live site matches committed snapshot")
        return 1 if notes else 0
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {SNAPSHOT.name}: {len(snap['posts'])} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
