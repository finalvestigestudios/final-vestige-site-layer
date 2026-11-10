#!/usr/bin/env python3
"""R273 offline reviewer docket. Preserves original reading scopes; NEVER release approval."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

HOLD = "DRAFT_HARD_HOLD"
INVALID = "INVALID_HARD_HOLD"
SOURCE_GATE = "tools/r272_crosswalk_snapshot_hold.py"
SOURCE_GATE_BLOB = "97cacd40b2a4324696f746798b472251a42a53b6"
DOCKET_PATH = "audits/r273_shared_source_review_docket_UNAPPROVED.json"
SCHEMA = "fv-r273-source-review-docket-v1"


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_json(raw):
    def no_dupes(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError("duplicate JSON key: " + k)
            out[k] = v
        return out
    return json.loads(raw.decode("utf-8"), object_pairs_hook=no_dupes,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def build_docket(crosswalk, originals):
    """Build comprehensive, unsanctioned review indices; no claims reconciled."""
    paths = {f["origin"]: f["path"] for f in crosswalk["source_files"]}
    all_rows = []
    for origin in sorted(originals):
        for idx, source in enumerate(originals[origin]):
            all_rows.append({"origin": origin, "source_file": paths[origin],
                             "row_index": idx, "source": source})
    by_id = defaultdict(list)
    for entry in all_rows:
        by_id[entry["source"]["id"]].append(entry)
    collisions = [{"source_id": source_id, "review_status": "pending-human-source-and-reading-scope-review",
                   "reviewer": None, "reviewed_on": None, "variants": entries}
                  for source_id, entries in sorted(by_id.items()) if len(entries) > 1]
    groups = []
    for g in sorted(crosswalk["groups"], key=lambda g: g["url"]):
        groups.append({"review_alias": g["url"], "review_status": g["review_status"],
                       "reviewer": None, "reviewed_on": None,
                       "variants": sorted(g["variants"],
                                          key=lambda v: (v["origin"], v["row_index"], v["source"]["id"]))})
    return {
        "schema": SCHEMA, "state": HOLD, "crosswalk_blob": "d62e493a67dedd23e04cfdf3cce762ef933c6bf9",
        "warning": "UNAPPROVED provenance worklist only; matching URLs or IDs do not prove shared claims or safe guidance.",
        "source_rows": len(all_rows), "review_alias_groups": len(groups),
        "duplicate_source_id_groups": len(collisions), "exact_urls": len({v["source"]["url"] for v in all_rows}),
        "shared_url_review": groups, "duplicate_id_review": collisions,
        "article_7_chemical_claims_reviewed": False,
        "article_7_cdc_claims_reviewed": False,
        "article_20_readygov_claim_reviewed": False,
        "independent_qd_pass": False, "medical_safety_verified": False,
        "privacy_approved": False, "merchant_offer_approved": False,
        "publication_authorized": False, "may_merge": False,
    }


def audit(root, read=None):
    """Snapshot-authenticated read-only parity check; strict HOLD never PASS."""
    root = Path(root)
    read = read or (lambda base, name: (base / name).read_bytes())
    output = {"state": INVALID, "independent_qd_pass": False,
              "publication_authorized": False, "errors": []}
    try:
        source_code = read(root, SOURCE_GATE)
        if blob(source_code) != SOURCE_GATE_BLOB:
            raise ValueError("R272 source-gate code identity changed")
        spec = importlib.util.spec_from_file_location("r273_frozen_r272", root / SOURCE_GATE)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        source_check = gate.audit(root, read)
        if (source_check.get("state") != HOLD or source_check.get("source_snapshot_parity") is not True
                or source_check.get("counts") != gate.CENSUS):
            raise ValueError("eight-origin R272 source crosswalk not authenticated HOLD")
        x = read_json(read(root, gate.CROSSWALK))
        originals = {origin: read_json(read(root, path))["sources"]
                     for origin, path, sha, n in gate.ORIGINS}
        expected = build_docket(x, originals)
        observed = read_json(read(root, DOCKET_PATH))
        if observed != expected:
            raise ValueError("R273 review docket omitted, altered, or adjudicated source reading")
        if (expected["source_rows"] != 244 or expected["review_alias_groups"] != 32
                or expected["duplicate_source_id_groups"] != 15 or expected["exact_urls"] != 202):
            raise ValueError("R273 original source provenance census changed")
        output.update({"state": HOLD, "source_readings": 244,
                       "review_alias_groups": 32, "duplicate_source_id_groups": 15,
                       "exact_urls": 202, "docket_parity": True})
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError,
            IndexError, ImportError) as error:
        output["errors"].append(str(error))
    return output


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    args = p.parse_args()
    result = audit(args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(2 if result["state"] == HOLD else 3)
