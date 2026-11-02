#!/usr/bin/env python3
"""Read-only, fail-closed release-custody gate for Final Vestige homepage page 6.

No WordPress requests, CMS writes, credentials, subscribers, or live content in output.
Inputs are fresh, separately obtained WordPress.com pages.get(context=edit) and
page-sections.list JSON readbacks. An isolated WordPress test is NOT host parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

# Captured via read-only WordPress.com calls on 2026-11-02; change requires review.
LIVE_LOCK = {
    "id": 6,
    "status": "publish",
    "modified": "2026-10-30T09:14:14",
    "content_hash": "7afdb933d2ec68fd993ef015c97a6eb9edfe0576",
    "blocks": (
        ("core/html", "6948a35c4e60ff43154440a7fad980dc3cae6859"),
        ("core/html", "1c97fec5cc356a02fb2f51a092f749c81efcd98c"),
        ("core/html", "abc983ae1b3cf45d35589c7e5366ccc522cb0462"),
        ("core/group", "f9da41225609adcca1c23f18b39079d1275c9249"),
        ("core/html", "e53df6922591588603a41ce2e56dfdc418ba2d98"),
        ("core/html", "9454d1e44ee4932a4975796a88d2640ab9ecae8d"),
    ),
}

WP_COMMENT = re.compile(r"<!--\s*(/?)wp:([a-z0-9/-]+)[\s\S]*?-->")
SHA1 = lambda x: hashlib.sha1(x.encode("utf-8")).hexdigest()
SHA256 = lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()


def hold(code: str) -> None:
    raise ValueError("HOLD_" + code)


def unwrap(payload: dict) -> dict:
    if not isinstance(payload, dict):
        hold("READBACK_NOT_OBJECT")
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        hold("READBACK_DATA_INVALID")
    return data


def split_top_level(raw: str) -> list[tuple[str, str]]:
    """Parse Gutenberg comments with a stack: nested blocks cannot fake six roots."""
    if not isinstance(raw, str) or not raw:
        hold("EMPTY_PAGE")
    stack: list[tuple[str, int]] = []
    spans: list[tuple[str, int, int]] = []
    for token in WP_COMMENT.finditer(raw):
        closing, kind = token.group(1), token.group(2)
        self_closing = token.group(0).rstrip().endswith("/-->")
        if closing:
            if not stack or stack[-1][0] != kind:
                hold("BLOCK_NESTING_INVALID")
            stack.pop()
            if not stack:
                spans[-1] = (kind, spans[-1][1], token.end())
        elif self_closing:
            if not stack:
                spans.append((kind, token.start(), token.end()))
        else:
            if not stack:
                spans.append((kind, token.start(), -1))
            stack.append((kind, token.start()))
    if stack or not spans or any(stop < start for _, start, stop in spans):
        hold("BLOCK_NESTING_INVALID")
    if raw[:spans[0][1]].strip() or raw[spans[-1][2]:].strip():
        hold("UNOWNED_PAGE_CONTENT")
    if any(raw[a[2]:b[1]].strip() for a, b in zip(spans, spans[1:])):
        hold("UNOWNED_PAGE_CONTENT")
    return [(kind if "/" in kind else "core/" + kind, raw[start:stop])
            for kind, start, stop in spans]


def audit(page_json: dict, sections_json: dict, replacement: str,
          *, lock: dict = LIVE_LOCK) -> dict:
    page = unwrap(page_json)
    sections = unwrap(sections_json)
    if (page.get("id") != lock["id"] or page.get("status") != lock["status"]
            or page.get("modified") != lock["modified"]):
        hold("PAGE_ID_STATUS_OR_MODIFIED_DRIFT")
    if sections.get("id") != lock["id"] or sections.get("modified") != lock["modified"]:
        hold("SECTION_ID_OR_MODIFIED_DRIFT")
    if sections.get("classic_content") is not False:
        hold("UNEXPECTED_CLASSIC_CONTENT")
    body = page.get("content")
    raw = body.get("raw") if isinstance(body, dict) else body
    if not isinstance(raw, str):
        hold("RAW_PAGE_UNAVAILABLE")
    if SHA1(raw) != lock["content_hash"] or sections.get("content_hash") != lock["content_hash"]:
        hold("LIVE_PAGE_CONTENT_DRIFT")
    original = split_top_level(raw)
    listed = sections.get("sections")
    if (not isinstance(listed, list) or len(listed) != len(lock["blocks"])
            or len(original) != len(lock["blocks"])):
        hold("TOP_LEVEL_BLOCK_COUNT_DRIFT")
    for i, ((kind, chunk), listed_block, (want_kind, want_hash)) in enumerate(
            zip(original, listed, lock["blocks"])):
        if (kind != want_kind or not isinstance(listed_block, dict)
                or listed_block.get("index") != i or listed_block.get("name") != want_kind
                or listed_block.get("block_hash") != want_hash or SHA1(chunk) != want_hash):
            hold(f"BLOCK_{i}_DRIFT")
    if len(re.findall(r'<span class="fv-margin-strip__item"', original[0][1])) != 72:
        hold("MARGINS_COUNT")
    if original[3][1].count("<!-- wp:jetpack/subscriptions") != 1:
        hold("JETPACK_SUBSCRIPTION_MISSING_OR_DUPLICATED")
    protected = "".join(chunk for i, (_, chunk) in enumerate(original) if i != 1)
    if len(re.findall(r'href="/focus/"', protected)) != 2:
        hold("FOCUS_LINKS_NOT_PRESERVED")
    if ("fv-focus-cta" not in original[2][1]
            or "fv-home-shell" not in original[3][1]
            or 'type="application/ld+json"' not in original[5][1]):
        hold("PRESERVED_BLOCK_IDENTITY_CHANGED")
    replacement_blocks = split_top_level(replacement)
    if len(replacement_blocks) != 1 or replacement_blocks[0][0] != "core/html":
        hold("REPLACEMENT_NOT_ONE_HTML_BLOCK")
    if ("data-fv-home-flagship" not in replacement or "<style>" not in replacement
            or "<script>" not in replacement):
        hold("FLAGSHIP_DELIVERY_INCOMPLETE")
    preview = "".join([original[0][1], replacement] + [c for _, c in original[2:]])
    preview_blocks = split_top_level(preview)
    if len(preview_blocks) != 6 or any(
        preview_blocks[i] != original[i] for i in (0, 2, 3, 4, 5)
    ):
        hold("PROTECTED_BLOCK_MUTATED")
    rollback = "".join([preview_blocks[0][1], original[1][1]] + [c for _, c in preview_blocks[2:]])
    if rollback != raw or SHA1(rollback) != lock["content_hash"]:
        hold("ROLLBACK_NOT_BYTE_IDENTICAL")
    # No HTML, WP credentials or subscriber data printed or stored in this report.
    return {
        "status": "PREVIEW_ROLLBACK_BYTE_VERIFIED_NOT_PUBLISHED",
        "production_write": False,
        "page_id": lock["id"],
        "expected_modified": lock["modified"],
        "live_content_sha1": lock["content_hash"],
        "live_block_hashes": [h for _, h in lock["blocks"]],
        "replacement_block_sha1": SHA1(replacement),
        "replacement_bytes": len(replacement.encode("utf-8")),
        "preview_full_page_sha256": SHA256(preview),
        "rollback_full_page_sha256": SHA256(rollback),
        "preserved_block_indices": [0, 2, 3, 4, 5],
        "margins_records": 72,
        "jetpack_subscriptions": 1,
        "focus_links": 2,
        "hosted_wordpress_com_execution": "NOT_TESTED",
        "qd_wcag_and_founder_approval": "NOT_GRANTED_BY_THIS_GATE",
        "publication": "HOLD",
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--page-json", type=Path, required=True)
    p.add_argument("--sections-json", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    args = p.parse_args()
    # Fail closed on unmatched candidate source and rights, even if the same
    # unreviewed edit appeared in both its study and release fixture.
    from verify_release_content_parity import RELEASE_FIXTURE, verify_repo
    verify_repo(args.repo)
    proposed = (args.repo / RELEASE_FIXTURE).read_text(encoding="utf-8")
    report = audit(json.loads(args.page_json.read_text(encoding="utf-8")),
                   json.loads(args.sections_json.read_text(encoding="utf-8")),
                   proposed)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        # Fail without echoing raw readback contents, paths or credentials.
        category = str(exc) if str(exc).startswith("HOLD_") else type(exc).__name__
        raise SystemExit("HOLD: " + category)
