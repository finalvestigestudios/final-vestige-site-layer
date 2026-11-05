"""Inert saved-source auditor: affiliate view vs. click endpoints.

Consumes a user-supplied, sanitized WordPress pages snapshot. No network or
WordPress writes, tracking scripts, sales estimates, or automatic release actions.
A browser/network trace is required to prove real requests or cookie behavior.
"""
from __future__ import annotations

import argparse
import html
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class Sources(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[dict] = []
        self.images: list[dict] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a)
        elif tag == "img" and a.get("src"):
            self.images.append(a)


def _url_kind(url: str) -> str:
    try:
        u = urlsplit(html.unescape(url).strip())
    except ValueError:
        return "invalid"
    host = (u.hostname or "").lower()
    path = u.path.lower()
    if host in ("www.awin1.com", "awin1.com"):
        if path == "/cshow.php":
            return "awin_creative_view_url"
        if path in ("/cread.php", "/awclick.php", "/pclick.php"):
            return "awin_click_url"
        return "awin_other_url"
    if host and host not in ("finalvestige.com", "www.finalvestige.com"):
        return "external_other"
    return "site_or_relative"


def audit_page(page: dict) -> dict:
    parser = Sources()
    content = page.get("content", "")
    if isinstance(content, dict):
        content = content.get("raw") or content.get("rendered") or ""
    parser.feed(str(content))
    link_clicks = [l for l in parser.links if _url_kind(l["href"]) == "awin_click_url"]
    view_images = [i for i in parser.images if _url_kind(i["src"]) == "awin_creative_view_url"]
    other_external = [l for l in parser.links if _url_kind(l["href"]) == "external_other"]
    sponsored_incomplete = [l for l in link_clicks if not {"sponsored", "noopener", "noreferrer"}.issubset(set(l.get("rel", "").split()))]
    view_image_missing_alt = [i for i in view_images if not i.get("alt", "").strip()]
    meta = page.get("meta") or {}
    return {
        "id": page.get("id"), "slug": page.get("slug"), "status": page.get("status"),
        "awin_click_link_count": len(link_clicks),
        "awin_creative_view_image_count": len(view_images),
        "external_non_awin_link_count": len(other_external),
        "sponsored_attribute_failures": len(sponsored_incomplete),
        "view_image_missing_alt_count": len(view_image_missing_alt),
        "dedicated_seo_description_present": bool(str(meta.get("advanced_seo_description") or "").strip()),
        "review_flags": [
            *(["third_party_image_request_on_render_review_consent_and_network"] if view_images else []),
            *(["direct_external_links_review_attribution_not_necessarily_defect"] if other_external else []),
            *(["sponsored_link_attribute_incomplete"] if sponsored_incomplete else []),
            *(["image_alt_missing"] if view_image_missing_alt else []),
            *(["dedicated_seo_description_empty"] if not str(meta.get("advanced_seo_description") or "").strip() else []),
        ],
    }


def audit_snapshot(data: dict) -> dict:
    pages = data.get("pages")
    if not isinstance(pages, list):
        raise ValueError("snapshot must contain pages: [objects]")
    out = [audit_page(p) for p in pages]
    return {"pages": out, "method": "saved_source_only_not_browser_or_consent_evidence", "network_requests_performed": 0}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("snapshot", type=Path, help="Locally held, sanitized {pages:[...]} JSON")
    args = p.parse_args()
    print(json.dumps(audit_snapshot(json.loads(args.snapshot.read_text(encoding="utf8"))), indent=2))


if __name__ == "__main__":
    main()
