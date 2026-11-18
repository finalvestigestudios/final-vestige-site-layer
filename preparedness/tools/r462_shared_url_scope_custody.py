#!/usr/bin/env python3
"""R462 read-only shared-URL source-scope custody. Structural evidence, never QD PASS."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

REPO = "finalvestigestudios/final-vestige-site-layer"
CROSSWALK_GIT = "d62e493a67dedd23e04cfdf3cce762ef933c6bf9"
SNAPSHOT_GIT = "056d14cd97d29b843d52912383c237b9122e73ef"
TOTALS = (244, 202, 32)
HOLD = "DRAFT_HARD_HOLD"
REVIEW = "pending-human-source-and-reading-scope-review"

class CrosswalkHold(ValueError):
    """A provenance defect which must not create any publish authorization."""

def require(ok, message):
    if not ok:
        raise CrosswalkHold(message)

def git_blob(blob):
    return hashlib.sha1(b"blob " + str(len(blob)).encode("ascii") + b"\0" + blob).hexdigest()

def no_duplicates(pairs):
    d = {}
    for key, value in pairs:
        require(key not in d, "duplicate JSON property: " + str(key))
        d[key] = value
    return d

def read_pinned(root, path, sha):
    require(isinstance(path, str) and not path.startswith("/") and ".." not in Path(path).parts,
            "unsafe source file path")
    p = root / path
    require(p.is_file() and not p.is_symlink(), "missing or linked file: " + path)
    data = p.read_bytes()
    require(len(data) <= 250000 and git_blob(data) == sha, "source Git blob drift: " + path)
    return json.loads(data, object_pairs_hook=no_duplicates)

def audit(crosswalk, source_rows, snapshot=None, expected=TOTALS):
    """Rebuild URL groups from original row identity, preserving every author scope.

    expected is overridable for unit fixtures only. CLI uses frozen 244/202/32.
    """
    require(isinstance(crosswalk, dict) and crosswalk.get("schema_version") == 1,
            "unreviewed crosswalk schema")
    require(crosswalk.get("status") == "DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED",
            "source crosswalk review state promoted")
    roster = crosswalk.get("source_files")
    require(isinstance(roster, list) and roster, "missing provenance roster")
    require(isinstance(source_rows, dict) and len(roster) == len(source_rows),
            "source roster count mismatch")
    groups_by_url = defaultdict(list)
    all_rows = []
    origins = set()
    for file in roster:
        require(isinstance(file, dict) and set(file) == {"origin", "path", "git_blob_sha", "count"},
                "source roster fields changed")
        origin, path = file["origin"], file["path"]
        require(isinstance(origin, str) and origin not in origins, "origin duplicated")
        origins.add(origin)
        require(isinstance(path, str) and path in source_rows, "source file missing")
        rows = source_rows[path]
        require(isinstance(rows, list) and len(rows) == file["count"], "source rows changed")
        for index, src in enumerate(rows):
            require(isinstance(src, dict) and isinstance(src.get("id"), str)
                    and isinstance(src.get("url"), str) and src["id"] and src["url"],
                    "source identity invalid")
            identity = {"origin": origin, "id": src["id"], "row_index": index}
            variant = {"origin": origin, "source_file": path, "row_index": index, "source": src}
            groups_by_url[src["url"]].append((identity, variant))
            all_rows.append((origin, index, src["id"], src["url"]))
    require(len(set(all_rows)) == len(all_rows), "source row duplicated")
    dupes = {url: rows for url, rows in groups_by_url.items() if len(rows) > 1}
    actual = (len(all_rows), len(groups_by_url), len(dupes))
    require(actual == expected, "source group census drift; fresh review required")
    require((crosswalk.get("raw_source_rows"), crosswalk.get("unique_source_urls"),
             crosswalk.get("duplicate_url_groups")) == expected, "crosswalk census altered")
    groups = crosswalk.get("groups")
    require(isinstance(groups, list) and len(groups) == len(dupes), "URL groups lost/added")
    seen = set()
    results = []
    for group in groups:
        require(isinstance(group, dict), "malformed shared URL group")
        url = group.get("url")
        require(isinstance(url, str) and url in dupes and url not in seen,
                "duplicated or misdirected URL review group")
        seen.add(url)
        require(group.get("canonical_url") == url, "URL silently canonicalized/retargeted")
        require(group.get("review_status") == REVIEW and group.get("reviewer") is None
                and group.get("reviewed_on") is None, "false human source approval")
        actual_pairs = dupes[url]
        identities = group.get("identities")
        variants = group.get("variants")
        require(isinstance(identities, list) and isinstance(variants, list)
                and len(identities) == len(variants) == len(actual_pairs),
                "origin source identity or reading scope dropped")
        serialize = lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"))
        require(sorted(map(serialize, identities)) ==
                sorted(serialize(i) for i, _ in actual_pairs), "source IDs/origin row changed")
        require(sorted(map(serialize, variants)) ==
                sorted(serialize(v) for _, v in actual_pairs), "source scope/metadata changed")
        source_ids = {v["source"]["id"] for v in variants}
        scopes = {v["source"].get("supports") or "" for v in variants}
        dates = {v["source"].get("verified_on") for v in variants}
        results.append({"url": url, "source_rows": len(variants),
                        "different_source_ids": len(source_ids) > 1,
                        "different_reading_scopes": len(scopes) > 1,
                        "missing_reading_scope": "" in scopes,
                        "different_verification_dates": len(dates) > 1,
                        "review_status": "PENDING_HUMAN_REVIEW"})
    require(seen == set(dupes), "shared URL missing from human docket")
    if snapshot is not None:
        require(snapshot.get("repository") == REPO and snapshot.get("qualified_qd_pass") is False
                and snapshot.get("release_state") == HOLD, "original source snapshot not safe")
        candidate = snapshot.get("candidate", {}).get("sources", {})
        for file in roster:
            short = file["path"].removeprefix("preparedness/sources/")
            require(candidate.get(short) == file["git_blob_sha"],
                    "nine-origin Git source pin drift: " + short)
        require(len(snapshot.get("origins", {})) == 9
                and len(snapshot.get("candidate", {}).get("articles", {})) == 35,
                "nine origins or 35 manuscripts incomplete")
    return {"state": "URL_SCOPE_REVIEW_HARD_HOLD", "release_state": HOLD,
            "qualified_qd_pass": False, "source_claim_support_verified": False,
            "may_publish": False, "commercial_offer_verified": False,
            "authored_source_rows": actual[0], "literal_urls": actual[1],
            "shared_url_review_groups": actual[2],
            "different_id_groups": sum(x["different_source_ids"] for x in results),
            "different_scope_groups": sum(x["different_reading_scopes"] for x in results),
            "missing_scope_groups": sum(x["missing_reading_scope"] for x in results),
            "verification_date_discrepancy_groups":
                sum(x["different_verification_dates"] for x in results),
            "groups": sorted(results, key=lambda x: x["url"])}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args(argv)
    try:
        cw = read_pinned(args.root, "sources/crosswalk.json", CROSSWALK_GIT)
        snapshot = read_pinned(args.root, "audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json", SNAPSHOT_GIT)
        rows = {}
        for item in cw["source_files"]:
            path = item["path"]
            require(path.startswith("preparedness/sources/"), "source path outside Preparedness")
            obj = read_pinned(args.root, path.removeprefix("preparedness/"), item["git_blob_sha"])
            rows[path] = obj["sources"]
        print(json.dumps(audit(cw, rows, snapshot), indent=2, sort_keys=True))
    except (OSError, UnicodeError, KeyError, TypeError, ValueError) as e:
        print(json.dumps({"state": "SOURCE_CUSTODY_FAILURE_HARD_HOLD",
                          "qualified_qd_pass": False, "may_publish": False, "error": str(e)}))
    return 2  # success = review-only HARD HOLD; never an editorial/safety PASS

if __name__ == "__main__":
    raise SystemExit(main())
