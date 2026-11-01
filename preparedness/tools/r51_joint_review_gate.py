#!/usr/bin/env python3
"""R51: independently cross-check R49 numeric and R50 safety custody; HOLD only.

Do NOT infer verified sources, approved safety advice, independent reviewer identity,
or publication eligibility. This is a deterministic, read-only data-consistency gate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_COUNTS = (186, 89, 7, 15, 29, 25)
FALSE_FLAGS = (
    "may_publish", "qualified_safety_clearance", "independent_QD_approval",
    "human_source_links_verified",
)

class IntegrationHold(ValueError):
    """Independent custody disagreement: never grant clearance."""

def need(condition, message):
    if not condition:
        raise IntegrationHold(message)

def digest(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         allow_nan=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def sha(value):
    return isinstance(value, str) and HEX64.fullmatch(value) is not None

def _check_fingerprint(report, name):
    need(type(report) is dict and sha(report.get("fingerprint_sha256")),
         name + " missing report fingerprint")
    payload = {k: v for k, v in report.items() if k != "fingerprint_sha256"}
    need(digest(payload) == report["fingerprint_sha256"],
         name + " report altered after evidence gate")

def verify_reports(numeric, safety, *, expected=DEFAULT_COUNTS):
    """Verify both reports, cross-article/source lineage, all false safety states.

    expected = (quantified claims, accessibility URLs, inaccessible URLs,
                open safety incidents, candidate rows, historic blocked source IDs).
    Overrides exist only to support small, independent synthetic test fixtures.
    """
    need(type(expected) is tuple and len(expected) == 6
         and all(type(v) is int and v >= 0 for v in expected),
         "invalid independently pinned census")
    claims, access, inaccessible, incidents, candidates, blocked = expected
    _check_fingerprint(numeric, "R49 numeric")
    _check_fingerprint(safety, "R50 safety")
    for name, report in (("R49", numeric), ("R50", safety)):
        need(report.get("issue") == 136 and report.get("release_state") == "HOLD",
             name + " escaped issue 136 / release HOLD")
        for flag in FALSE_FLAGS:
            need(report.get(flag) is False, name + " false approval flag: " + flag)
    need(numeric.get("source_claim_accuracy_verified") is False
         and numeric.get("human_source_reviews_completed") is False,
         "R49 human claim review was falsely upgraded")
    need(safety.get("claim_accuracy_verified") is False,
         "R50 factual verification was falsely upgraded")
    nc = numeric.get("counts")
    sc = safety.get("counts")
    need(type(nc) is dict and type(sc) is dict,
         "missing independent evidence counts")
    need((nc.get("original_numeric_claim_blocks"),
          nc.get("original_accessibility_urls"),
          nc.get("unavailable_source_urls")) == (claims, access, inaccessible),
         "R49 frozen quantitative/accessibility census changed")
    need(type(nc.get("accessible_text_extractions_not_human_checks")) is int
         and nc["accessible_text_extractions_not_human_checks"] == access - inaccessible,
         "R49 source accessibility arithmetic inconsistent")
    need((sc.get("open_incidents"), sc.get("candidate_rows"),
          sc.get("historically_blocked_sources")) == (incidents, candidates, blocked),
         "R50 frozen safety/blocked-source census changed")
    need(sc.get("completed_independent_reviews") == 0
         and sc.get("placeholder_B09") == 1
         and sc.get("reviewable_candidates") == candidates - 1,
         "R50 unevaluated placeholder or human review count upgraded")

    nr = numeric.get("review_tasks")
    sr = safety.get("candidate_workorders")
    si = safety.get("open_incidents")
    sb = safety.get("unresolved_source_access")
    need(all(type(x) is list for x in (nr, sr, si, sb)),
         "individual original review evidence missing")
    need((len(nr), len(sr), len(si), len(sb)) ==
         (claims, candidates, incidents, blocked),
         "individual review records lost, duplicated or manufactured")
    seen_claims, article_shas, scoped_sources = set(), {}, {}
    cited_occurrences = 0
    numeric_urls = set()
    for index, task in enumerate(nr, start=1):
        need(type(task) is dict and task.get("claim_ordinal") == index,
             "original numeric claim occurrence order changed")
        identity = task.get("claim_identity_sha256")
        slug, article_sha = task.get("slug"), task.get("original_article_html_sha256")
        need(sha(identity) and identity not in seen_claims and type(slug) is str
             and bool(slug) and sha(article_sha),
             "invalid or duplicated original quantified claim identity")
        seen_claims.add(identity)
        if slug in article_shas:
            need(article_shas[slug] == article_sha,
                 "conflicting original article body hash in numeric review")
        article_shas[slug] = article_sha
        for flag in ("source_claim_accuracy_verified",
                     "qualified_safety_clearance", "may_publish"):
            need(task.get(flag) is False,
                 "numeric claim assigned false approval: " + flag)
        need(task.get("state") ==
             "PENDING_INDEPENDENT_SOURCE_SCOPE_UNIT_CONTEXT_AND_SAFETY_REVIEW",
             "numeric claim no longer has independent-review HOLD state")
        flags = task.get("review_flags")
        need(type(flags) is list and
             "NUMBER_TOKEN_IS_NOT_CLAIM_OR_UNIT_VERIFICATION" in flags and
             "HUMAN_SOURCE_AND_CONTEXT_CHECK_REQUIRED" in flags,
             "numeric token presence misrepresented as claim verification")
        ids, variants = task.get("original_source_id_occurrences"), task.get("original_source_variants")
        need(type(ids) is list and type(variants) is list
             and len(ids) == len(variants) and bool(ids),
             "numeric claim lost original citation occurrences")
        cited_occurrences += len(ids)
        for sid, source in zip(ids, variants):
            need(type(source) is dict and type(sid) is str and sid
                 and source.get("source_id") == sid
                 and type(source.get("original_url")) is str
                 and source["original_url"].startswith("https://")
                 and sha(source.get("original_source_record_sha256"))
                 and source.get("human_source_link_checked") is False
                 and source.get("claim_supported_verified") is False,
                 "numeric source variant lost identity or was falsely verified")
            key = (slug, sid)
            current_sha = source["original_source_record_sha256"]
            if key in scoped_sources:
                need(scoped_sources[key] == current_sha,
                     "source record changed inside same article/source ID")
            scoped_sources[key] = current_sha
            numeric_urls.add(source["original_url"])
    need(nc.get("original_citation_occurrences_in_numeric_blocks") == cited_occurrences,
         "quantified-claim citation occurrence count is misleading")

    seen_safety = set()
    for row in si:
        need(type(row) is dict and type(row.get("id")) is str
             and re.fullmatch(r"SX-\d{2}", row["id"])
             and row["id"] not in seen_safety
             and row.get("state") == "HOLD"
             and row.get("severity") in ("HIGH", "MEDIUM", "LOW"),
             "safety incident lost, duplicated, downgraded or cleared")
        seen_safety.add(row["id"])
    severity_counts = Counter(row["severity"] for row in si)
    need((sc.get("high"), sc.get("medium"), sc.get("low")) ==
         (severity_counts["HIGH"], severity_counts["MEDIUM"], severity_counts["LOW"]),
         "safety incident severity census changed")

    blocked_ids = set()
    historical_overlap = []
    for row in sb:
        need(type(row) is dict and type(row.get("source_id")) is str
             and row["source_id"] not in blocked_ids
             and row.get("review_state") == "HOLD"
             and row.get("human_link_check_complete") is False
             and type(row.get("machine_retrieval_failure")) is str
             and bool(row["machine_retrieval_failure"].strip()),
             "historic source blocker lost, duplicated or falsely resolved")
        blocked_ids.add(row["source_id"])
        variants = row.get("original_variants")
        need(type(variants) is list and bool(variants),
             "historic source blocker lost contributor reading variants")
        for v in variants:
            need(type(v) is dict and
                 type(v.get("url")) is str and v["url"].startswith("https://")
                 and sha(v.get("original_source_sha256")),
                 "historic blocked-source variant identity changed")
            if v["url"] in numeric_urls:
                historical_overlap.append((row["source_id"], v["url"]))
        observations = row.get("r48_machine_access_observations")
        need(type(observations) is list and
             all(type(v) is dict and type(v.get("ok")) is bool for v in observations),
             "historical failure observations rewritten as human checks")

    seen_candidates, overlap_count = set(), 0
    for task in sr:
        need(type(task) is dict and type(task.get("candidate")) is str
             and task["candidate"] not in seen_candidates,
             "safety candidate missing, duplicated or corrupted")
        cid, slug = task["candidate"], task.get("article")
        seen_candidates.add(cid)
        need(type(slug) is str and sha(task.get("article_html_sha256"))
             and task.get("state") == "HOLD"
             and task.get("may_publish") is False
             and task.get("qualified_human_review_completed") is False,
             "safety candidate lost article identity or gained false approval")
        if slug in article_shas:
            need(article_shas[slug] == task["article_html_sha256"],
                 "R49/R50 original article SHA disagreement")
        if cid == "B09":
            need(task.get("unevaluated_placeholder") is True
                 and task.get("in_r48_reviewed_appendix") is False
                 and task.get("line_at_original_snapshot") is None
                 and not task.get("excerpt_not_independently_verified"),
                 "B09 placeholder promoted into an evaluated claim")
        else:
            need(task.get("unevaluated_placeholder") is False
                 and task.get("in_r48_reviewed_appendix") is True,
                 "genuine candidate silently reclassified as placeholder")
        sources = task.get("source_records")
        need(type(sources) is list and bool(sources),
             "candidate source evidence discarded")
        seen_source_ids = set()
        for source in sources:
            need(type(source) is dict and type(source.get("source_id")) is str
                 and source["source_id"] not in seen_source_ids
                 and source.get("human_claim_support_verified") is False,
                 "candidate source duplicated or falsely verified")
            sid = source["source_id"]
            seen_source_ids.add(sid)
            h = source.get("article_scope_source_sha256")
            need(h is None or sha(h),
                 "candidate article-scoped original source hash malformed")
            variants = source.get("all_original_contributor_variants")
            need(type(variants) is list and bool(variants)
                 and all(type(v) is dict and sha(v.get("original_source_sha256"))
                         and type(v.get("url")) is str and v["url"].startswith("https://")
                         for v in variants),
                 "candidate lost independent contributor variant lineage")
            if h is not None and (slug, sid) in scoped_sources:
                need(h == scoped_sources[(slug, sid)],
                     "R49/R50 same-article source fingerprint disagreement")
                overlap_count += 1
    need("B09" in seen_candidates,
         "unevaluated B09 placeholder omitted from original machine evidence")
    result = {
        "schema": "r51-reconciled-review-custody-v1", "issue": 136,
        "release_state": "HOLD", "may_publish": False,
        "qualified_safety_clearance": False,
        "independent_QD_approval": False, "human_source_links_verified": False,
        "claim_accuracy_verified": False,
        "machine_validation_not_independent_review": True,
        "counts": {
            "quantified_claims_pending": claims,
            "source_access_urls_machine_observed": access,
            "machine_inaccessible_urls_in_numeric_sample": inaccessible,
            "historically_blocked_original_source_ids": blocked,
            "open_safety_incidents": incidents,
            "unevaluated_placeholder_candidates": 1,
            "safety_candidate_rows_not_approvals": candidates,
            "cross_report_original_source_id_matches": overlap_count,
            "blocked_historical_variants_overlapping_numeric_urls":
                len(historical_overlap),
        },
        "upstream_report_sha256": {
            "R49": numeric["fingerprint_sha256"],
            "R50": safety["fingerprint_sha256"],
        },
        "historical_blocked_numeric_url_overlap_not_resolved":
            sorted([{"source_id": sid, "url": url} for sid, url in historical_overlap],
                   key=lambda x: (x["source_id"], x["url"])),
        "limitations": (
            "Same-repository report hashes prove internal consistency, not an "
            "independently trusted custody anchor. Machine page access and matched "
            "numeric tokens are not claim support. Historic blocked sources and "
            "recent numeric samples are different censuses. All 35 articles, the "
            "water tool, 30 shared-URL source groups, 43 fallback relationships "
            "and all human/qualified-safety/QD release gates remain on HOLD."),
    }
    result["fingerprint_sha256"] = digest(result)
    return result

def _module(name, path):
    need(path.is_file() and not path.is_symlink(), "missing original audit: " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "cannot load audit: " + name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--format", choices=("summary", "json"), default="summary")
    args = parser.parse_args(argv)
    try:
        root = args.repo_root.resolve(strict=True)
        original = _module("r51_build", root / "preparedness/tools/build.py")
        r49 = _module("r51_numeric", root / "preparedness/tools/figure_source_scope_triage_gate.py")
        r50 = _module("r51_safety", root / "preparedness/tools/safety_exception_custody_gate.py")
        lib = original.Library(root / "preparedness")
        docs = root / "preparedness/docs/r48"
        figures = r49._read(docs / "FIGURE-TRIAGE-2026-11-01.json", root)
        access = r49._read(docs / "SOURCE-ACCESSIBILITY-2026-11-01.json", root)
        mdpath = docs / "SAFETY-EXCEPTION-REGISTER-2026-11-01.md"
        need(mdpath.is_file() and not mdpath.is_symlink()
             and mdpath.resolve(strict=True).is_relative_to(root),
             "original safety incident register lost")
        candidates = r50._json(docs / "SAFETY-CANDIDATES-2026-11-01.json", root)
        n = r49.audit(lib, figures, access, expected=(186, 89, 82, 7))
        s = r50.audit(lib, mdpath.read_text(encoding="utf-8"), candidates, access)
        report = verify_reports(n, s)
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps(report, sort_keys=True, ensure_ascii=False))
        return 0
    except (IntegrationHold, OSError, ValueError, TypeError, KeyError, ImportError) as exc:
        print("R51 CROSS-REPORT SAFETY HOLD: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
