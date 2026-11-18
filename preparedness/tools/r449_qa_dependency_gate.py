#!/usr/bin/env python3
"""R449: fail-closed original Preparedness QA-branch custody preflight.

Read-only evidence check. Passing structural checks NEVER means safety review,
QD approval, a production build, a WordPress release, or commercial conversion.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

HOLD = "DRAFT_HARD_HOLD"
EXPECTED = (157, 169, 2205, 2789, 2931, 2939)
OVERLAP = "preparedness/tests/test_preparedness.py"
ALLOWED = {
    157: {"preparedness/content/articles/household-emergency-plan.body.html",
          "preparedness/content/articles/three-day-kit.body.html",
          "preparedness/sources/fragments/start.json",
          "preparedness/taxonomy.json", OVERLAP},
    169: {OVERLAP},
    2205: {OVERLAP, "preparedness/audits/r318_source_fixture_qa_remediation_HARD_HOLD.md"},
}
BASES = {157:"claude/prep-start-bbfeb8", 169:"claude/prep-food-ccdc55",
         2205:"review/preparedness-food-fixture-isolation-20261030",
         2789:"main",
         2931:"research/apollo-r440-educator-offer-proof-20261117",
         2939:"review/preparedness-r447-adjudication-proposal-custody-20261117"}
PREFIXES = {2789:"preparedness/editorial-reviews/",
            2931:"experience2/apollo-r441/",
            2939:"preparedness/"}
COUNTS = {"articles":35,"source_ids":203,"source_occurrences":280,
          "distinct_literal_urls":181,"shared_url_review_groups":17,
          "unresolved_source_disputes":5,"unselected_forks":9,
          "contributor_refs":9}
SHA = re.compile(r"^[0-9a-f]{40}$")

def unique_object(pairs):
    d = {}
    for k,v in pairs:
        if k in d: raise ValueError("duplicate JSON key: "+k)
        d[k] = v
    return d

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object)

def audit(capture, fresh=None, ledger=None):
    failures = []
    def fail(code):
        if code not in failures: failures.append(code)
    if not isinstance(capture,dict):
        return result(["INVALID_CAPTURE"],{})
    if capture.get("repo") != "finalvestigestudios/final-vestige-site-layer":
        fail("REPO_DRIFT")
    if capture.get("source_issue") != 136 or capture.get("business_issue") != 820:
        fail("ISSUE_DRIFT")
    if capture.get("release_state") != HOLD or any(
            capture.get(k) is not False for k in
            ("publishable","qd_approved","paid_offer_verified","paid_conversion_verified")):
        fail("FALSE_APPROVAL")
    if capture.get("review_disputes") != {"source":5,"forks":9,"shared_url_groups":17}:
        fail("REVIEW_DISPUTES_LOST")
    if capture.get("merge_decision") != "NOT_APPROVED":
        fail("MERGE_APPROVAL_INVENTED")
    prs = capture.get("pull_requests")
    if not isinstance(prs,list):
        prs = []; fail("PR_CAPTURE_MISSING")
    numbers = [p.get("number") for p in prs if isinstance(p,dict)]
    if len(numbers)!=len(prs) or len(set(numbers))!=len(numbers) or set(numbers)!=set(EXPECTED):
        fail("PR_COVERAGE_MISMATCH")
    pr_map = {}
    for p in prs:
        if not isinstance(p,dict) or p.get("number") not in EXPECTED:
            fail("PR_INVALID"); continue
        n = p["number"]; pr_map[n] = p
        for key in ("head_sha","base_sha"):
            if not isinstance(p.get(key),str) or not SHA.fullmatch(p[key]):
                fail("INVALID_SHA:"+str(n)+":"+key)
        if p.get("base")!=BASES[n]:
            fail("BASE_CHANGED:"+str(n))
        if p.get("state")!="open" or p.get("draft") is not True:
            fail("NOT_UNMERGED_DRAFT:"+str(n))
        files = p.get("filenames")
        if not isinstance(files,list) or any(
                not isinstance(f,str) or not f or f.startswith("/") or
                "\\" in f or ".." in f.split("/") for f in files):
            fail("PATH_INVALID:"+str(n)); continue
        if len(files)!=len(set(files)) or len(files)!=p.get("changed_files"):
            fail("CHANGED_FILES_MISMATCH:"+str(n))
        if n in ALLOWED and set(files)!=ALLOWED[n]:
            fail("QA_SCOPE_DRIFT:"+str(n))
        if n in PREFIXES and (not files or any(
                not f.startswith(PREFIXES[n]) for f in files)):
            fail("FOREIGN_WORKSTREAM_CHANGE:"+str(n))
        if n==2939 and any(
                not f.startswith(("preparedness/reviews/",
                                  "preparedness/tools/",
                                  "preparedness/tests/")) for f in files):
            fail("INTEGRATION_MANUSCRIPT_TOUCH:"+str(n))
    if 169 in pr_map and 2205 in pr_map and (
            pr_map[2205].get("base_sha")!=pr_map[169].get("head_sha")):
        fail("DEPENDENT_QA_PARENT_SHA_DRIFT")
    path_prs=defaultdict(list)
    for n in (157,169,2205):
        for f in pr_map.get(n,{}).get("filenames",[]):
            if isinstance(f,str): path_prs[f].append(n)
    overlap={f:sorted(ns) for f,ns in path_prs.items() if len(ns)>1}
    if overlap!={OVERLAP:[157,169,2205]}:
        fail("QA_TEST_FILE_OVERLAP_DRIFT")
    pins=capture.get("branch_pins")
    if not isinstance(pins,list) or len(pins)!=9 or any(
        not isinstance(p,dict) or not isinstance(p.get("branch"),str) or
        not p["branch"].startswith("claude/prep-") or
        not isinstance(p.get("sha"),str) or not SHA.fullmatch(p["sha"])
        for p in pins) or len({p.get("branch") for p in pins if isinstance(p,dict)})!=9:
        fail("ORIGINAL_BRANCH_PINS_INVALID")
    if ledger is None:
        fail("NO_AUTHENTIC_ORIGINAL_LEDGER")
    elif not isinstance(ledger,dict):
        fail("ORIGINAL_LEDGER_INVALID")
    else:
        if ledger.get("counts")!=COUNTS or ledger.get("branch_pins")!=pins:
            fail("ORIGINAL_ARTICLE_SOURCE_CUSTODY_DRIFT")
        articles=ledger.get("articles")
        if not isinstance(articles,list) or len(articles)!=35 or any(
                a.get("publication_state")!="HARD_HOLD" or
                a.get("qualified_safety_state")!="NOT_APPROVED" or
                a.get("source_occurrences_bound_to_this_article")!=
                "NOT_AUTHENTICATED_FROM_ORIGINAL_DOCKET" for a in articles):
            fail("ORIGINAL_ARTICLE_SAFETY_OR_PLACEMENTS_UNPROVEN")
        if ledger.get("release_state")!=HOLD or ledger.get("publishable") is not False:
            fail("ORIGINAL_LEDGER_PREMATURE_APPROVAL")
    if fresh is None:
        fail("NO_INDEPENDENT_FRESH_GITHUB_READBACK")
    elif not isinstance(fresh,dict):
        fail("FRESH_READBACK_INVALID")
    else:
        observed=fresh.get("pull_requests")
        if not isinstance(observed,list) or len(observed)!=len(EXPECTED):
            fail("FRESH_PR_COVERAGE_MISSING")
        else:
            obs_by={p.get("number"):p for p in observed if isinstance(p,dict)}
            if set(obs_by)!=set(EXPECTED): fail("FRESH_PR_IDENTITIES_CHANGED")
            for n,p in pr_map.items():
                other=obs_by.get(n,{})
                for key in ("head_sha","base_sha","base","state","draft",
                            "filenames","changed_files"):
                    if p.get(key)!=other.get(key):
                        fail("FRESH_PR_DRIFT:"+str(n)+":"+key)
        if not isinstance(pins,list) or fresh.get("observed_branch_heads") != {
                p["branch"]:p["sha"] for p in pins if isinstance(p,dict) and
                "branch" in p and "sha" in p}:
            fail("FRESH_ORIGINAL_BRANCH_DRIFT")
        if not isinstance(fresh.get("observed_at_utc"),str):
            fail("FRESH_TIMESTAMP_MISSING")
    return result(failures,overlap)

def result(failures,overlap):
    return {"release_state":HOLD, "errors":failures,
            "structural_preflight_pass":not failures,
            "overlapping_files":overlap,
            "required_manual_qa_merge_resolution":True,
            "original_source_disputes_pending":5,
            "original_manuscript_forks_unselected":9,
            "source_url_groups_unmerged":17,
            "native_build_verified":False,
            "genuine_export_pairs_verified":False,
            "qd_pass":False, "publishable":False,
            "verified_fv_preparedness_offer":False,
            "grok_family_asset_match":None,
            "net_revenue_per_1000_qualified_sessions":None}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--capture",required=True,type=Path)
    parser.add_argument("--fresh",type=Path)
    parser.add_argument("--ledger",type=Path)
    a=parser.parse_args()
    try:
        r=audit(read_json(a.capture),
                read_json(a.fresh) if a.fresh else None,
                read_json(a.ledger) if a.ledger else None)
    except (OSError,ValueError,TypeError) as exc:
        r=result(["INPUT_REJECTED:"+type(exc).__name__],{})
    print(json.dumps(r,indent=2,sort_keys=True))
    return 2 if r["errors"] else 0

if __name__=="__main__":
    raise SystemExit(main())
