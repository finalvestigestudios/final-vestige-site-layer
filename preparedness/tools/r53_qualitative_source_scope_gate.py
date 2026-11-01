#!/usr/bin/env python3
"""R53: source-scoped work orders for every R13 high-consequence action block.

This is an offline, read-only MACHINE triage. It cannot assess whether a source
supports a claim, whether advice is safe, or whether a human performed a review.
An article's historical safety-review metadata is never a qualified clearance.
Never resolve same-URL contributor readings or historical 403s automatically.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = (36, 779, 237, 542, 15, 25)
FALSE_FLAGS = ("may_publish", "qualified_safety_clearance",
               "independent_QD_approval", "human_source_links_verified")
HOLD = "PENDING_INDEPENDENT_CLAIM_SOURCE_SCOPE_AND_SAFETY_REVIEW"


class QualitativeHold(ValueError):
    """Original action/source/safety evidence disagreed; preserve release HOLD."""


def need(condition, why):
    if not condition:
        raise QualitativeHold(why)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()


def module(name, filename):
    """Explicit sibling loading works under python -I, without sys.path trust."""
    path = Path(__file__).with_name(filename)
    need(path.is_file() and not path.is_symlink(), "missing gate: " + filename)
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None,
         "cannot load original gate: " + filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def audit(lib, triage, safety, *, expected=DEFAULT):
    """Build a lossless source-scope queue; only an independent reviewer can clear it.

    expected permits smaller, explicitly bounded synthetic test corpora. The
    production CLI always pins the frozen 36/779/237/542/15/25 census.
    All original article/source pins are additionally checked by existing gates.
    """
    need(type(expected) is tuple and len(expected) == 6
         and all(type(n) is int and n >= 0 for n in expected),
         "invalid independently declared census")
    items, flags, uncited, cited, incidents, blocked = expected
    r13 = module("r53_original_r13", "high_consequence_claim_triage.py")
    need(type(triage) is dict and type(safety) is dict,
         "missing source/action or safety report")
    need(triage.get("triage_digest_sha256") ==
         digest({k: v for k, v in triage.items() if k != "triage_digest_sha256"}),
         "R13 report fingerprint invalid")
    need(safety.get("fingerprint_sha256") ==
         digest({k: v for k, v in safety.items() if k != "fingerprint_sha256"}),
         "R50 report fingerprint invalid")
    need(triage.get("release_state") == safety.get("release_state") == "HOLD"
         and triage.get("may_publish") is False
         and triage.get("independent_human_source_checks_verified") is False
         and triage.get("qualified_safety_approvals") == 0
         and triage.get("no_citation_is_proof_of_accuracy") is True
         and triage.get("regex_heuristics_have_false_negatives") is True,
         "original machine triage review authority compromised")
    need(safety.get("schema") == "r50-safety-exception-lineage-v1"
         and safety.get("issue") == 136
         and safety.get("claim_accuracy_verified") is False
         and all(safety.get(k) is False for k in FALSE_FLAGS),
         "R50 safety/publication authority compromised")
    need(safety.get("counts", {}).get("open_incidents") == incidents
         and safety.get("counts", {}).get("historically_blocked_sources") == blocked,
         "open safety-incident or historic inaccessible-source census changed")
    need(len(lib.articles) == items, "original article/tool inventory changed")
    variants = getattr(lib, "source_variants", {})
    need(type(variants) is dict, "missing contributor-specific source variants")
    all_urls = []
    for sid, records in variants.items():
        need(type(sid) is str and type(records) is list and records,
             "missing or invalid original source variants")
        seen_origins, urls = set(), set()
        for record in records:
            need(type(record) is dict and record.get("id") == sid
                 and type(record.get("_origin")) is str
                 and record["_origin"] and record["_origin"] not in seen_origins
                 and type(record.get("url")) is str
                 and record["url"].startswith("https://"),
                 "changed, ambiguous or unsafe contributor source variant")
            seen_origins.add(record["_origin"])
            urls.add(record["url"])
            all_urls.append(record["url"])
        need(len(urls) == 1, "same ID has conflicting original source URLs")
    if expected == DEFAULT:
        need(len(all_urls) == 224 and len(set(all_urls)) == 186
             and len(getattr(lib, "crosswalk_groups", {})) == 30,
             "224 original records / 186 URLs / 30 shared groups not preserved")

    # Recompute the R13 triage from the actual original article bodies; a
    # self-repinned altered report must not substitute for original visible text.
    actual = r13.build_triage(lib, expected_items=items)
    need(triage == actual, "R13 visible action work-order evidence drift")
    need(triage.get("triaged_blocks") == flags
         and triage.get("without_same_block_citation") == uncited
         and flags - uncited == cited,
         "high-consequence action / uncited / cited census changed")
    if expected == DEFAULT:
        need(sum(row["visible_block_citation_occurrences"] for row in triage["articles"]) == 1959,
             "1,959 visible source citation occurrences not preserved")
        original_source_pairs = 0
        fallback_pairs = 0
        for slug, meta in lib.articles.items():
            source_ids = set(r13.CITES.findall(meta["_body"]))
            original_source_pairs += len(source_ids)
            for sid in source_ids:
                try:
                    source = lib.source_for(meta, sid)
                except (KeyError, ValueError, TypeError) as exc:
                    raise QualitativeHold("missing source in original claim crosswalk") from exc
                if (getattr(lib, "article_origins", {}).get(slug, "base") != "base"
                        and source.get("_origin", "base") == "base"):
                    fallback_pairs += 1
        need(original_source_pairs == 367 and fallback_pairs == 43,
             "367 original article/source relationships or 43 base fallbacks lost")

    open_sx = safety.get("open_incidents")
    need(type(open_sx) is list and len(open_sx) == incidents,
         "missing open safety exceptions")
    ids = set()
    for sx in open_sx:
        need(type(sx) is dict and type(sx.get("id")) is str
             and sx["id"] not in ids and sx.get("state") == "HOLD"
             and sx.get("severity") in ("HIGH", "MEDIUM", "LOW"),
             "missing, duplicated or falsely closed safety incident")
        ids.add(sx["id"])
    blockers = safety.get("unresolved_source_access")
    need(type(blockers) is list and len(blockers) == blocked,
         "historic machine-blocked source evidence lost")
    blocked_by_id = {}
    for record in blockers:
        need(type(record) is dict and type(record.get("source_id")) is str
             and record["source_id"] not in blocked_by_id
             and record.get("review_state") == "HOLD"
             and record.get("human_link_check_complete") is False
             and type(record.get("original_variants")) is list
             and record["original_variants"],
             "historic source failure silently cleared or duplicated")
        blocked_by_id[record["source_id"]] = record

    orders, counts, source_use_count = [], Counter(), Counter()
    for article in triage["articles"]:
        slug = article["slug"]
        need(slug in lib.articles, "missing article associated with machine triage")
        meta = lib.articles[slug]
        need(meta.get("slug") == slug and
             meta.get("status", {}).get("publish") == "draft",
             "non-draft or misidentified article")
        original = meta["_body"]
        original_sha = hashlib.sha256(original.encode("utf-8")).hexdigest()
        need(original_sha == article["body_sha256"],
             "original article body/source identity drift")
        blocks = r13.scan_html(original)
        for flag in article["flags"]:
            ordinal = flag["block_ordinal"]
            need(type(ordinal) is int and 0 < ordinal <= len(blocks),
                 "invalid visible action block ordinal")
            block = blocks[ordinal - 1]
            raw_cites = list(block["citations"])  # preserve repeated occurrences
            need(flag["flag_sha256"] ==
                 digest({k: v for k, v in flag.items() if k != "flag_sha256"})
                 and flag["article"] == slug
                 and flag["source_body_sha256"] == original_sha
                 and flag["block_tag"] == block["tag"]
                 and flag["citation_occurrences_in_same_block"] == len(raw_cites)
                 and flag["source_ids_in_same_block"] == list(dict.fromkeys(raw_cites))
                 and flag["excerpt"] == block["text"][:r13.MAX_NOTE_LENGTH]
                 and flag["review_state"] == r13.STATUS,
                 "source-occurrence or original claim text changed")
            readings = []
            for sid in dict.fromkeys(raw_cites):
                need(type(meta.get("source_use", {}).get(sid)) is str
                     and meta["source_use"][sid].strip(),
                     "missing original article-specific source-use note: " + sid)
                try:
                    source = lib.source_for(meta, sid)
                except (KeyError, TypeError, ValueError) as exc:
                    raise QualitativeHold("article-source scope missing: " + slug + "/" + sid) from exc
                need(type(source) is dict and source.get("id") == sid
                     and type(source.get("url")) is str
                     and source["url"].startswith("https://")
                     and type(source.get("_origin", "base")) is str,
                     "invalid original scoped source record")
                url = source["url"]
                variant_digest = digest(source)
                prior = blocked_by_id.get(sid)
                if prior:
                    need(any(x.get("origin") == source.get("_origin", "base")
                             and x.get("url") == url
                             and x.get("original_source_sha256") == variant_digest
                             for x in prior["original_variants"]),
                         "historically blocked original source variant changed")
                source_origins = getattr(lib, "article_origins", {})
                article_origin = source_origins.get(slug, "base")
                is_fallback = source.get("_origin", "base") == "base" and article_origin != "base"
                shared = url in getattr(lib, "crosswalk_groups", {})
                readings.append({
                    "source_id": sid,
                    "citation_occurrences_in_block": raw_cites.count(sid),
                    "original_url": url,
                    "article_contributor_origin": article_origin,
                    "source_contributor_origin": source.get("_origin", "base"),
                    "original_source_record_sha256": variant_digest,
                    "original_source_use": meta["source_use"][sid],
                    "original_source_reading_scope": source.get("notes", ""),
                    "original_source_supports_note": source.get("supports", ""),
                    "shared_url_group_requires_human_review": shared,
                    "base_fallback_requires_human_review": is_fallback,
                    "historically_machine_inaccessible_source_id": bool(prior),
                    "independent_source_scope_verified": False,
                    "human_source_link_checked": False,
                    "claim_supported_by_source_verified": False,
                })
                counts["historically_blocked_source_uses"] += bool(prior)
                counts["shared_url_source_uses"] += shared
                counts["fallback_source_uses"] += is_fallback
                source_use_count[(slug, sid, source.get("_origin", "base"))] += 1
            priority = ("HIGH_MACHINE_REVIEW_PRIORITY" if
                        not raw_cites or "medical-dependency" in flag["risk_families"]
                        or "vulnerable-households" in flag["risk_families"]
                        or any(r["historically_machine_inaccessible_source_id"] for r in readings)
                        else "STANDARD_MACHINE_REVIEW_PRIORITY")
            key = {"slug": slug, "block_ordinal": ordinal,
                   "original_article_html_sha256": original_sha,
                   "original_R13_flag_sha256": flag["flag_sha256"],
                   "citation_source_id_occurrences": raw_cites}
            order = {
                "work_order_id_sha256": digest(key),
                "article": slug, "block_ordinal": ordinal,
                "original_article_html_sha256": original_sha,
                "original_R13_flag_sha256": flag["flag_sha256"],
                "block_tag": flag["block_tag"],
                "risk_families_machine_flags": flag["risk_families"],
                "machine_priority_not_safety_diagnosis": priority,
                "excerpt_not_factually_verified": flag["excerpt"],
                "excerpt_truncated": flag["excerpt_truncated"],
                "citation_source_id_occurrences": raw_cites,
                "source_readings_in_article_scope": readings,
                "uncited_in_same_visible_block": not raw_cites,
                "article_historical_safety_review_state_not_qualified_approval":
                    meta.get("safety_review", {}).get("state", "unknown"),
                "claim_support_verified": False,
                "qualified_safety_clearance": False,
                "independent_QD_approval": False,
                "may_publish": False,
                "review_state": HOLD,
            }
            orders.append(order)
            counts["uncited_action_blocks" if not raw_cites else "cited_action_blocks"] += 1
            counts["citation_occurrences_within_flagged_blocks"] += len(raw_cites)
            counts[priority] += 1
    need(len(orders) == flags and counts["uncited_action_blocks"] == uncited
         and counts["cited_action_blocks"] == cited
         and len({o["work_order_id_sha256"] for o in orders}) == flags,
         "lost, duplicated, or falsely deduplicated visible action work orders")
    counts["distinct_article_source_reading_uses_in_flags"] = len(source_use_count)
    counts["unresolved_historic_source_ids"] = len(blocked_by_id)
    counts["open_safety_exceptions"] = len(open_sx)
    out = {
        "schema": "r53-qualitative-source-scoped-human-review-queue-v1",
        "issue": 136, "release_state": "HOLD", "may_publish": False,
        "qualified_safety_clearance": False, "independent_QD_approval": False,
        "human_source_links_verified": False, "claim_accuracy_verified": False,
        "machine_authority": "R13_HEURISTIC_RETRIAGE_PLUS_ORIGINAL_CONTRIBUTOR_SOURCE_SCOPE",
        "counts": dict(sorted(counts.items())),
        "article_count": items,
        "work_orders": orders,
        "open_safety_incidents": [{"id": x["id"], "severity": x["severity"],
                                   "state": "HOLD"} for x in open_sx],
        "blocked_historical_source_ids_not_current_link_failures": sorted(blocked_by_id),
        "original_R13_triage_sha256": triage["triage_digest_sha256"],
        "original_R50_safety_sha256": safety["fingerprint_sha256"],
        "limitations": (
            "Heuristic regex has false negatives and false positives. A citation "
            "or numeric token does not prove factual support, safety, freshness, "
            "reading depth, an independent human review or QD clearance. "
            "Historical machine access failures are not current access claims. "
            "This is a HOLD work order, not a clinical recommendation."),
    }
    out["fingerprint_sha256"] = digest(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=ROOT.parent)
    ap.add_argument("--summary", action="store_true",
                    help="Print only counts/flags, not all private review work orders")
    opts = ap.parse_args(argv)
    try:
        root = opts.repo_root.resolve(strict=True)
        tools = root / "preparedness" / "tools"
        build = module("r53_build", "build.py")
        r13 = module("r53_action", "high_consequence_claim_triage.py")
        r50 = module("r53_safety", "safety_exception_custody_gate.py")
        lib = build.Library(root / "preparedness")
        doc = root / "preparedness" / "docs" / "r48"
        md = doc / "SAFETY-EXCEPTION-REGISTER-2026-11-01.md"
        need(md.is_file() and not md.is_symlink(), "missing original incident register")
        candidates = r50._json(doc / "SAFETY-CANDIDATES-2026-11-01.json", root)
        safety = r50.audit(lib, md.read_text(encoding="utf-8"), candidates)
        triage = r13.build_triage(lib)
        result = audit(lib, triage, safety)
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if opts.summary:
            result = {k: v for k, v in result.items() if k != "work_orders"}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (QualitativeHold, OSError, ValueError, TypeError, KeyError, ImportError) as exc:
        print("R53 QUALITATIVE SOURCE REVIEW HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
