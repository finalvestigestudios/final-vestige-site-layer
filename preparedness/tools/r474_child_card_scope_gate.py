#!/usr/bin/env python3
"""R474: fail-closed Article #15 / Tool #104 child-card purpose & citation custody.

Read-only review gate. It does not revise parenting/school advice, register new
sources, persist children's data, approve privacy claims, or publish anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HOLD = "DRAFT_HARD_HOLD"
ARTICLE = "family-communication-plan"
TOOL = "family-reunification-card"
EVIDENCE = {
    "content/articles/family-communication-plan.body.html": "8ac8bd7dba3be15d477c15737e54d83364d72527",
    "content/articles/family-communication-plan.meta.json": "dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3",
    "content/tools/family-reunification-card.body.html": "be8698ac5d020476ff649d85813810e2000c6f98",
    "content/tools/family-reunification-card.meta.json": "47da1e7e20e39f0ea85e26d54a8d58301f6e0a15",
}
EDITORIAL_HEAD = "8cecc7ff09fe7e89a1eda366f1de574b39be84bd"
EDITORIAL_BLOB = "c83330dbc53625be81e30c681aa6df35308ab52e"
MANIFEST_BLOB = "3b90c422aa85fdcbd26b7d4f09a123c3dbf26ffc"
PARENT_HEAD = "42f3cfc57b5bd6f065980d40236a42fe1ac4b4a0"
REVIEW_SOURCES = (
    ("cdc-child-keeping-safe-2025-review-only", "2025-12-16", "https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html"),
    ("cdc-child-before-during-after-2025-review-only", "2025-12-24", "https://www.cdc.gov/children-and-school-preparedness/before-during-after/index.html"),
    ("cdc-child-backpack-2020-catalog-review-only", "2020", "https://stacks.cdc.gov/view/cdc/139829"),
)
DECISIONS = (
    "child_backpack_vs_adult_public_carry", "printed_card_sensitive_information",
    "school_authorized_pickup", "cdc_2025_source_registration",
    "school_and_clinician_context", "local_only_privacy_security",
    "qualified_accessibility_print_review", "native_wp_preview_citation_parity",
)
REQUIRED_OLD_IDS = frozenset(("shelter-cdc-reunification", "shelter-ready-plan-form", "shelter-co-oss-reunification"))


class Hold(ValueError):
    pass


def need(ok: bool, reason: str):
    if not ok:
        raise Hold(reason)


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def strict_json(raw: bytes) -> dict:
    def unique(pairs):
        out = {}
        for k, v in pairs:
            need(k not in out, "duplicate JSON key: " + k)
            out[k] = v
        return out
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    need(type(obj) is dict, "JSON root must be object")
    return obj


def checked_file(root: Path, rel: str, sha: str) -> bytes:
    root = root.resolve()
    path = root / rel
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root),
         "unavailable or linked native input: " + rel)
    raw = path.read_bytes()
    need(blob_sha(raw) == sha, "original Git blob mismatch: " + rel)
    return raw


def validate_manifest(m: dict):
    need(m.get("schema") == "fv-preparedness-r474-child-card-purpose-review-v1", "review schema altered")
    need(m.get("integration_parent_sha") == PARENT_HEAD and
         m.get("editorial_review_head_sha") == EDITORIAL_HEAD and
         m.get("editorial_e466_memo_blob") == EDITORIAL_BLOB, "cross-agent review SHA drift")
    need(m.get("original_blobs") == EVIDENCE, "original 4-file blob custody changed")
    need(m.get("article_number") == 15 and m.get("tool_number") == 104 and
         m.get("tool_102_is_distinct") is True, "article / tool identity conflated")
    need(m.get("release") == HOLD and m.get("may_publish") is False and
         m.get("qualified_qd_pass") is False and
         m.get("child_medical_advice_approved") is False and
         m.get("child_privacy_verified") is False and
         m.get("school_pickup_rules_universal") is False and
         m.get("commercial_offer_approved") is False, "false release, privacy or commerce clearance")
    sources = m.get("review_only_sources")
    need(type(sources) is list and len(sources) == len(REVIEW_SOURCES), "new source review inventory changed")
    need(tuple((s.get("id"), s.get("published"), s.get("url")) for s in sources if type(s) is dict)
         == REVIEW_SOURCES, "new CDC source URL/date/identity drift")
    for s in sources:
        need(s.get("citation_registered") is False and
             s.get("read_scope") in ("full_official_page", "catalog_record_only") and
             s.get("review_state") == "REVIEW_ONLY_NOT_IN_ORIGINAL_CITATIONS", "review source laundered")
    need(sources[2]["read_scope"] == "catalog_record_only", "PDF reading-depth inflated")
    need(m.get("fema_pdf_original_publication") == "2017-07" and
         m.get("fema_pdf_second_page_checked") is False, "FEMA PDF provenance overstated")
    items = m.get("decisions")
    need(type(items) is list and tuple(d.get("id") for d in items if type(d) is dict) == DECISIONS,
         "human-review decision docket incomplete or reordered")
    for d in items:
        need(d.get("state") == "UNADJUDICATED" and d.get("reviewer") is None and
             d.get("evidence") is None and d.get("approved_copy") is None and
             d.get("owner") in ("Preparedness/QD", "Founder/Commerce", "Claude/Engineering"),
             "fabricated human approval or missing owner")
    need(m.get("commercial_funnel", {}).get("paid_sku_authenticated") is False and
         m.get("commercial_funnel", {}).get("grok_published_asset_matched") is False and
         m.get("commercial_funnel", {}).get("realized_net_revenue_verified") is False,
         "unsupported offer, social asset or revenue assertion")


def validate_originals(article: str, a_meta: dict, tool: str, t_meta: dict, m: dict) -> dict:
    validate_manifest(m)
    for slug, number, meta in ((ARTICLE, 15, a_meta), (TOOL, 104, t_meta)):
        need(meta.get("slug") == slug and meta.get("n") == number, "article/tool metadata identity changed")
        need(meta.get("status", {}).get("publish") == "draft" and
             meta.get("safety_review", {}).get("state") == "pending" and
             meta.get("safety_review", {}).get("reviewer") is None and
             meta.get("safety_review", {}).get("date") is None,
             "original review or publication status promoted")
        old_ids = meta.get("source_use")
        need(type(old_ids) is dict and REQUIRED_OLD_IDS <= set(old_ids), "authored source-use IDs missing")
        need(not any(s[0] in old_ids for s in REVIEW_SOURCES), "review-only CDC URL repurposed as authored source")
        need("2025" not in old_ids["shelter-cdc-reunification"], "older CDC citation rebranded as 2025 guidance")
    need("<strong>Keep it on paper, too.</strong>" in article and
         "This is our caution, not an agency's." in article and
         "{{link:family-reunification-card|fold-over wallet card}}" in article,
         "original Article #15 context/attribution missing")
    need("A printed card can be lost" in tool and
         "Do not put a child's full name" in tool and
         "a medical diagnosis or a password on it." in tool and
         "First names or nicknames and phone numbers are usually enough." in tool,
         "Tool #104 blanket privacy warning altered or silently repaired")
    need("minimal version" in tool and "School, childcare and care (left off the minimal version)" in tool,
         "minimal/public-carry vs school-card functional boundary lost")
    need("{{cite:shelter-cdc-reunification}}" in article and
         "{{cite:shelter-cdc-reunification}}" in tool and
         "{{cite:shelter-ready-plan-form}}" in article,
         "original citation or source-use reading scope missing")
    # New source tokens are not accepted into original drafts until a separately
    # approved crosswalk and human review. This is a legacy-content custody test.
    for text in (article, tool):
        need(not any("{{cite:" + s[0] + "}}" in text for s in REVIEW_SOURCES),
             "review-only 2025 CDC reference laundered into original article")
    return {"state": "CHILD_CARD_CONTEXT_AND_CITATION_REVIEW_HARD_HOLD",
            "article": 15, "tool": 104, "originals_checked": 4,
            "review_sources_unregistered": 3, "unadjudicated_decisions": len(DECISIONS),
            "purpose_boundary_open": True, "school_pickup_authority_not_from_card": True,
            "child_privacy_verified": False, "qualified_qd_pass": False,
            "may_publish": False, "wordpress_writes": False,
            "commercial_paid_offer_verified": False}


def native(root: Path) -> dict:
    data = {p: checked_file(root, p, sha) for p, sha in EVIDENCE.items()}
    # R474 manifest is itself immutable once frozen in the PR, while the
    # editorial E466 memo remains independently owned on branch #2789.
    m = strict_json(checked_file(root, "reviews/r474_child_card_scope_manifest.json", MANIFEST_BLOB))
    result = validate_originals(data[f"content/articles/{ARTICLE}.body.html"].decode(),
         strict_json(data[f"content/articles/{ARTICLE}.meta.json"]),
         data[f"content/tools/{TOOL}.body.html"].decode(),
         strict_json(data[f"content/tools/{TOOL}.meta.json"]), m)
    # Separate native 35-article + WordPress/private-export validators are
    # mandatory and have not been evidenced here; this tool cannot clear release.
    result["native_build_and_export_release_clearance"] = False
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ns = p.parse_args(argv)
    try:
        out = native(ns.root)
    except (Hold, ValueError, KeyError, TypeError, OSError, UnicodeError, json.JSONDecodeError) as e:
        out = {"state": "R474_NATIVE_SOURCE_OR_REVIEW_EVIDENCE_MISSING_HARD_HOLD",
               "error": str(e), "may_publish": False,
               "qualified_qd_pass": False, "wordpress_writes": False}
    print(json.dumps(out, sort_keys=True))
    return 2  # Structural evidence or missing evidence: never QD PASS.


if __name__ == "__main__":
    sys.exit(main())
