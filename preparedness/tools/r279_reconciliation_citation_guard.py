#!/usr/bin/env python3
"""Fail-closed R200→R275→R277 source-provenance/reading-depth custody.

This checks immutable evidence structure, NOT medical accuracy, editorial adequacy,
accessibility, real-world emergency safety, or approval for publication.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

HOLD = "DRAFT_HARD_HOLD"
INVALID = "INVALID_HARD_HOLD"
ORIGINAL = "audits/r200_seven_cluster_35_article_frozen_custody.json"
INTEGRATED = "audits/r276_all_slate_identity_UNAPPROVED.json"
RECONCILED = "audits/r277_source_baseline_reconciliation_UNAPPROVED.json"
DEPTH = "audits/r277_integrated_body_depth_witness_UNAPPROVED.json"
PINS = {
    ORIGINAL: "5822f9dfde21d1f3bdfc26658769d852c639438c",
    INTEGRATED: "b8c7c6df0dca62b04b01abc5671b7083ad9cb61e",
    RECONCILED: "2b9656c2fac9679041aaa45e35f2e88bc9f414e1",
    DEPTH: "70b5b6c097f7b714061b825412777f746ee628f8",
}
FLAGS = ("may_merge", "publication_authorized", "independent_qd_pass",
         "medical_safety_verified", "privacy_approved")
CLUSTERS = ("start", "shelter", "food", "health", "hist-field", "hist-food", "hist-home")
SHA = re.compile(r"^[0-9a-f]{40}$")


def git_blob(raw: bytes) -> str:
    if type(raw) is not bytes:
        raise ValueError("Git identity requires bytes")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def strict_json(raw: bytes):
    def unique(pairs):
        out = {}
        for key, val in pairs:
            if key in out:
                raise ValueError("duplicate JSON key " + key)
            out[key] = val
        return out
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON")))


def require(condition: bool, reason: str):
    if not condition:
        raise ValueError(reason)


def held(flags: dict, required=FLAGS):
    require(isinstance(flags, dict) and all(flags.get(key, "MISSING") is False for key in required),
            "approval flag drift or missing gate")


def inspect(original: dict, integrated: dict, recon: dict, depth: dict):
    """Cross-check four read-only records; caller must verify their Git blobs."""
    require(original.get("schema") == "fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1", "R200 schema")
    require(integrated.get("schema") == "fv-r276-all-slate-identity-v1", "integrated schema")
    require(recon.get("schema") == "fv-r277-source-baseline-erratum-v1", "R277 reconciliation schema")
    require(depth.get("schema") == "fv-r277-source-depth-structure-unapproved-v1", "R277 depth schema")
    require(all(x.get("state") == HOLD for x in (original, integrated, recon, depth)), "hard hold drift")
    for row in (original, integrated, recon, depth):
        held(row.get("release", row), ("publication_authorized", "independent_qd_pass", "medical_safety_verified"))
    for row in (integrated, recon, depth):
        held(row.get("release", row))
    require(integrated.get("snapshot_ref") == "df96120007ceb33290764392a5900e356e04deac", "integrated snapshot ref")
    require(original.get("artifact_count") == 35 and original.get("export_target_count_with_six_tools") == 41, "original article/tools census")
    orig = original.get("articles")
    require(isinstance(orig, list) and len(orig) == 35, "original 35 articles missing")
    require({a.get("n") for a in orig} == set(range(1, 36)), "article numbers missing or repeated")
    slugs = [a.get("slug") for a in orig]
    routes = [a.get("route") for a in orig]
    require(len(set(slugs)) == len(set(routes)) == 35, "duplicate slug or URL")
    require(all(isinstance(route, str) and route.startswith("/preparedness/") and route.endswith("/") for route in routes), "noncanonical route")
    require(set(original.get("branch_heads", {})) == set(CLUSTERS), "frozen contributor roster")
    heads = original["branch_heads"]
    require(all(isinstance(v, str) and SHA.fullmatch(v) for v in heads.values()), "frozen head SHA")
    for a in orig:
        require(a.get("source_cluster") in heads and a.get("branch_sha") == heads[a["source_cluster"]], "article provenance mismatch")
        require(all(isinstance(a.get(k), str) and SHA.fullmatch(a[k]) for k in ("body_oid", "meta_oid")), "original article SHA invalid")
    entries = integrated.get("entries")
    require(isinstance(entries, list) and len(entries) == 96, "integrated 96-file custody incomplete")
    path_entries = {e["path"]: e for e in entries}
    require(len(path_entries) == 96, "duplicate integrated paths")
    require(all(isinstance(e.get("sha"), str) and SHA.fullmatch(e["sha"]) and type(e.get("size")) is int and e["size"] > 0 for e in entries), "integrated byte/OID invalid")
    require(Counter(e["role"] for e in entries)["article_body"] == 35 and Counter(e["role"] for e in entries)["article_meta"] == 35, "integrated article corpus incomplete")
    require(integrated.get("source_review") == {"shared_url_groups": 32, "duplicate_id_groups": 15, "held_occurrences": 3}, "integrated source holds altered")
    require(recon.get("source_review") == {"unadjudicated_shared_url_groups": 32, "unadjudicated_duplicate_id_groups": 15, "held_cdc_ready_gov_occurrences": 3}, "R277 citation holds altered")
    require(recon.get("source_refs", {}).get("r200_manifest_blob") == PINS[ORIGINAL] and recon["source_refs"].get("r276_integrated_manifest_blob") == PINS[INTEGRATED], "incorrect provenance pins")
    require(depth.get("r200_manifest_blob") == PINS[ORIGINAL] and depth.get("integrated_manifest_blob") == PINS[INTEGRATED], "incorrect depth pins")
    branches = recon.get("branch_heads")
    require(isinstance(branches, list) and len(branches) == 7, "seven current branch snapshots required")
    require(Counter(row.get("origin") for row in branches) == Counter(CLUSTERS), "duplicate/missing contributor")
    for b in branches:
        require(b.get("head_sha_at_check") == b.get("r200_frozen_sha") == heads[b["origin"]]
                and b.get("compare_status") == "identical" and b.get("ahead") == b.get("behind") == 0,
                "current contributor claimed drift or unsupported approval")
    require(recon.get("comparison_census") == {"r200_current_matches": 7,
            "r276_older_crosswalk_matches": 2, "older_provenance_differences": 5,
            "unreviewed_new_branch_changes_identified": 0}, "historical-vs-current baseline confused")
    snap = recon.get("article_snapshot", {})
    require({k: snap.get(k) for k in ("r200_articles", "r275_integrated_articles", "baseline_different_articles", "body_blob_differences", "meta_blob_differences", "route_duplicate_count")} ==
            {"r200_articles": 35, "r275_integrated_articles": 35, "baseline_different_articles": 17, "body_blob_differences": 14, "meta_blob_differences": 12, "route_duplicate_count": 0}, "historical article discrepancy census")
    differences = snap.get("differences")
    require(isinstance(differences, list) and len(differences) == 17, "missing discrepancy entries")
    mapped = {row["n"]: row for row in differences}
    require(len(mapped) == 17, "duplicate discrepancy entries")
    original_by_n = {a["n"]: a for a in orig}
    expected = {}
    for n, a in original_by_n.items():
        paths = {part: path_entries.get(f"content/articles/{a['slug']}.{suffix}") for part, suffix in (("body", "body.html"), ("meta", "meta.json"))}
        require(all(paths.values()) and paths["body"]["role"] == "article_body" and paths["meta"]["role"] == "article_meta", "lost integrated manuscript")
        body_changed = paths["body"]["sha"] != a["body_oid"]
        meta_changed = paths["meta"]["sha"] != a["meta_oid"]
        if body_changed or meta_changed:
            expected[n] = (body_changed, meta_changed)
            row = mapped.get(n)
            require(isinstance(row, dict) and row.get("n") == n and row.get("slug") == a["slug"] and row.get("source_cluster") == a["source_cluster"] and row.get("route") == a["route"], "missing or misplaced historic source row")
            for key, value in (("r200_body_blob", a["body_oid"]), ("r200_meta_blob", a["meta_oid"]), ("r275_body_blob", paths["body"]["sha"]), ("r275_meta_blob", paths["meta"]["sha"]), ("body_diff", body_changed), ("meta_diff", meta_changed)):
                require(row.get(key) == value, "historical source OID/flag altered " + key)
    require(set(mapped) == set(expected) and len(expected) == 17 and sum(v[0] for v in expected.values()) == 14 and sum(v[1] for v in expected.values()) == 12, "unreported integrated differences")
    witness = depth.get("rows")
    require(isinstance(witness, list) and len(witness) == 14, "all 14 changed bodies require depth review")
    witness_map = {r["n"]: r for r in witness}
    require(len(witness_map) == 14 and set(witness_map) == {n for n,v in expected.items() if v[0]}, "depth witness not aligned to body changes")
    shorter = []
    for n, row in witness_map.items():
        a = original_by_n[n]
        path = path_entries[f"content/articles/{a['slug']}.body.html"]
        require(row.get("slug") == a["slug"] and row.get("r200_blob") == a["body_oid"] and row.get("r275_blob") == path["sha"], "depth source identity mismatch")
        require(type(row.get("body_bytes_old")) is int and row["body_bytes_old"] == a["body_bytes"] and type(row.get("body_bytes_integrated")) is int and row["body_bytes_integrated"] == path["size"], "depth byte lengths mismatch")
        require(type(row.get("body_byte_delta")) is int and row["body_byte_delta"] == row["body_bytes_integrated"] - row["body_bytes_old"], "misreported byte delta")
        if row["body_byte_delta"] < 0: shorter.append(n)
        for old, new in (("word_count_old", "word_count_integrated"), ("heading_count_old", "heading_count_integrated"), ("citation_occurrences_old", "citation_occurrences_integrated")):
            require(type(row.get(old)) is int and type(row.get(new)) is int and 0 <= row[old] <= row[new], "structural/citation loss requires human review")
        require(row.get("lost_citation_ids") == [] and isinstance(row.get("introduced_citation_ids"), list) and row.get("structural_reading_depth_never_decreased") is True, "citation scope or depth claim altered")
    require(sorted(shorter) == [24,25,27,32,33,34] and depth.get("body_html_shorter_article_numbers") == sorted(shorter), "six shorter bodies not properly flagged")
    require({k: depth.get(k) for k in ("article_html_changed", "body_html_shorter_in_bytes", "word_counts_lower", "heading_counts_lower", "citation_occurrence_counts_lower", "removed_citation_id_sets")} == {"article_html_changed":14, "body_html_shorter_in_bytes":6, "word_counts_lower":0, "heading_counts_lower":0, "citation_occurrence_counts_lower":0, "removed_citation_id_sets":0}, "unsubstantiated depth totals")
    return {"state": HOLD, "source_parity_mechanical_only": True, "article_count":35,
            "changed_articles":17, "changed_bodies":14, "changed_metadata":12,
            "requires_human_source_review": True, "publication_authorized":False,
            "independent_qd_pass":False}



# R279 correction to immutable R277 witness. R277 accurately preserves citation
# occurrence totals, but its zero-loss ID claim is FALSE in Articles 24 and 25.
# This read-only gate extracts raw IDs again from frozen Git blobs. Zero changed
# occurrence totals never imply preservation of source identities.
CITE_ID = re.compile(r"\{\{cite:([a-zA-Z0-9][a-zA-Z0-9._:-]*)\}\}")
CITE_OPEN = re.compile(r"\{\{cite:")
REMAPPED_JERKY = {24: 1, 25: 7}
HIST_FOOD_ORIGINAL = "67e116e536c7410bed30f8f3b1bb8c166f3c223d"
HIST_FOOD_ORIGINAL_SOURCE_BLOB = "c1856c998c6c728f0de72221e5654a238df994a9"
HIST_FOOD_INTEGRATED_SOURCE_BLOB = "d10628342fea5f177a8d1be00dd906d0c9c7850e"


def raw_cites(raw: bytes):
    found = CITE_ID.findall(raw.decode("utf-8", errors="strict"))
    require(len(found) == len(CITE_OPEN.findall(raw.decode("utf-8"))),
            "malformed or hidden citation token")
    return Counter(found)


def check_raw_ids(n: int, before: bytes, after: bytes, witness: dict):
    """Verify 1:1 raw citation identity on actual source bytes, never by URL alias."""
    require(git_blob(before) == witness["r200_blob"], "wrong original body Git blob")
    require(git_blob(after) == witness["r275_blob"], "wrong integrated body Git blob")
    old, new = raw_cites(before), raw_cites(after)
    require(sum(old.values()) == witness["citation_occurrences_old"] and
            sum(new.values()) == witness["citation_occurrences_integrated"],
            "citation occurrence count mismatch")
    removed = sorted(set(old) - set(new))
    introduced = sorted(set(new) - set(old))
    if n in REMAPPED_JERKY:
        k = REMAPPED_JERKY[n]
        require(removed == ["nchfp-jerky"] and introduced == ["hist-food-nchfp-jerky"]
                and old["nchfp-jerky"] == k and new["hist-food-nchfp-jerky"] == k,
                "Article 24/25 raw source-ID replacement differs from held evidence")
        require(old["hist-food-nchfp-jerky"] == 0 and new["nchfp-jerky"] == 0,
                "retained old ID / newly introduced ID mismatch")
        require(all(new[source_id] >= uses for source_id, uses in old.items()
                    if source_id != "nchfp-jerky"),
                "other cited source lost occurrences during purported rekey")
        require(witness.get("lost_citation_ids") == [] and
                witness.get("introduced_citation_ids") == [],
                "R277 historical false zero-loss witness modified; create new erratum")
        return {"n": n, "raw_removed_ids": removed, "raw_introduced_ids": introduced,
                "replaced_occurrences": k, "independent_equivalence_approved": False}
    require(removed == [] and introduced == witness.get("introduced_citation_ids")
            and witness.get("lost_citation_ids") == [],
            "unrecognized raw source-ID replacement or loss")
    decreased = {key: [count, new[key]] for key, count in old.items() if new[key] < count}
    # Three retained source IDs each lose one occurrence in the authentic Article 13
    # revision. These are held evidence changes, not permission to discard citations.
    known_article13 = {"usfa-fire-escape": [11,10],
                       "shelter-nfpa-escape": [21,20],
                       "shelter-usfa-high-rise": [3,2]}
    require(decreased == (known_article13 if n == 13 else {}),
            "unreviewed occurrence reduction of a retained citation ID")
    return {"n": n, "raw_removed_ids": [], "raw_introduced_ids": introduced,
            "replaced_occurrences": 0, "retained_id_occurrence_decreases_held": decreased,
            "independent_equivalence_approved": False}


def git_show(repo: Path, ref: str, path: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), "show", ref + ":" + path],
                            capture_output=True, timeout=15, check=False)
    require(result.returncode == 0, "unavailable frozen Git object: " + ref + ":" + path)
    return result.stdout


def check_original_fragment(repo: Path, integrated_ref: str):
    path = "preparedness/sources/fragments/hist-food.json"
    a = git_show(repo, HIST_FOOD_ORIGINAL, path)
    b = git_show(repo, integrated_ref, path)
    require(git_blob(a) == HIST_FOOD_ORIGINAL_SOURCE_BLOB and
            git_blob(b) == HIST_FOOD_INTEGRATED_SOURCE_BLOB,
            "NCHFP source fragment provenance differs from original evidence")
    old, new = strict_json(a)["sources"], strict_json(b)["sources"]
    original = next((x for x in old if x.get("id") == "nchfp-jerky"), None)
    updated = next((x for x in new if x.get("id") == "hist-food-nchfp-jerky"), None)
    require(isinstance(original, dict) and isinstance(updated, dict),
            "source record missing from frozen source fragment")
    require(original["title"] == updated["title"] and
            original["supports"] == updated["supports"] and
            original["url"].rstrip("/") == updated["url"].rstrip("/"),
            "source equivalence candidate requires fresh human review")
    return {"same_title_and_supports": True, "url_review_alias_only": True,
            "different_raw_id": True, "independent_equivalence_approved": False}


def audit(root: Path, repo: Path | None = None):
    root = Path(root)
    result = {"state": INVALID, "source_parity_mechanical_only": False,
              "publication_authorized": False, "independent_qd_pass": False, "errors": []}
    try:
        contents = {}
        for name, sha in PINS.items():
            raw = (root / name).read_bytes()
            require(git_blob(raw) == sha, "source witness Git blob mismatch: " + name)
            contents[name] = strict_json(raw)
        result.update(inspect(*(contents[k] for k in (ORIGINAL, INTEGRATED, RECONCILED, DEPTH))))
        require(repo is not None, "frozen native Git objects unavailable; full R279 gate NOT RUN")
        original, integrated, recon, depth = (contents[k] for k in
                                                (ORIGINAL, INTEGRATED, RECONCILED, DEPTH))
        by_n = {x["n"]: x for x in original["articles"]}
        verified = []
        for witness in depth["rows"]:
            n = witness["n"]
            record = by_n[n]
            path = "preparedness/content/articles/" + record["slug"] + ".body.html"
            verified.append(check_raw_ids(n,
                git_show(repo, record["branch_sha"], path),
                git_show(repo, integrated["snapshot_ref"], path), witness))
        require(len(verified) == 14 and sum(x["replaced_occurrences"] for x in verified) == 8,
                "unaccounted historical citation-ID substitutions")
        result["r279_raw_citation_scan"] = verified
        result["r279_source_fragment"] = check_original_fragment(repo, integrated["snapshot_ref"])
        result["historical_r277_zero_loss_claim_corrected"] = True
        result["independent_equivalence_approved"] = False
        result["git_blobs_rechecked"] = 30
    except (OSError, TypeError, ValueError, KeyError, AttributeError, UnicodeError, subprocess.TimeoutExpired) as exc:
        result["errors"].append(str(exc))
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="preparedness/ directory")
    parser.add_argument("--repo", type=Path, required=True, help="local full Git repo with all frozen objects")
    args = parser.parse_args()
    report = audit(args.root, args.repo)
    print(json.dumps(report, sort_keys=True, indent=2))
    raise SystemExit(2 if report["state"] == HOLD else 3)
