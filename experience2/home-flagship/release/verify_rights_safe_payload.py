#!/usr/bin/env python3
"""Fail-closed, read-only audit of the ACTUAL proposed WordPress block.

Unlike the old staging-only fixtures, this checks the exact page-6 replacement
file and the source CSS/JS in the production-rooted release branch.
No WordPress API, authenticated request, user data or production write.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys

HOME = Path(__file__).resolve().parents[1]
STYLE_NAMES = ("flagship.css", "chronicle.css", "chronicle-lens.css",
               "inquiry.css", "observer-lab.css", "reading-trail.css", "wp-integration.css")
SCRIPT_NAMES = ("flagship.js", "observer-lab.js", "chronicle-lens.js", "reading-trail.js")
TARGET = "release/production-change/"
NYPL_CAPTURE = "edit-017-v02-nypl-5003296-original.jpg"
UNSUPPORTED = "NYPL believes this item is in the public domain under United States law."
SAFE_PLATE = "ARCHIVAL REFERENCE · IMAGE NOT REPRODUCED"
OPENING = '<section class="fv-hf__opening"'
RIGHTS = (
    "NASA does not endorse Final Vestige or any product or service.",
    "The displayed scan is the Wikimedia Commons file marked public domain",
    "From The New York Public Library. Reuse rights for this exact digital capture are pending verification",
)


def chapter_interior(source: str, release: bool) -> str:
    boundary = "<style>" if release else "</main>"
    end = source.find(boundary)
    first = source.find(OPENING)
    last = source.rfind("</section>", 0, end)
    if end < 0 or first < 0 or last < first or source.find(OPENING, first + 1) >= 0:
        raise ValueError("CHAPTER_BOUNDARY_UNAVAILABLE")
    return source[first:last + len("</section>")]


def audit(source: str, block: str, styles: dict[str, str], scripts: dict[str, str],
          meta: dict, original: str) -> list[str]:
    errors = []
    def require(ok: bool, name: str) -> None:
        if not ok:
            errors.append(name)
    try:
        require(chapter_interior(source, False) == chapter_interior(block, True),
                "ACTUAL_RELEASE_EDITORIAL_PARITY")
    except ValueError:
        errors.append("CHAPTER_BOUNDARY_UNAVAILABLE")
    require(source.count(OPENING) == 1 and block.count(OPENING) == 1,
            "SEVEN_CHAPTER_WRAPPER_CUSTODY")
    require(source.count("<img ") == 2 and block.count("<img ") == 2,
            "TWO_ARCHIVAL_IMAGES_ONLY")
    require(all(NYPL_CAPTURE not in v and UNSUPPORTED not in v for v in (source, block)),
            "UNVERIFIED_NYPL_CAPTURE_OR_PUBLIC_DOMAIN_CLAIM")
    require(SAFE_PLATE in source and SAFE_PLATE in block, "ORIGINAL_SOURCE_PLATE_MISSING")
    require(all(t in source and t in block for t in RIGHTS), "ARCHIVAL_CREDIT_MISSING")
    require(block.startswith("<!-- wp:html -->\n") and
            block.rstrip().endswith("<!-- /wp:html -->"), "WORDPRESS_HTML_BLOCK_WRAPPER")

    matches = list(re.finditer(r"/\* ==== ([\w.\-]+\.css) ==== \*/\n", block))
    inline_css = block.split("<style>", 1)[1].split("</style>", 1)[0] if (
        block.count("<style>") == block.count("</style>") == 1) else ""
    marks = list(re.finditer(r"/\* ==== ([\w.\-]+\.css) ==== \*/\n", inline_css))
    require(len(marks) == len(STYLE_NAMES) and
            tuple(m.group(1) for m in marks) == STYLE_NAMES,
            "CSS_MODULE_ORDER_AND_CARDINALITY")
    for i, name in enumerate(STYLE_NAMES):
        if len(marks) == len(STYLE_NAMES):
            chunk = inline_css[marks[i].end():marks[i+1].start() if i+1<len(marks) else len(inline_css)]
            require(chunk.strip() == styles[name].replace("\r\n","\n").strip(), "INLINE_CSS_BYTE_PARITY_" + name)
    embedded_scripts = re.findall(r"<script>([\s\S]*?)</script>", block)
    require(len(embedded_scripts) == len(SCRIPT_NAMES), "INLINE_SCRIPT_CARDINALITY")
    for i, name in enumerate(SCRIPT_NAMES):
        if len(embedded_scripts) == len(SCRIPT_NAMES):
            require(embedded_scripts[i].strip() == scripts[name].strip(),
                    "INLINE_SCRIPT_BYTE_PARITY_" + name)
    require(block.count("data:image/svg+xml,") == 2, "PINNED_ORIGINAL_INLINE_GRAIN_COUNT")
    require(block.count("https://finalvestige.com/focus/") >= 1,
            "FOCUS_FIELD_BOOK_LINK_MISSING")
    require("jetpack/subscriptions" not in block, "SUBSCRIBER_BLOCK_MUST_REMAIN_OUTSIDE_REPLACEMENT")
    require("DESIGN CANDIDATE" not in block, "DEVELOPMENT_MARKER_LEAK")
    raw = block.encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    sha1 = hashlib.sha1(raw).hexdigest()
    apply = meta.get("apply", {})
    rollback = meta.get("rollback", {})
    require(apply.get("replacement_sha256") == digest and
            apply.get("replacement_sha1") == sha1 and
            apply.get("replacement_bytes") == len(raw), "WRONG_RELEASE_PAYLOAD_DIGEST_OR_SIZE")
    require(rollback.get("params", {}).get("expected_block_hash") == sha1,
            "ROLLBACK_EXPECTED_REPLACEMENT_HASH_STALE")
    require(meta.get("target", {}).get("wpcom_site") == 256784396 and
            meta.get("target", {}).get("page_id") == 6 and
            meta.get("target", {}).get("block_to_replace", {}).get("index") == 1 and
            apply.get("params", {}).get("expected_block_hash") ==
            meta.get("target", {}).get("block_to_replace", {}).get("block_hash_sha1"),
            "PRODUCTION_PAGE_SECTION_GUARD_CHANGED")
    require(hashlib.sha1(original.encode("utf-8")).hexdigest() ==
            meta.get("target", {}).get("block_to_replace", {}).get("block_hash_sha1"),
            "ORIGINAL_ROLLBACK_HASH_CHANGED")
    require(meta.get("status", "").startswith("PROPOSED - NOT APPLIED") and
            meta.get("no_plugin_install") is True and
            meta.get("no_theme_or_navigation_change") is True,
            "PRODUCTION_RELEASE_HOLD_GUARDS_CHANGED")
    return errors


def read_and_audit(home: Path = HOME) -> list[str]:
    base = home / "release" / "production-change"
    return audit((home / "index.html").read_text("utf-8"),
                 (base / "replacement-block-index1.html").read_text("utf-8"),
                 {n:(home/("wp-candidate" if n=="wp-integration.css" else "")/n).read_text("utf-8") for n in STYLE_NAMES},
                 {n:(home/n).read_text("utf-8") for n in SCRIPT_NAMES},
                 json.loads((base/"PROPOSED_PRODUCTION_CHANGE.json").read_text("utf-8")),
                 (base/"original-block-index1.html").read_text("utf-8"))


if __name__ == "__main__":
    problems = read_and_audit()
    print(json.dumps({"status":"DRAFT_PAYLOAD_PARITY_PASS_NOT_RELEASE_APPROVED" if not problems else "HOLD",
                      "errors":problems,"production_writes":0,"release":"HOLD"},indent=2))
    sys.exit(2 if problems else 0)
