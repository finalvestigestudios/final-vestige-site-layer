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


