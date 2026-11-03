#!/usr/bin/env python3
"""Read-only release drift and archival reproduction guard for Final Vestige page 6.

Consumes a LOCAL permissioned WordPress pages.get JSON export plus a source-controlled
candidate. Makes no network calls or CMS writes. Outputs summary metadata, not content,
subscriber data, credentials or WordPress databases. Never authorizes publication.
"""
from __future__ import annotations

import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote

FORBIDDEN_MEDIA_TOKENS = (
    "edit-017-v02-nypl-5003296-original.jpg",
    "edit-017-v02-nypl-5003296-original",
)


class ImageReferenceParser(HTMLParser):
    """Collect fetch-capable HTML media attributes, excluding catalog hyperlinks."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in ("img", "source", "video", "image", "picture"):
            return
        fetching = {"src", "srcset", "data-src", "data-srcset", "poster", "href", "xlink:href"}
        for key, value in attrs:
            if key and key.lower() in fetching and value:
                self.references.append(value)


def normalize_url(value: str) -> str:
    value = unescape(value).lower()
    for _ in range(3):
        earlier = value
        value = unquote(value)
        if value == earlier:
            break
    return value


def fetch_capable_urls(source: str) -> list[str]:
    parser = ImageReferenceParser()
    parser.feed(source)
    parser.references.extend(re.findall(r"url\(\s*['\"]?([^\)'\"]+)", source, flags=re.I))
    return [normalize_url(ref) for ref in parser.references]


def reproduced_nypl_map(source: str) -> bool:
    return any(token in ref for ref in fetch_capable_urls(source)
               for token in FORBIDDEN_MEDIA_TOKENS)


def unpack_page(obj: dict) -> dict:
    """Accept page data or WordPress connector/REST data wrappers, raw content only."""
    if not isinstance(obj, dict):
        raise ValueError("not a WordPress page object")
    if isinstance(obj.get("structuredContent"), dict):
        obj = obj["structuredContent"]
    if isinstance(obj.get("data"), dict):
        obj = obj["data"]
    content = obj.get("content")
    if isinstance(content, dict):
        content = content.get("raw")
    if not isinstance(content, str):
        raise ValueError("raw WordPress content required; rendered content not sufficient")
    if obj.get("id") != 6 or obj.get("status") != "publish":
        raise ValueError("unexpected site page or unpublished revision")
    return {**obj, "content": content}


def html_blocks(content: str) -> list[str]:
    return re.findall(r"<!-- wp:html(?: [^>]*)? -->(.*?)<!-- /wp:html -->",
                      content, flags=re.S)


def audit_page(page_data: dict, candidate: str, expected_modified: str | None = None) -> dict:
    page = unpack_page(page_data)
    source = page["content"]
    blocks = html_blocks(source)
    flagship = [b for b in blocks if "fv-hf__opening" in b and "fv-hf__case" in b]
    margin_count = len(re.findall(r"<span\s+class=['\"]fv-margin-strip__item['\"]",
                                  source, flags=re.I))
    jetpack = len(re.findall(r"<!--\s*wp:jetpack/subscriptions\b", source))
    focus_links = len(re.findall(
        r"<a\b[^>]*href=['\"](?:https://finalvestige\.com)?/?focus/?['\"][^>]*>",
        source, flags=re.I))
    live_nypl = reproduced_nypl_map(source)
    candidate_nypl = reproduced_nypl_map(candidate)
    live_flagship = flagship[0] if len(flagship) == 1 else None
    candidate_blocks = html_blocks(candidate)
    candidate_payload = candidate_blocks[0] if len(candidate_blocks) == 1 else candidate
    same_payload = live_flagship is not None and live_flagship == candidate_payload
    guards = {
        "margins_72_present": margin_count == 72,
        "jetpack_subscription_present": jetpack == 1,
        "fieldbook_links_preserved": focus_links >= 2,
        "one_flagship_block": len(flagship) == 1,
        "candidate_rights_safe": not candidate_nypl,
        "live_rights_safe": not live_nypl,
        "live_exact_candidate": same_payload,
        "expected_modified": expected_modified is None or page.get("modified") == expected_modified,
    }
    return {
        "page_id": 6,
        "status": page.get("status"),
        "modified": page.get("modified"),
        "raw_content_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
        "html_block_count": len(blocks),
        "flagship_block_count": len(flagship),
        "margin_item_count": margin_count,
        "jetpack_subscription_count": jetpack,
        "fieldbook_link_count": focus_links,
        "live_archival_map_reproduction": live_nypl,
        "candidate_archival_map_reproduction": candidate_nypl,
        "candidate_media_ref_count": len(fetch_capable_urls(candidate)),
        "guards": guards,
        "release_decision": "HOLD",
        "manual_gates": ["founder exact approval", "independent QD", "rights review",
                         "hosted WordPress.com compatibility",
                         "manual accessibility/device QA"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wp-page-json", type=Path, required=True,
                        help="LOCAL raw page 6 JSON export; never upload source or credentials")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--expected-modified", default=None)
    args = parser.parse_args()
    try:
        page_data = json.loads(args.wp_page_json.read_text(encoding="utf-8"))
        result = audit_page(page_data, args.candidate.read_text(encoding="utf-8"),
                            args.expected_modified)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"release_decision": "HOLD", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if all(result["guards"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
