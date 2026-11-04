#!/usr/bin/env python3
"""R118: deterministic, private Preparedness 35-article reviewer crosswalk.

Inputs are R117 immutable Git-object catalogs; output NEVER approves advice, safety,
merging, publishing, a purchasable product, or QD. No CMS/network operations.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

HEX = re.compile(r"[0-9a-f]{40}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
OLD_SCHEMA = "fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1"
ORDER_SCHEMA = "fv-preparedness-r117-reviewer-source-and-author-diff-workorders-HOLD-v1"
NEW_SCHEMA = "fv-preparedness-r118-article-author-source-review-crosswalk-HOLD-v1"
SOURCE_PREFIX = "preparedness/sources/fragments/"
ARTICLE_PREFIX = "preparedness/content/articles/"
CLUSTERS = frozenset(("food", "health", "historical-field", "historical-food",
                      "historical-home", "shelter", "start-here"))

class Hold(ValueError):
    pass

def need(condition, reason):
    if not condition:
        raise Hold(reason)

def text_digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True).encode("utf-8")).hexdigest()

def json_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Hold("DUPLICATE_JSON_KEY")
        result[key] = value
    return result

def strict_load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=json_no_duplicates)

def check_oid(oid):
    need(type(oid) is str and HEX.fullmatch(oid), "INVALID_GIT_OID")

def check_articles(mapping):
    need(type(mapping) is dict, "INVALID_ARTICLE_CATALOG")
    bodies, metas = {}, {}
    for filename, oid in mapping.items():
        check_oid(oid)
        if filename.endswith(".body.html"):
            stem = filename[:-10]
            need(SLUG.fullmatch(stem), "UNSAFE_ARTICLE_ROUTE")
            bodies[stem] = oid
        elif filename.endswith(".meta.json"):
            stem = filename[:-10]
            need(SLUG.fullmatch(stem), "UNSAFE_ARTICLE_ROUTE")
            metas[stem] = oid
        else:
            raise Hold("UNKNOWN_ARTICLE_FILENAME")
    need(bodies.keys() == metas.keys(), "UNPAIRED_ARTICLE_EVIDENCE")
    return bodies, metas

def check_sources(mapping):
    need(type(mapping) is dict and "README.md" in mapping, "INVALID_SOURCE_CATALOG")
    for name, oid in mapping.items():
        check_oid(oid)
        need(name == "README.md" or
             (name.endswith(".json") and SLUG.fullmatch(name[:-5])), "UNSAFE_SOURCE_FRAGMENT_PATH")

def build_crosswalk(snapshot, workorders):
    need(type(snapshot) is dict and snapshot.get("schema") == OLD_SCHEMA, "INVALID_R117_SNAPSHOT")
    need(type(workorders) is dict and workorders.get("schema") == ORDER_SCHEMA, "INVALID_R117_WORKORDERS")
    need(snapshot.get("issue") == workorders.get("issue") == 136 and
         snapshot.get("business_issue") == workorders.get("business_issue") == 820,
         "WRONG_COORDINATION_ISSUE")
    gov = snapshot.get("governance")
    need(type(gov) is dict and gov.get("release_state") == "HOLD" and
         all(gov.get(k) is False for k in ("may_publish", "may_merge", "independent_QD_PASS",
                                             "medical_safety_verified", "merchant_offer_verified")),
         "INVALID_SNAPSHOT_GOVERNANCE")
    need(workorders.get("release_state") == "HOLD" and
         all(workorders.get(k) is False for k in ("may_publish", "may_merge", "independent_QD_PASS")),
         "INVALID_WORKORDER_GOVERNANCE")
    snaps = snapshot.get("snapshots")
    need(type(snaps) is list and len(snaps) == 9, "INVALID_NINE_HEAD_COUNT")
    need([s.get("role") for s in snaps] == ["baseline", "candidate"]+["contributor"]*7,
         "INVALID_HEAD_ROLES")
    base, candidate, *contributors = snaps
    need({c.get("cluster") for c in contributors} == CLUSTERS,
         "MISSING_OR_DUPLICATED_CONTRIBUTOR")
    need(len({s.get("ref") for s in snaps}) == 9, "DUPLICATE_HEAD_REFS")
    for s in snaps:
        need(type(s.get("ref")) is str and s["ref"], "INVALID_HEAD_REF")
        check_oid(s.get("sha"))
        check_articles(s.get("article_files"))
        check_sources(s.get("source_fragments"))
    base_bodies, base_metas = check_articles(base["article_files"])
    cand_bodies, cand_metas = check_articles(candidate["article_files"])
    need(len(base_bodies) == 35 and base_bodies.keys() == cand_bodies.keys(),
         "NOT_ORIGINAL_35_PAIRED_ROUTES")
    need(workorders.get("baseline_sha") == base["sha"] and
         workorders.get("candidate_sha") == candidate["sha"] and
         workorders.get("seven_contributor_heads") == {c["cluster"]: c["sha"] for c in contributors},
         "STALE_OR_INCONSISTENT_GIT_HEAD")
    observations = []
    for c in contributors:
        for key, prefix in (("article_files",ARTICLE_PREFIX), ("source_fragments",SOURCE_PREFIX)):
            need(c[key].keys() <= base[key].keys(), "UNTRACKED_NEW_SOURCE_OR_ARTICLE_PATH")
            for name, oid in c[key].items():
                if oid == base[key][name]:
                    continue
                cand_oid = candidate[key].get(name)
                expected = "EXACT_IN_RELEASE_CANDIDATE" if oid == cand_oid else (
                    "RELEASE_CANDIDATE_RETAINS_BASELINE" if cand_oid == base[key][name] else
                    "RELEASE_CANDIDATE_DIFFERS_FROM_BOTH")
                observations.append({"cluster":c["cluster"],"contributor_head":c["sha"],
                     "path":prefix+name,"kind":key,"contributor_git_blob":oid,
                     "frozen_original_git_blob":base[key][name],
                     "release_candidate_git_blob":cand_oid,"disposition":expected,
                     "requires_human_source_or_safety_adjudication":True})
    actual = workorders.get("rows")
    need(type(actual) is list and len(actual) == len(observations), "WORKORDER_LENGTH_DRIFT")
    def keyed(rows):
        index = {}
        for row in rows:
            need(type(row) is dict and type(row.get("path")) is str and
                 type(row.get("cluster")) is str, "INVALID_WORKORDER_ROW")
            key=(row["cluster"],row["path"])
            need(key not in index, "DUPLICATE_WORKORDER_KEY")
            index[key]=row
        return index
    need(keyed(actual) == keyed(observations), "SOURCE_CUSTODY_OR_CITATION_WORKORDER_DRIFT")
    grouped=defaultdict(list)
    for row in observations:
        grouped[row["path"]].append(row)
    need(workorders.get("observation_count") == len(observations) and
         workorders.get("unique_changed_paths") == len(grouped) and
         workorders.get("non_exact_candidate_observations") ==
            sum(r["disposition"]!="EXACT_IN_RELEASE_CANDIDATE" for r in observations),
         "WORKORDER_SUMMARY_DRIFT")
    overlaps=workorders.get("overlapping_paths")
    need(type(overlaps) is list, "MISSING_OVERLAP_PROVENANCE")
    expected_overlaps={p:(sorted(r["cluster"] for r in rows),
                          len({r["contributor_git_blob"] for r in rows}))
                       for p,rows in grouped.items() if len(rows)>1}
    need(len(overlaps) == len(expected_overlaps), "OVERLAP_COUNT_DRIFT")
    for over in overlaps:
        need(type(over) is dict and over.get("path") in expected_overlaps and
             (sorted(over.get("contributors", [])),over.get("distinct_contributor_git_blobs")) ==
             expected_overlaps[over["path"]], "OVERLAP_SOURCE_CUSTODY_DRIFT")
    roster=[]
    for slug in sorted(base_bodies):
        stem=ARTICLE_PREFIX+slug
        roster.append({"slug":slug,"original_body_git_blob":base_bodies[slug],
                       "original_meta_git_blob":base_metas[slug],
                       "candidate_body_git_blob":cand_bodies[slug],
                       "candidate_meta_git_blob":cand_metas[slug],
                       "contributor_changed_paths":sorted(p for p in grouped if p.startswith(stem+".")),
                       "human_source_and_safety_review":"NOT_COMPLETE"})
    decisions=[]
    for path in sorted(grouped):
        rows=grouped[path]
        variant_oids=sorted({r["contributor_git_blob"] for r in rows})
        is_source=path.startswith(SOURCE_PREFIX)
        is_metadata=path.endswith(".meta.json")
        decisions.append({"path":path,"path_kind":"source_fragment" if is_source else
                          ("article_metadata" if is_metadata else "article_body"),
             "risk_priority":"P0" if is_source or is_metadata else "P1",
             "baseline_git_blob":rows[0]["frozen_original_git_blob"],
             "candidate_git_blob":rows[0]["release_candidate_git_blob"],
             "contributor_variants":variant_oids,
             "contributor_heads":{r["cluster"]:r["contributor_head"] for r in sorted(rows,key=lambda x:x["cluster"])},
             "contributor_dispositions":{r["cluster"]:r["disposition"] for r in sorted(rows,key=lambda x:x["cluster"])},
             "human_review_required":True,"human_decision":"UNREVIEWED",
             "checks_pending":["meaning_and_claim_support","source_id_and_url_lineage",
                 "reading_depth","warnings_and_caveats","safety_state","copyright_and_attribution"]})
    return {"schema":NEW_SCHEMA,"issue":136,"business_issue":820,"release_state":"HOLD",
        "may_publish":False,"may_merge":False,"independent_QD_PASS":False,
        "medical_safety_verified":False,"merchant_offer_verified":False,
        "qualified_human_review_complete":False,"snapshots_verified_against_live_heads":False,
        "baseline_sha":base["sha"],"candidate_sha":candidate["sha"],
        "contributor_heads":{c["cluster"]:c["sha"] for c in contributors},
        "input_evidence_sha256":{"snapshots":text_digest(snapshot),
            "workorders":text_digest({**workorders, "rows":sorted(actual, key=lambda r:(r["cluster"],r["path"]))})},
        "article_count":len(roster),"article_roster":roster,
        "unique_changed_paths":len(decisions),"contributor_change_observations":len(observations),
        "review_decisions":decisions,
        "interpretation":"Immutable Git identity crosswalk only. All source and safety determinations require qualified independent human review."}

def verify_crosswalk(snapshot, workorders, existing):
    expected=build_crosswalk(snapshot, workorders)
    need(type(existing) is dict and existing == expected, "REVIEW_CROSSWALK_TAMPER_OR_STALE")
    return {"state":"HOLD","article_count":expected["article_count"],
            "changed_paths":expected["unique_changed_paths"],
            "observations":expected["contributor_change_observations"],
            "all_unreviewed":True,"may_publish":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshots",type=Path,required=True)
    p.add_argument("--workorders",type=Path,required=True)
    p.add_argument("--verify-crosswalk",type=Path)
    args=p.parse_args()
    try:
        s=strict_load(args.snapshots)
        w=strict_load(args.workorders)
        if args.verify_crosswalk:
            output=verify_crosswalk(s,w,strict_load(args.verify_crosswalk))
        else:
            output=build_crosswalk(s,w)
        print(json.dumps(output,sort_keys=True,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as e:
        print("HOLD: "+str(e),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    sys.exit(main())
