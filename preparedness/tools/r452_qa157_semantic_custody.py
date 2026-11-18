#!/usr/bin/env python3
"""R452: QA #157 non-test semantic custody against later Preparedness candidates.

READ-ONLY. Exact Git blob pins are custody checks, NOT evidence that any
emergency/medical advice has been approved. No merge, approval or publication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

HOLD = "DRAFT_HARD_HOLD"
PATHS = (
    "preparedness/content/articles/household-emergency-plan.body.html",
    "preparedness/content/articles/three-day-kit.body.html",
    "preparedness/sources/fragments/start.json",
    "preparedness/taxonomy.json",
)
QA157 = ("6407a31a882211e62c00f4e07ec7dc4d5abf99c6",
         "f578cdbae602c1ad58a9237c8dea0fd74c99f7da",
         "d5a5087042381227d840675d9eb08ddc375d21e8",
         "d20ff18bc6f243e08796c0505981979a10fca2d9")
R451 = ("f81cd43516e8295104230412f18776919148f905",
        "933f38ff3cd55a241cf9b392014fc52d4961e84f",
        "96140d6d1872588e5d20d9052445c9157e88934d",
        "15c547bb3018ac182b12a51036389cfa39a59168")
REFS = {"qa157":"7d1ae6b8ef93d10cfb6810987672360885e9c1aa",
        "candidate_r451":"05fdcf58c981967d26c16a30c9bf961b3e0dcdec"}
CRITICAL = {"household-emergency-plan", "three-day-kit",
            "go-bags", "preparedness-real-households"}

class CustodyError(ValueError):
    pass

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def unique_pairs(pairs):
    result = {}
    for key, val in pairs:
        if key in result:
            raise CustodyError("duplicate JSON key: " + key)
        result[key] = val
    return result

def parse_json(data: bytes, label: str):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (ValueError, UnicodeError) as exc:
        raise CustodyError(label + ": invalid JSON: " + str(exc)) from exc

def _index(records, key, label):
    if not isinstance(records, list):
        raise CustodyError(label + ": expected array")
    out = {}
    for entry in records:
        if not isinstance(entry, dict) or not isinstance(entry.get(key), str) or not entry[key]:
            raise CustodyError(label + ": missing identity " + key)
        if entry[key] in out:
            raise CustodyError(label + ": duplicate identity " + entry[key])
        out[entry[key]] = entry
    return out

def _ensure(condition, message):
    if not condition:
        raise CustodyError(message)

def assess(qa: dict[str, bytes], candidate: dict[str, bytes],
           qa_pins=QA157, candidate_pins=R451) -> dict:
    """Fail closed on custody/scope regression; always return an approval HOLD."""
    _ensure(set(qa) == set(PATHS) and set(candidate) == set(PATHS), "four exact source paths required")
    _ensure(len(qa_pins) == len(PATHS) and len(candidate_pins) == len(PATHS), "pin cardinality")
    for i, path in enumerate(PATHS):
        _ensure(isinstance(qa[path], bytes) and isinstance(candidate[path], bytes), "binary bytes required: " + path)
        _ensure(git_blob(qa[path]) == qa_pins[i], "QA157 Git blob mismatch: " + path)
        _ensure(git_blob(candidate[path]) == candidate_pins[i], "candidate Git blob mismatch: " + path)
    household = candidate[PATHS[0]].decode("utf-8").lower()
    _ensure("do not switch off the main breaker" in household,
            "household breaker-drill prohibition absent")
    _ensure("smoke and carbon monoxide alarms" in household and "medical" in household,
            "household safety-critical systems omitted")
    _ensure("switch off the main power for an evening" not in household,
            "unsafe old main-power rehearsal reintroduced")
    medical = candidate[PATHS[1]].decode("utf-8").lower()
    _ensure(all(w in medical for w in ("refrigerated medicine", "pharmacist", "interim-use", "replacement plan")),
            "refrigerated medicine product-specific pharmacist plan missing")
    _ensure("{{cite:start-cdc-pyh-prescriptions}}" in medical,
            "medicine plan citation missing")
    sources_qa = parse_json(qa[PATHS[2]], "QA157 sources")
    sources_now = parse_json(candidate[PATHS[2]], "candidate sources")
    before = _index(sources_qa.get("sources"), "id", "QA157 source")
    after = _index(sources_now.get("sources"), "id", "candidate source")
    _ensure(set(before) <= set(after), "QA157 original source ID removed")
    for source_id, original in before.items():
        current = after[source_id]
        _ensure(current.get("url") == original.get("url"), "source URL reassigned: " + source_id)
        _ensure(current.get("publisher") == original.get("publisher"), "source publisher reassigned: " + source_id)
        _ensure(isinstance(current.get("supports"), str) and current["supports"].strip(),
                "documented reading scope blank: " + source_id)
    redcross = after.get("start-redcross-older-adults", {})
    _ensure(redcross.get("kind") == "nonprofit", "American Red Cross incorrectly recast as regulator")
    taxonomy_qa = parse_json(qa[PATHS[3]], "QA157 taxonomy")
    taxonomy_now = parse_json(candidate[PATHS[3]], "candidate taxonomy")
    slate_qa = _index(taxonomy_qa.get("slate"), "slug", "QA157 slate")
    slate_now = _index(taxonomy_now.get("slate"), "slug", "candidate slate")
    _ensure(len(slate_qa) == len(slate_now) == 35 and set(slate_qa) == set(slate_now),
            "35-article URL identity drift")
    for slug, original in slate_qa.items():
        current = slate_now[slug]
        for field in ("n", "title", "track", "section", "status"):
            _ensure(current.get(field) == original.get(field), "slate identity/status drift: " + slug + "/" + field)
        _ensure(not original.get("gate") or current.get("gate") is True,
                "qualified review gate was weakened: " + slug)
        _ensure(current.get("status") != "published", "publication state advanced: " + slug)
    _ensure(all(slate_now[slug].get("gate") is True for slug in CRITICAL),
            "QA157 Start Here publication gate lost")
    strengthened = sorted(slug for slug in slate_now
                          if slate_now[slug]["gate"] is True and slate_qa[slug].get("gate") is not True)
    return {
        "release_state": HOLD,
        "source_review": "NOT_APPROVED",
        "native_build": "NOT_EXECUTED",
        "qualified_human_review": "NOT_APPROVED",
        "exact_git_blob_pins": {"qa157": dict(zip(PATHS, qa_pins)),
                                "candidate_r451": dict(zip(PATHS, candidate_pins))},
        "article_count": len(slate_now),
        "original_source_ids_retained": len(before),
        "candidate_source_ids": len(after),
        "additional_review_gates_preserved": strengthened,
        "unresolved_comparative_scope_review": ["source supports text changes", "medical/editorial language",
                                                "source disputes/forks", "native private previews"],
        "assurance": "Structural non-regression only; content safety not approved",
    }

def read_root(root: Path):
    return {path: (root / path).read_bytes() for path in PATHS}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = assess(read_root(args.qa_root), read_root(args.candidate_root))
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, UnicodeError, CustodyError) as exc:
        print(json.dumps({"release_state":HOLD,"error":str(exc),"source_review":"NOT_APPROVED"}))
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
