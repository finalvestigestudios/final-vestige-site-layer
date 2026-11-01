#!/usr/bin/env python3
"""R49: source-scoped, read-only audit of R48 *preliminary* numeric triage.

The R48 number-token test is NOT a claim verification: finding "20" somewhere
in one or several sources does not establish 20 seconds, the right source,
the correct conditions, or a medically safe instruction. Preserve the exact
original per-article source variant and queue every claim for independent review.
No network requests, writes, reviewer approvals, WordPress or publication.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

# Deliberately match the original R48 extraction contract, including its
# limitations. Changing this pattern requires regenerating and reviewing R48.
FIG = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?|\d+/\d+|[½⅛¼¾⅓⅔])\s*(?:-|to)?\s*"
    r"(?:(?:°\s?[FC])|degrees?|percent|%|feet|foot|ft|hours?|hrs?|"
    r"minutes?|mins?|seconds?|days?|weeks?|months?|years?|drops?|"
    r"teaspoons?|tsp|tablespoons?|gallons?|quarts?|liters?|litres?|"
    r"ounces?|oz|pounds?|lbs?|inch(?:es)?|micron|mL|ml|cups?|"
    r"miles?|mph|psi|pounds? of pressure|feet away)\b", re.I)
BLOCK = re.compile(r"<(p|li|td|th|blockquote|dd)\b[^>]*>(.*?)</\1>", re.S | re.I)
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
TAG = re.compile(r"<[^>]+>")
KNOWN = frozenset(("ALL_FIGURES_FOUND", "SOME_FIGURES_NOT_FOUND",
                   "NO_FIGURES_FOUND", "NO_TESTABLE_SOURCE"))
HOLD = "PENDING_INDEPENDENT_SOURCE_SCOPE_UNIT_CONTEXT_AND_SAFETY_REVIEW"
TOPICS = {
    "water-contamination": r"\b(?:boil|water|treat|filter|bleach|chlorine|chemical|advisory|disinfect)\b",
    "food-and-preservation": r"\b(?:food|meat|jerky|canner|canning|botuli|refrigerat|freez|curing|dehydrat)\w*",
    "fire-carbon-monoxide": r"\b(?:fire|generator|carbon monoxide|grill|burn|exhaust|combustion)\w*",
    "medical-vulnerable": r"\b(?:medicin|insulin|infant|baby|pregnan|disabled|medical device|child)\w*",
}

class TriageHold(ValueError):
    """Evidence missing or inconsistent: never infer clearance."""

def need(condition, message):
    if not condition:
        raise TriageHold(message)

def digest(item):
    raw = json.dumps(item, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def normalize(text):
    text = (text.lower().replace("½", "1/2").replace("⅛", "1/8")
            .replace("¼", "1/4").replace("¾", "3/4")
            .replace("–", "-").replace("’", "'"))
    return re.sub(r"\s+", " ", text)

def extract_original_claims(lib):
    """Re-derive R48 claim block identity from untouched article HTML."""
    rows = []
    for slug, meta in sorted(lib.articles.items()):
        if meta.get("kind") == "tool":
            continue
        need(meta.get("slug") == slug and isinstance(meta.get("_body"), str),
             "article slug or original HTML unavailable")
        for block in BLOCK.finditer(meta["_body"]):
            raw = block.group(2)
            cites = CITE.findall(raw)
            if not cites:
                continue
            text = normalize(html.unescape(TAG.sub(" ", CITE.sub(" ", raw))))
            figs = sorted({re.sub(r"\s+", " ", m.group(0)).strip()
                           for m in FIG.finditer(text)})
            if figs:
                rows.append({"slug": slug, "track": meta["track"],
                             "text": text[:400], "figs": figs, "cites": cites})
    return rows

def claim_key(row):
    return digest({key: row[key] for key in
                   ("slug", "track", "text", "figs", "cites")})

def audit(lib, figures, accessibility, expected=None):
    """Fail closed on stale/mis-scoped evidence. NEVER certify a claim.

    expected optionally pins (claim blocks, accessibility URLs, accessible,
    inaccessible). The production CLI requires the frozen R48 census; synthetic
    tests may pass a small independent census.
    """
    need(isinstance(figures, list) and isinstance(accessibility, list),
         "review inputs must be arrays")
    originals = extract_original_claims(lib)
    need(Counter(map(claim_key, originals)) == Counter(map(claim_key, figures)),
         "R48 claim rows no longer match original article blocks: re-triage required")
    by_url = {}
    for rec in accessibility:
        need(type(rec) is dict and type(rec.get("url")) is str
             and rec["url"].startswith("https://") and type(rec.get("ok")) is bool,
             "invalid source accessibility row")
        url = rec["url"]
        need(url not in by_url, "duplicate accessibility URL: " + url)
        need(rec["ok"] or bool(rec.get("error") or rec.get("status")),
             "inaccessible URL needs a recorded failure reason")
        need(not rec["ok"] or rec.get("kind") == "html",
             "PDF/unknown kind cannot be tested as source text")
        by_url[url] = rec
    ok_count = sum(r["ok"] for r in accessibility)
    if expected is not None:
        need(type(expected) is tuple and len(expected) == 4
             and all(type(x) is int and x >= 0 for x in expected),
             "invalid expected census")
        need((len(figures), len(accessibility), ok_count,
              len(accessibility) - ok_count) == expected,
             "frozen R48 claim/source counts changed without independent review")

    review = []
    statuses = Counter()
    flags_count = Counter()
    url_uses = Counter()
    for ordinal, rec in enumerate(figures, start=1):
        need(type(rec) is dict and rec.get("status") in KNOWN,
             "unknown figure-triage status")
        need(all(type(rec.get(k)) is list for k in
                 ("figs", "cites", "missing", "tested_sources", "untested_sources")),
             "incomplete figure evidence fields")
        need(rec["figs"] and rec["cites"] and
             all(type(s) is str and s for s in rec["cites"] + rec["figs"]),
             "missing source/figure evidence")
        need(len(rec["figs"]) == len(set(rec["figs"])) and
             len(rec["missing"]) == len(set(rec["missing"])) and
             set(rec["missing"]).issubset(rec["figs"]),
             "invalid missing-figure census")
        slug = rec["slug"]
        need(slug in lib.articles, "orphan numeric claim")
        meta = lib.articles[slug]
        expected_tested, expected_untested = [], []
        sources = []
        for sid in rec["cites"]:
            try:
                source = lib.source_for(meta, sid)  # NEVER global lib.register
            except (KeyError, ValueError, TypeError) as exc:
                raise TriageHold("source not in original article scope: " +
                                 str(exc)) from exc
            need(type(source) is dict and type(source.get("url")) is str,
                 "original source missing URL")
            url = source["url"]
            need(url in by_url, "cited original URL omitted from accessibility table")
            url_uses[url] += 1
            access = by_url[url]
            if access["ok"]:
                expected_tested.append(sid)
            else:
                expected_untested.append(sid)
            # Do not merge same-URL variants with distinct original reading notes.
            sources.append({"source_id": sid, "original_url": url,
                            "article_source_origin": source.get("_origin", "base"),
                            "original_source_record_sha256": digest(source),
                            "accessibility_only": bool(access["ok"]),
                            "source_text_sha256": access.get("sha256"),
                            "human_source_link_checked": False,
                            "claim_supported_verified": False})
        need(Counter(rec["tested_sources"]) == Counter(expected_tested)
             and Counter(rec["untested_sources"]) == Counter(expected_untested),
             "source accessibility status inconsistent with article citation identity")
        status = rec["status"]
        missing = rec["missing"]
        if not expected_tested:
            need(status == "NO_TESTABLE_SOURCE" and not missing,
                 "blocked source incorrectly presented as figure-tested")
        else:
            need((status == "ALL_FIGURES_FOUND" and not missing) or
                 (status == "SOME_FIGURES_NOT_FOUND" and 0 < len(missing) < len(rec["figs"])) or
                 (status == "NO_FIGURES_FOUND" and len(missing) == len(rec["figs"])),
                 "figure status contradicts figure/token census")
        statuses[status] += 1
        flags = ["NUMBER_TOKEN_IS_NOT_CLAIM_OR_UNIT_VERIFICATION",
                 "HUMAN_SOURCE_AND_CONTEXT_CHECK_REQUIRED"]
        if len(set(rec["cites"])) > 1:
            flags.append("MULTIPLE_CITED_SOURCES_NEED_INDIVIDUAL_ATTRIBUTION")
        if expected_untested:
            flags.append("AT_LEAST_ONE_CITED_SOURCE_INACCESSIBLE")
        if any(by_url[s["original_url"]]["ok"] and
               not by_url[s["original_url"]].get("sha256") for s in sources):
            flags.append("ACCESSIBLE_EXTRACT_WITHOUT_RECORDED_CONTENT_SHA256")
        if missing:
            flags.append("NUMBER_TOKEN_NOT_LOCATED_NOT_NECESSARILY_CONTRADICTED")
        priority_topics = sorted(t for t, pat in TOPICS.items()
                                 if re.search(pat, rec["text"], re.I))
        if (meta.get("track") == "modern" or
                (getattr(lib, "slate", {}) or {}).get(slug, {}).get("gate") is True):
            priority_topics.append("ACTIONABLE_CONTENT_REVIEW_REQUIRED")
        flags_count.update(flags)
        review.append({
            "claim_ordinal": ordinal,
            "claim_identity_sha256": claim_key(rec),
            "slug": slug,
            "original_article_html_sha256":
                hashlib.sha256(meta["_body"].encode("utf-8")).hexdigest(),
            "original_article_track": meta["track"],
            "original_source_id_occurrences": list(rec["cites"]),
            "original_source_variants": sources,
            "figures": list(rec["figs"]),
            "machine_number_token_status_only": status,
            "missing_tokens_in_r48": list(missing),
            "human_review_priority_topics_not_findings": sorted(set(priority_topics)),
            "review_flags": flags,
            "state": HOLD,
            "source_claim_accuracy_verified": False,
            "qualified_safety_clearance": False,
            "may_publish": False,
        })

    need(set(url_uses) == set(by_url),
         "R48 source accessibility contains unbound URLs or is missing used URLs")
    result = {
        "schema_version": 1, "issue": 136, "release_state": "HOLD",
        "machine_authority": "R48_SOURCE_SCOPED_NUMBER_TOKEN_TRIAGE_ONLY",
        "source_claim_accuracy_verified": False,
        "human_source_reviews_completed": False,
        "human_source_links_verified": False,
        "qualified_safety_clearance": False,
        "independent_QD_approval": False,
        "may_publish": False,
        "counts": {
            "original_numeric_claim_blocks": len(originals),
            "original_accessibility_urls": len(by_url),
            "accessible_text_extractions_not_human_checks": ok_count,
            "unavailable_source_urls": len(by_url) - ok_count,
            "number_token_status_only": dict(sorted(statuses.items())),
            "review_flags": dict(sorted(flags_count.items())),
            "original_citation_occurrences_in_numeric_blocks":
                sum(len(r["cites"]) for r in figures),
        },
        "review_tasks": review,
        "limitations": (
            "A number anywhere in a page, including across several cited sources, "
            "does NOT verify its unit, context, exact supporting page, currency, "
            "mathematical derivation, claim accuracy, safety or accessibility to "
            "a human reviewer. R48 source access is AI-assisted machine evidence. "
            "No source or safety status is upgraded."),
    }
    result["fingerprint_sha256"] = digest(result)
    return result

def _read(path, root):
    need(path.is_file() and not path.is_symlink()
         and path.resolve(strict=True).is_relative_to(root),
         "missing, linked or outside-root evidence artifact")
    return json.loads(path.read_text(encoding="utf-8"))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--format", choices=("summary", "json"), default="summary")
    args = parser.parse_args(argv)
    try:
        root = args.repo_root.resolve(strict=True)
        modpath = root / "preparedness/tools/build.py"
        need(modpath.is_file() and not modpath.is_symlink(),
             "missing or linked original WordPress draft renderer")
        spec = importlib.util.spec_from_file_location("r49_original_draft_library", modpath)
        need(spec is not None and spec.loader is not None, "cannot load original library")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        lib = module.Library(root / "preparedness")
        docs = root / "preparedness/docs/r48"
        figures = _read(docs / "FIGURE-TRIAGE-2026-11-01.json", root)
        access = _read(docs / "SOURCE-ACCESSIBILITY-2026-11-01.json", root)
        result = audit(lib, figures, access, expected=(186, 89, 82, 7))
        if args.format == "summary":
            result = {k: v for k, v in result.items() if k != "review_tasks"}
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except (TriageHold, OSError, TypeError, ValueError, KeyError) as exc:
        print("R49 NUMERIC SOURCE TRIAGE HOLD: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
