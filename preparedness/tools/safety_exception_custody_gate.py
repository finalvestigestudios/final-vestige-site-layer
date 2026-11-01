#!/usr/bin/env python3
"""R50: preserve R48 safety exceptions and source variants; NEVER grant safety approval."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

class SafetyHold(ValueError):
    """Fail closed if original evidence or outstanding reviews are lost."""

def need(ok, reason):
    if not ok:
        raise SafetyHold(reason)

def digest(obj):
    b = json.dumps(obj, sort_keys=True, ensure_ascii=False, allow_nan=False,
                   separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

SEVERITIES = {f"SX-{n:02d}": ("HIGH" if n <= 5 else "MEDIUM" if n <= 12 else "LOW")
              for n in range(1, 16)}
IDS = {f"A{n:02d}" for n in range(1, 21)} | {f"B{n:02d}" for n in range(1, 10)}
REVIEWABLE = IDS - {"B09"}
SX = re.compile(r"^\|\s*(SX-\d{2})\s*\|\s*(HIGH|MEDIUM|LOW)\s*\|", re.M)
B = re.compile(r"^\|\s*[\x60]([a-z0-9-]+)[\x60]\s*\|\s*([^|\n]+?)\s*\|\s*(https://[^|\s]+)\s*\|", re.M)
A = re.compile(r"^\|\s*([AB]\d{2}(?:\s*,\s*[AB]\d{2})*)\s*\|", re.M)

def parse_register(md):
    need(type(md) is str and "## Appendix A:" in md and "## Appendix B:" in md,
         "register appendices unavailable")
    prior, _, appendix_b = md.partition("## Appendix B:")
    head, _, appendix_a = prior.partition("## Appendix A:")
    need("**No exception below is closed.**" in head and
         ("Every entry is " + chr(96) + "OPEN" + chr(96)) in head,
         "safety HOLD notice lost")
    sx = SX.findall(head)
    need(len(sx) == 15 and len({key for key, _ in sx}) == 15
         and dict(sx) == SEVERITIES,
         "an open incident was lost, duplicated, relabeled or downgraded")
    appendix_ids = [v for m in A.findall(appendix_a)
                    for v in re.findall(r"[AB]\d{2}", m)]
    need(len(appendix_ids) == 28 and set(appendix_ids) == REVIEWABLE,
         "28 independently identified candidate rows not preserved")
    blocked = B.findall(appendix_b)
    need(len(blocked) == 25 and len({sid for sid, _, _ in blocked}) == 25,
         "25 previously inaccessible cited source records not preserved")
    return sx, blocked, appendix_ids

def original_rows(lib, sid):
    rows = getattr(lib, "source_variants", {}).get(sid, [])
    if not rows:
        s = getattr(lib, "register", {}).get(sid)
        rows = [s] if s is not None else []
    need(bool(rows), "original source identifier absent: " + sid)
    need(all(type(v) is dict and type(v.get("url")) is str
             and v["url"].startswith("https://") for v in rows),
         "original source URL invalid: " + sid)
    return [{"origin": s.get("_origin", "base"), "url": s["url"],
             "original_source_sha256": digest(s)} for s in rows]

def audit(lib, md, candidates, access=None):
    sx, blocked, app = parse_register(md)
    need(type(candidates) is list and len(candidates) == 29,
         "R48 source candidate census changed")
    ids = [c.get("id") for c in candidates if type(c) is dict]
    need(len(ids) == 29 and len(set(ids)) == 29 and set(ids) == IDS,
         "R48 candidate identity missing or duplicated")
    if access is None:
        access = []
    need(type(access) is list, "accessibility records not an array")
    by_url = {}
    for rec in access:
        need(type(rec) is dict and type(rec.get("url")) is str
             and rec["url"].startswith("https://")
             and type(rec.get("ok")) is bool and rec["url"] not in by_url,
             "accessibility evidence malformed or duplicated")
        by_url[rec["url"]] = rec

    blockers = []
    for sid, failure, displayed_url in blocked:
        variants = original_rows(lib, sid)
        # Appendix B sometimes shows a truncated URL; use original source
        # variants as canonical, not a truncated or updated display string.
        need(any(v["url"].startswith(displayed_url.rstrip("…")) for v in variants),
             "Appendix B URL disagrees with original source identity: " + sid)
        blockers.append({
            "source_id": sid, "machine_retrieval_failure": failure.strip(),
            "appendix_display_url": displayed_url, "original_variants": variants,
            "r48_machine_access_observations": [
                {"url": v["url"], "ok": by_url[v["url"]]["ok"]}
                for v in variants if v["url"] in by_url],
            "human_link_check_complete": False, "review_state": "HOLD",
        })

    tasks = []
    for row in candidates:
        sid, slug = row["id"], row.get("article")
        need(type(slug) is str and slug in lib.articles,
             "candidate article missing: " + sid)
        meta = lib.articles[slug]
        need(row.get("file") ==
             "preparedness/content/articles/" + slug + ".body.html"
             and type(meta.get("_body")) is str,
             "original candidate body/slug path changed: " + sid)
        need(type(row.get("keys")) is list and bool(row["keys"]),
             "keyword search evidence missing: " + sid)
        need(type(row.get("sources_with_hits")) is dict and
             type(row.get("sources_not_in_corpus")) is list and
             row.get("status") in ("ALL_KEYS_FOUND_IN_CITED_SOURCES",
                                    "SOME_KEYS_FOUND_IN_CITED_SOURCES",
                                    "NO_KEYS_FOUND"),
             "invalid machine-triage row: " + sid)
        placeholder = sid == "B09"
        if placeholder:
            need(row.get("note") == "placeholder" and not row.get("excerpt")
                 and not (type(row.get("line")) is int and row["line"] > 0),
                 "B09 has no claim or reviewed passage; cannot claim verification")
        else:
            need(type(row.get("excerpt")) is str and row["excerpt"].strip()
                 and type(row.get("line")) is int and row["line"] > 0,
                 "candidate original line/excerpt unavailable: " + sid)
        source_ids = list(row["sources_with_hits"]) + list(row["sources_not_in_corpus"])
        need(len(source_ids) == len(set(source_ids)) and bool(source_ids)
             and all(type(i) is str and i for i in source_ids),
             "candidate lost source IDs or duplicated evidence: " + sid)
        sources = []
        for source_id in source_ids:
            variants = original_rows(lib, source_id)
            try:
                selected = lib.source_for(meta, source_id)
            except (KeyError, ValueError, TypeError):
                selected = None
            sources.append({
                "source_id": source_id,
                "all_original_contributor_variants": variants,
                "article_scope_source_sha256": digest(selected) if selected else None,
                "extracted_keyword_hits_not_claim_support":
                    len(row["sources_with_hits"].get(source_id, [])),
                "not_in_r48_extracted_corpus":
                    source_id in row["sources_not_in_corpus"],
                "human_claim_support_verified": False,
            })
        tasks.append({
            "candidate": sid, "article": slug,
            "article_html_sha256": hashlib.sha256(
                meta["_body"].encode("utf-8")).hexdigest(),
            "line_at_original_snapshot": row.get("line"),
            "excerpt_not_independently_verified": row.get("excerpt"),
            "source_records": sources,
            "keyword_result_not_factual_validation": row["status"],
            "in_r48_reviewed_appendix": sid in app,
            "unevaluated_placeholder": placeholder,
            "qualified_human_review_completed": False,
            "may_publish": False, "state": "HOLD",
        })

    result = {
        "schema": "r50-safety-exception-lineage-v1", "issue": 136,
        "release_state": "HOLD", "may_publish": False,
        "qualified_safety_clearance": False, "independent_QD_approval": False,
        "human_source_links_verified": False, "claim_accuracy_verified": False,
        "counts": {"open_incidents": 15, "high": 5, "medium": 7, "low": 3,
                   "historically_blocked_sources": 25, "candidate_rows": 29,
                   "reviewable_candidates": 28, "placeholder_B09": 1,
                   "completed_independent_reviews": 0},
        "open_incidents": [{"id": sid, "severity": sev, "state": "HOLD"}
                           for sid, sev in sx],
        "unresolved_source_access": blockers, "candidate_workorders": tasks,
        "limitations": (
            "AI-assisted keyword presence, numeric tokens and page access are "
            "NOT human source validation, specific-claim support or a qualified "
            "safety review. The 25 historically blocked sources are a separate "
            "census from the smaller R48 numeric-accessibility sample. "
            "B09 was a placeholder, not a 29th evaluated claim."),
    }
    result["fingerprint_sha256"] = digest(result)
    return result

def _json(path, root):
    need(path.is_file() and not path.is_symlink()
         and path.resolve(strict=True).is_relative_to(root),
         "private evidence missing, linked or outside repo")
    return json.loads(path.read_text(encoding="utf-8"))

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path,
                    default=Path(__file__).resolve().parents[2])
    ap.add_argument("--format", choices=("summary", "json"), default="summary")
    args = ap.parse_args(argv)
    try:
        root = args.repo_root.resolve(strict=True)
        p = root / "preparedness/tools/build.py"
        need(p.is_file() and not p.is_symlink(),
             "original article/source library unavailable")
        spec = importlib.util.spec_from_file_location("r50_original_library", p)
        need(spec is not None and spec.loader is not None,
             "cannot load original builder")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        lib = mod.Library(root / "preparedness")
        docs = root / "preparedness/docs/r48"
        md_path = docs / "SAFETY-EXCEPTION-REGISTER-2026-11-01.md"
        need(md_path.is_file() and not md_path.is_symlink()
             and md_path.resolve(strict=True).is_relative_to(root),
             "original safety exception register missing")
        result = audit(lib, md_path.read_text(encoding="utf-8"),
                       _json(docs / "SAFETY-CANDIDATES-2026-11-01.json", root),
                       _json(docs / "SOURCE-ACCESSIBILITY-2026-11-01.json", root))
        if args.format == "summary":
            result = {k: v for k, v in result.items()
                      if k not in ("open_incidents", "unresolved_source_access",
                                   "candidate_workorders")}
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except (SafetyHold, OSError, ValueError, TypeError, KeyError) as exc:
        print("R50 SAFETY EXCEPTION CUSTODY HOLD: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
