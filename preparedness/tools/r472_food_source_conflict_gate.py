#!/usr/bin/env python3
"""R472 — read-only food/source-version conflict release quarantine.

Original Article #11 has two actionable wild-game freezing prescriptions. NCHFP
2014 records a procedure, but CDC 2024 says wild-game strains can resist freezing
and USDA FSIS 2025 cautions against relying on home freezing. This script records
original provenance, never selects a safe method and never grants QD approval.
It checks all inherited native gates first, then DENIES release by design.
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
ARTICLE = "safe-jerky-dehydration"
BODY_BLOB = "6fa55c397b161437e016d5d4a6c27da7ce3fa6bd"
META_BLOB = "50b365e8109c14bdb9ce1a9365db88215a678ec5"
PARENT_BLOB = "f4387ec5c0c275ce6ceb21860e1535979a43e390"
NCHFP_2014 = "https://nchfp.uga.edu/how/dry/meat-and-poultry/jerky/"
CDC_2024 = "https://www.cdc.gov/trichinellosis/prevention/index.html"
FSIS_2025 = "https://ask.fsis.usda.gov/article/Does-freezing-destroy-parasites"
CDC_2026 = "https://wwwnc.cdc.gov/eid/article/32/7/26-0062_article"

class SafetyHold(ValueError):
    pass

def require(test: bool, explanation: str) -> None:
    if not test:
        raise SafetyHold(explanation)

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def strict_json(raw: bytes) -> dict:
    def object_hook(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "duplicate metadata key: " + key)
            value[key] = item
        return value
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=object_hook)
    require(isinstance(obj, dict), "metadata must be object")
    return obj

def read_pinned(root: Path, path: str, sha: str) -> bytes:
    root = root.resolve()
    target = root / path
    require(target.is_file() and not target.is_symlink()
            and target.resolve().is_relative_to(root), "missing or linked source: " + path)
    raw = target.read_bytes()
    require(git_blob(raw) == sha, "source Git blob changed: " + path)
    return raw

BLOCK = re.compile(r"<(?:li|tr)\b[^>]*>.*?</(?:li|tr)\s*>", re.I | re.S)
TAGS = re.compile(r"<[^>]*>", re.S)
TEMP = re.compile(r"(?<!\w)[-+]?\d+(?:\.\d+)?\s*[°º]\s*[Ff](?!\w)")
DURATION = re.compile(r"\b\d+\s*(?:days?|weeks?|months?)\b", re.I)
FREEZE = re.compile(r"\bfreez(?:e|es|ing|er|ers)\b", re.I)
TARGET = re.compile(r"\b(?:wild\s+game|trichinell\w*|wild\s+boar|bear\s+meat)\b", re.I)
SOURCE = re.compile(r"\{\{cite:([a-z0-9][a-z0-9-]*)\}\}")

def evidence_sites(body: str) -> list[dict]:
    """Docket only: a match is not a medical determination or approved rewrite."""
    require(isinstance(body, str), "article body must be UTF-8 text")
    matches = []
    for number, chunk in enumerate(BLOCK.findall(body), 1):
        rendered = html.unescape(TAGS.sub(" ", chunk))
        rendered = " ".join(rendered.split())
        if not (TARGET.search(rendered) and FREEZE.search(rendered)
                and TEMP.search(rendered) and DURATION.search(rendered)):
            continue
        sources = sorted(set(SOURCE.findall(chunk)))
        matches.append({
            "block_index": number,
            "sha256": hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
            "source_ids": sources,
            "claim_kind": "numeric_freezing_prescription_with_wild_game_or_trichinella",
            "needs_qualified_human_review": True,
        })
    return matches

def audit(body: str, metadata: dict, *, expected_sites: int = 2) -> dict:
    """Independently enforce original evidence, pending safety state and both holds."""
    require(metadata.get("slug") == ARTICLE and metadata.get("n") == 11,
            "wrong Article #11 identity")
    require(metadata.get("status", {}).get("publish") == "draft",
            "Article #11 publication state is not draft")
    sr = metadata.get("safety_review", {})
    require(sr.get("state") == "pending" and sr.get("reviewer") is None
            and sr.get("date") is None, "unverified food safety or QD approval")
    source_use = metadata.get("source_use")
    require(isinstance(source_use, dict)
            and "nchfp-jerky" in source_use
            and "Trichinella" in source_use["nchfp-jerky"]
            and "wild game" in source_use["nchfp-jerky"],
            "original NCHFP reading-scope record lost")
    sites = evidence_sites(body)
    require(len(sites) == expected_sites,
            f"claim-site inventory drift: expected {expected_sites}, found {len(sites)}")
    require(all("nchfp-jerky" in s["source_ids"] for s in sites),
            "prescription lost its authored source citation")
    return {
        "state": "P0_FOOD_SOURCE_VERSION_CONFLICT_HARD_HOLD",
        "release_state": HOLD, "article": ARTICLE,
        "flagged_original_claim_sites": len(sites), "sites": sites,
        "source_version_question": "NCHFP 2014 instructions are not CDC/USDA approval of household freezing for every wild-game Trichinella strain",
        "source_urls": [NCHFP_2014, CDC_2024, FSIS_2025, CDC_2026],
        "human_adjudication_required": True,
        "qualified_qd_pass": False, "medical_or_food_safety_verified": False,
        "may_publish": False, "wordpress_writes": False,
    }

def native(root: Path) -> dict:
    root = root.resolve()
    # Source identities have to be checked before any imported repository module.
    b = read_pinned(root, "content/articles/" + ARTICLE + ".body.html", BODY_BLOB)
    m = read_pinned(root, "content/articles/" + ARTICLE + ".meta.json", META_BLOB)
    result = audit(b.decode("utf-8"), strict_json(m))
    parent_rel = "tools/r471_wordpress_export_custody.py"
    read_pinned(root, parent_rel, PARENT_BLOB)
    spec = importlib.util.spec_from_file_location("r472_readonly_parent", root / parent_rel)
    require(spec is not None and spec.loader is not None, "pinned parent not importable")
    parent = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = parent
    spec.loader.exec_module(parent)
    # All original source/citation/CSS/35-article/export gates must run as well.
    prior = parent.native(root)
    require(prior.get("articles_checked") == 35 and prior.get("may_publish") is False,
            "inherited 35-article custody cannot be established")
    result["inherited_native_export_bytes_matched"] = True
    return result

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    opts = parser.parse_args(argv)
    try:
        result = native(opts.root)
    except (SafetyHold, OSError, UnicodeError, json.JSONDecodeError,
            ValueError, KeyError, TypeError, ImportError, AssertionError) as exc:
        result = {"state": "P0_FOOD_CUSTODY_UNEXECUTED_OR_DRIFT_HARD_HOLD",
                  "release_state": HOLD, "error": str(exc),
                  "qualified_qd_pass": False, "may_publish": False,
                  "wordpress_writes": False}
    print(json.dumps(result, sort_keys=True))
    return 2  # Never a publication approval; even valid original claims need review.

if __name__ == "__main__":
    sys.exit(main())
