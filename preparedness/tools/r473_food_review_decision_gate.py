#!/usr/bin/env python3
"""R473 — fail-closed source-version and 12-surface food-review decision custody.

The original article and reviewer material are NOT rewritten by this tool. It
recognizes the 2011/2014 UGA discrepancy and later CDC/USDA species cautions,
requires each of 12 independently flagged exposures to remain pending, and
chains into the existing R472 source/35-article/export hold. Never QD PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

HOLD = "DRAFT_HARD_HOLD"
BASE = "preparedness"
ARTICLE = "safe-jerky-dehydration"
BODY_BLOB = "6fa55c397b161437e016d5d4a6c27da7ce3fa6bd"
META_BLOB = "50b365e8109c14bdb9ce1a9365db88215a678ec5"
MANIFEST_BLOB = "be3bf4504ef8e81f157620244985f32dc3539c63"
PARENT_BLOB = "d43b0bf847ed83e0b1cf340bf2057e25f8ca3802"
EDITORIAL_E463 = "5076f3b364a5871b9a347a5837cddc81ee00febf"
EDITORIAL_E464 = "ba97ab12e377e79e6e74cebc92f79382e6512a62"
EDITORIAL_HEAD = "2a4a68a644c5ea89ae8a2dd31c988364eb984c58"
EXPECTED_IDS = (
    "freezer_lead", "freezer_table", "heat_action", "method_table",
    "method_preference", "equipment_procedure", "eight_step_recipe",
    "shelf_life", "storage_preference", "vacuum_safety",
    "commercial_shelf", "universal_verified",
)
VERSION_SCOPE = {
    "uga_2011": ("2011-03", "pork_and_wild_game_grouped",
                 "https://nchfp.uga.edu/papers/UGA_Publications/prep_safe_jerky.pdf"),
    "nchfp_2014": ("2014", "pork_and_wild_game_grouped",
                   "https://nchfp.uga.edu/how/dry/meat-and-poultry/jerky/"),
    "cdc_2024": ("2024-03-12", "pork_example_wild_game_freeze_resistance",
                 "https://www.cdc.gov/trichinellosis/prevention/index.html"),
    "fsis_2025": ("2025-02-03", "home_freezing_not_reliable_for_trichina",
                  "https://ask.fsis.usda.gov/article/Does-freezing-destroy-parasites"),
    "cdc_mmwr_2024": ("2024-05-23", "bear_meat_outbreak_not_jerky_case",
                      "https://www.cdc.gov/mmwr/volumes/73/wr/mm7320a2.htm"),
    "cdc_eid_2026": ("2026-06-24", "unfrozen_jerky_case_not_home_freezer_test",
                     "https://wwwnc.cdc.gov/eid/article/32/7/26-0062_article"),
}
# Exact phrases are original manuscript identification witnesses, NOT replacement advice.
# The two executable freezer claims are checked separately by the pinned R472 gate.
ANCHORS = {
    "heat_action": "Heat the meat to a safe internal temperature, and prove it with a thermometer",
    "method_table": "Three published approaches (as published",
    "method_preference": "FSIS sequence is the more conservative",
    "equipment_procedure": "Most dehydrator instructions do not include the heating step",
    "eight_step_recipe": "Contamination controls, in order",
    "shelf_life": "How long home-dried jerky keeps",
    "storage_preference": "We would follow the shortest figure",
    "vacuum_safety": 'vacuum packaging "also a good option"',
    "commercial_shelf": "Commercially made jerky is made under federal inspection",
    "universal_verified": "Every instruction and figure here comes from the USDA",
}

class ReleaseHold(ValueError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseHold(message)

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def strict_json(raw: bytes) -> dict:
    def unique(pairs):
        d = {}
        for k, v in pairs:
            require(k not in d, "duplicate JSON property: " + k)
            d[k] = v
        return d
    d = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    require(type(d) is dict, "top-level must be object")
    return d

def pinned(root: Path, relative: str, sha: str) -> bytes:
    root = root.resolve()
    p = root / relative
    require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root),
            "missing or linked repository evidence: " + relative)
    b = p.read_bytes()
    require(blob_sha(b) == sha, "Git blob differs: " + relative)
    return b

def validate_manifest(manifest: dict) -> None:
    require(manifest.get("schema") == "fv-preparedness-r473-food-exposure-review-v1",
            "review schema drift")
    require(manifest.get("article_number") == 11 and
            manifest.get("article_slug") == ARTICLE and
            manifest.get("required_exposure_count") == 12, "article or docket identity drift")
    require(manifest.get("original_body_blob") == BODY_BLOB and
            manifest.get("original_metadata_blob") == META_BLOB and
            manifest.get("e463_original_redline_blob") == EDITORIAL_E463 and
            manifest.get("e464_source_lineage_blob") == EDITORIAL_E464 and
            manifest.get("e464_editorial_head") == EDITORIAL_HEAD,
            "editorial witness provenance drift")
    require(manifest.get("release") == HOLD and
            manifest.get("source_version_conflict_open") is True and
            manifest.get("qualified_qd_pass") is False and
            manifest.get("medical_or_food_safety_verified") is False and
            manifest.get("may_publish") is False, "fabricated safety or release clearance")
    versions = manifest.get("source_versions")
    require(type(versions) is list and len(versions) == len(VERSION_SCOPE),
            "source lineage inventory drift")
    seen = set()
    for s in versions:
        require(type(s) is dict and type(s.get("id")) is str, "source version record malformed")
        sid = s["id"]
        require(sid in VERSION_SCOPE and sid not in seen, "duplicate/unauthorized version")
        seen.add(sid)
        pub, scope, url = VERSION_SCOPE[sid]
        require(s.get("published") == pub and s.get("species_scope") == scope and
                s.get("url") == url and s.get("review_state") == "conflict_open",
                "source chronology/species scope or URL changed: " + sid)
        require(s.get("type") in ("historical_not_universal_instruction",
               "public_health_scope_caution", "case_evidence_not_universal_schedule"),
               "source incorrectly promoted to safety instruction")
    require(seen == set(VERSION_SCOPE), "missing source-version witness")
    entries = manifest.get("exposures")
    require(type(entries) is list and len(entries) == 12, "required 12 exposure entries missing")
    require(tuple(e.get("id") for e in entries if type(e) is dict) == EXPECTED_IDS,
            "original exposure order or identity changed")
    for e in entries:
        require(e.get("review_state") == "UNADJUDICATED" and
                e.get("qualified_reviewer") is None and
                e.get("review_date") is None and
                e.get("approved_replacement") is None and
                e.get("decision_evidence") is None,
                "fabricated or unreviewed approval: " + e["id"])
        require(e.get("priority") in ("P0", "P1") and
                e.get("authored_source_id") and e.get("review_question") and
                e.get("locator"), "lost claim provenance: " + e["id"])

def visible_text(body: str) -> str:
    # This extraction is a locating aid only; R469/R470 handle hidden markup/CSS.
    no_tags = re.sub(r"<[^>]*>", " ", body, flags=re.S)
    return " ".join(html.unescape(no_tags).split())

def audit(body: str, meta: dict, manifest: dict, *, r472_result: dict) -> dict:
    validate_manifest(manifest)
    require(meta.get("n") == 11 and meta.get("slug") == ARTICLE,
            "metadata article identity changed")
    require(meta.get("status", {}).get("publish") == "draft" and
            meta.get("safety_review", {}).get("state") == "pending" and
            meta.get("safety_review", {}).get("reviewer") is None and
            meta.get("safety_review", {}).get("date") is None,
            "original food review was improperly promoted")
    require(type(meta.get("source_use")) is dict and
            "nchfp-jerky" in meta["source_use"],
            "authored NCHFP source-use evidence absent")
    require(type(r472_result) is dict and
            r472_result.get("flagged_original_claim_sites") == 2 and
            r472_result.get("state") == "P0_FOOD_SOURCE_VERSION_CONFLICT_HARD_HOLD" and
            r472_result.get("may_publish") is False and
            len(r472_result.get("sites", [])) == 2 and
            all("nchfp-jerky" in site.get("source_ids", []) for site in r472_result["sites"]),
            "two original wild-game numeric claims not independently quarantined")
    rendered = visible_text(body)
    for id, anchor in ANCHORS.items():
        require(anchor.casefold() in rendered.casefold(),
                "original E463 exposure missing or obscured: " + id)
    return {
        "state": "ORIGINAL_12_FOOD_EXPOSURES_AND_VERSION_SCOPES_HARD_HOLD",
        "release_state": HOLD, "original_article": ARTICLE,
        "original_claim_exposures": 12, "wild_game_numeric_sites": 2,
        "other_claim_review_surfaces": 10, "source_version_witnesses": len(VERSION_SCOPE),
        "historic_version_discrepancy": True,
        "wild_game_and_pork_not_interchangeable": True,
        "qualified_human_review_required": True, "qualified_qd_pass": False,
        "medical_or_food_safety_verified": False, "may_publish": False,
        "wordpress_writes": False,
    }

def load_parent(root: Path):
    rel = "tools/r472_food_source_conflict_gate.py"
    pinned(root, rel, PARENT_BLOB)
    name = "r473_pinned_r472_source_hold"
    spec = importlib.util.spec_from_file_location(name, root / rel)
    require(spec is not None and spec.loader is not None, "R472 parent missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def native(root: Path) -> dict:
    root = root.resolve()
    body = pinned(root, "content/articles/"+ARTICLE+".body.html", BODY_BLOB)
    meta = strict_json(pinned(root, "content/articles/"+ARTICLE+".meta.json", META_BLOB))
    manifest = strict_json(pinned(root, "reviews/r473_food_exposure_manifest.json", MANIFEST_BLOB))
    parent = load_parent(root)
    before = parent.audit(body.decode("utf-8"), meta)
    result = audit(body.decode("utf-8"), meta, manifest, r472_result=before)
    inherited = parent.native(root)  # Original 35-article and WP-export custody.
    require(inherited.get("may_publish") is False and
            inherited.get("flagged_original_claim_sites") == 2 and
            inherited.get("inherited_native_export_bytes_matched") is True,
            "R472 original WP/preview and all-source custody did not complete")
    result["inherited_native_export_bytes_matched"] = True
    return result

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ns = p.parse_args(argv)
    try:
        result = native(ns.root)
    except (ReleaseHold, OSError, UnicodeError, json.JSONDecodeError,
            ValueError, ImportError, KeyError, TypeError, AssertionError) as exc:
        result = {"state":"R473_SOURCE_OR_BUILD_CUSTODY_MISSING_HARD_HOLD",
                  "error":str(exc),"release_state":HOLD,
                  "may_publish":False,"qualified_qd_pass":False,
                  "wordpress_writes":False}
    print(json.dumps(result, sort_keys=True))
    return 2  # A successful structural audit NEVER authorizes publishing.

if __name__ == "__main__":
    sys.exit(main())
