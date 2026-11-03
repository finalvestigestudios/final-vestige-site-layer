#!/usr/bin/env python3
"""R103: offline, read-only 30-collision source/citation reviewer handoff.

All source/support text is UNVERIFIED. CSV is spreadsheet-formula neutralized.
A re-sealed or edited R102 report is never accepted without independent replay.
No network, CMS, publishing, source mutations, approval ingestion or file writes.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import r102_author_scoped_collision_workorder as parent

SCHEMA = "r103-source-collision-offline-human-handoff-v1"
REVIEW = "NOT_REVIEWED"
HOLD = "HOLD"
HEADER = ("group_number", "group_sha256", "literal_source_url_NOT_VERIFIED",
          "record_kind", "record_ordinal", "selected_source_origin",
          "literal_source_id", "article_slug", "article_origin",
          "citation_ordinal", "author_source_use_or_recorded_support",
          "source_or_context_original_json_NOT_VERIFIED",
          "original_record_sha256", "human_source_review", "human_claim_review",
          "qualified_safety_review", "may_publish")
DANGEROUS = re.compile(r"^[\\s\\uFEFF\\u200B]*[=+@\\-]", re.UNICODE)


class Gate(ValueError):
    """Never silently reconcile a changed author, citation, URL or source."""


def need(ok: bool, message: str) -> None:
    if not ok:
        raise Gate(message)


def verified_parent(report: dict, independently_replayed: dict) -> None:
    """A self-consistent SHA seal is NOT a trusted provenance anchor."""
    need(type(report) is dict and type(independently_replayed) is dict
         and report == independently_replayed, "R102 independent replay mismatch")
    need(report.get("schema") == parent.SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == HOLD
         and report.get("may_publish") is False
         and report.get("may_merge") is False
         and report.get("qualified_safety_review") == REVIEW
         and report.get("source_claim_support_review") == REVIEW
         and report.get("independent_QD") == REVIEW,
         "untrusted R102 safety or release state")
    seal = report.get("sha256_seal")
    need(type(seal) is str and len(seal) == 64
         and parent.digest({k: v for k, v in report.items()
                            if k != "sha256_seal"}) == seal,
         "R102 seal mismatch")
    need(report.get("original_article_drafts") == 35
         and report.get("actual_buildable_tools") == 1
         and report.get("additional_planned_tools_not_buildable") == 5
         and report.get("literal_url_collision_groups_pending_human_review") == 30
         and type(report.get("groups")) is list
         and len(report["groups"]) == 30,
         "original full-slate/collision inventory changed")


def packet(report: dict, independently_replayed: dict) -> dict:
    """Emit complete, explicitly unapproved per-variant/per-occurrence records."""
    verified_parent(report, independently_replayed)
    groups, flat = [], []
    prior_urls = []
    cited = 0
    for index, group in enumerate(report["groups"], 1):
        url = group.get("literal_url")
        need(type(url) is str and url.startswith("https://")
             and group.get("human_review") == REVIEW
             and group.get("review_state") ==
                 "pending-human-source-and-reading-scope-review"
             and group.get("same_url_is_not_shared_claim_authority") is True,
             "literal URL or human review state changed")
        variants = group.get("variants")
        uses = group.get("author_bound_citation_contexts")
        need(type(variants) is list and len(variants) >= 2
             and group.get("variant_count") == len(variants)
             and type(uses) is list and group.get("citation_occurrences") == len(uses),
             "source variant or citation occurrence missing")
        need(group.get("citing_articles") ==
             sorted({u.get("article_slug") for u in uses}),
             "citing article roster differs from original occurrences")
        variant_keys = [(v.get("origin"), v.get("source_id")) for v in variants]
        need(all(type(a) is str and a and type(b) is str and b
                 for a,b in variant_keys)
             and len(set(variant_keys)) == len(variant_keys),
             "same URL variants silently aliased")
        group_hash = parent.digest(group)
        rows = []
        for n, v in enumerate(variants, 1):
            original_json = parent.canonical(v)
            row = {
                "group_number": index, "group_sha256": group_hash,
                "literal_source_url_NOT_VERIFIED": url, "record_kind": "SOURCE_VARIANT",
                "record_ordinal": n, "selected_source_origin": v["origin"],
                "literal_source_id": v["source_id"], "article_slug": "",
                "article_origin": "", "citation_ordinal": "",
                "author_source_use_or_recorded_support":
                    v.get("supports_as_recorded_not_independently_verified") or "",
                "source_or_context_original_json_NOT_VERIFIED": original_json,
                "original_record_sha256": parent.digest(v),
                "human_source_review": REVIEW, "human_claim_review": REVIEW,
                "qualified_safety_review": REVIEW, "may_publish": False
            }
            need(row["original_record_sha256"] == parent.digest(
                json.loads(original_json)), "original source record corrupted")
            rows.append(row)
        seen_cites = set()
        for n, u in enumerate(uses, 1):
            key = (u.get("article_slug"), u.get("citation_ordinal_in_article"))
            need(key not in seen_cites
                 and (u.get("selected_source_origin"),
                      u.get("source_id_as_authored")) in variant_keys
                 and type(u.get("author_scoped_source_use")) is str
                 and u["author_scoped_source_use"].strip()
                 and parent.digest(u["author_scoped_source_use"]) ==
                     u.get("author_scoped_source_use_sha256")
                 and parent.digest(u.get("proximity_excerpt_not_claim_verification")) ==
                     u.get("proximity_sha256")
                 and u.get("existing_article_safety_state_without_new_approval") in
                     ("pending", "approved", "not-required"),
                 "authored citation, source identity or reading-depth drift")
            seen_cites.add(key)
            original_json = parent.canonical(u)
            rows.append({
                "group_number": index, "group_sha256": group_hash,
                "literal_source_url_NOT_VERIFIED": url,
                "record_kind": "CITATION_OCCURRENCE", "record_ordinal": n,
                "selected_source_origin": u["selected_source_origin"],
                "literal_source_id": u["source_id_as_authored"],
                "article_slug": u["article_slug"],
                "article_origin": u["article_origin"],
                "citation_ordinal": u["citation_ordinal_in_article"],
                "author_source_use_or_recorded_support":
                    u["author_scoped_source_use"],
                "source_or_context_original_json_NOT_VERIFIED": original_json,
                "original_record_sha256": parent.digest(u),
                "human_source_review": REVIEW, "human_claim_review": REVIEW,
                "qualified_safety_review": REVIEW, "may_publish": False
            })
        groups.append({"group_number": index, "group_sha256": group_hash,
                       "literal_url_NOT_VERIFIED": url,
                       "variant_count": len(variants),
                       "citation_occurrences": len(uses),
                       "rows": rows, "human_review": REVIEW,
                       "may_publish": False})
        flat.extend(rows)
        cited += len(uses)
        prior_urls.append(url)
    need(prior_urls == sorted(set(prior_urls))
         and cited == report.get("collision_citation_occurrences"),
         "same URL ordering, uniqueness or citation census changed")
    result = {
        "schema": SCHEMA, "issue": 136, "release_state": HOLD,
        "may_publish": False, "may_merge": False,
        "human_source_and_claim_review": REVIEW,
        "qualified_safety_review": REVIEW, "independent_QD": REVIEW,
        "browser_and_wordpress_QA": REVIEW,
        "r102_corpus_sha256": report["sha256_seal"],
        "original_35_articles_1_buildable_tool": True,
        "missing_planned_tools": 5,
        "literal_url_groups": len(groups),
        "collision_citation_occurrences": cited,
        "variant_rows": sum(g["variant_count"] for g in groups),
        "rows_total": len(flat),
        "groups": groups
    }
    result["sha256_seal"] = parent.digest(result)
    return result


def neutralize(value: object) -> str:
    """Visible spreadsheet literal, never executable formula, even after whitespace."""
    if value is None:
        return ""
    text = str(value)
    return "'" + text if DANGEROUS.match(text) or text.startswith(("\t", "\r", "\n")) else text


def csv_text(workorder: dict, kind: str) -> str:
    need(kind in ("SOURCE_VARIANT", "CITATION_OCCURRENCE"), "invalid CSV kind")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=HEADER, quoting=csv.QUOTE_ALL,
                            extrasaction="raise", lineterminator="\r\n")
    writer.writeheader()
    for group in workorder["groups"]:
        for row in group["rows"]:
            if row["record_kind"] == kind:
                writer.writerow({key: neutralize(row[key]) for key in HEADER})
    return stream.getvalue()


def html_text(workorder: dict) -> str:
    """Self-contained print-safe noninteractive evidence; no external loads."""
    esc = lambda value: html.escape(str(value), quote=True)
    bits = [
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'\">",
        "<title>R103 PRIVATE HOLD — same-URL evidence review</title>",
        "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:70rem;margin:auto;padding:1rem;color:#111;background:#fff}",
        "section{border-top:3px solid #333;margin:2rem 0;padding:1rem 0;break-before:page}",
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #888;padding:.8rem}",
        ".hold{font-weight:700;border:3px solid #111;padding:1rem}",
        "@media print{body{max-width:none}section{break-before:page}pre{white-space:pre-wrap}}",
        "</style></head><body>",
        "<header><h1>Preparedness Archive: shared-source human review workorders</h1>",
        "<p class=\"hold\">PRIVATE DRAFT — HOLD. No source or claim has been approved here. No clinical, emergency-safety or QD clearance. Do not publish or merge.</p>",
        "<p>Original reading notes and source statements are unverified assertions preserved for human checking. Repeated URLs do not prove shared claim support. No links, scripts, trackers, downloads, forms or network requests are embedded.</p>",
        "<p>Full-corpus R102 fingerprint: <code>" + esc(workorder["r102_corpus_sha256"]) + "</code>. R103 fingerprint: <code>" + esc(workorder["sha256_seal"]) + "</code>.</p></header>"
    ]
    for group in workorder["groups"]:
        bits.append("<section><h2>Group " + str(group["group_number"]) +
                    " of " + str(workorder["literal_url_groups"]) + "</h2>")
        bits.append("<p><b>Literal URL (unverified, not a clickable link):</b> <code>" +
                    esc(group["literal_url_NOT_VERIFIED"]) + "</code></p>")
        bits.append("<p>Group SHA-256: <code>" + esc(group["group_sha256"]) +
                    "</code>; author variants: " + str(group["variant_count"]) +
                    "; actual citation occurrences: " +
                    str(group["citation_occurrences"]) + ".</p>")
        for row in group["rows"]:
            heading = ("Distinct source variant" if row["record_kind"] == "SOURCE_VARIANT"
                       else "Original authored citation occurrence")
            bits.append("<h3>" + heading + " " + str(row["record_ordinal"]) + "</h3>")
            if row["article_slug"]:
                bits.append("<p>Article: <code>" + esc(row["article_slug"]) +
                            "</code>; author origin: <code>" +
                            esc(row["article_origin"]) + "</code>; citation ordinal: " +
                            str(row["citation_ordinal"]) + "</p>")
            bits.append("<p>Origin: <code>" + esc(row["selected_source_origin"]) +
                        "</code>; source ID: <code>" + esc(row["literal_source_id"]) +
                        "</code>; original record SHA-256: <code>" +
                        esc(row["original_record_sha256"]) + "</code></p>")
            bits.append("<pre>" +
                        esc(row["source_or_context_original_json_NOT_VERIFIED"]) +
                        "</pre>")
        bits.append("<p class=\"hold\">Human review still required: verify exact source edition and live URL, inspect the specific passage and each author-scoped claim, document contradictions, and obtain qualified review for high-consequence instructions. No automated approval.</p></section>")
    bits.append("</body></html>")
    return "\n".join(bits)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("html", "variants-csv", "citations-csv",
                                              "summary-json"), default="summary-json")
    args = parser.parse_args(argv)
    lib = build.Library()
    baseline = parent.workorder(lib)
    result = packet(baseline, parent.workorder(build.Library()))
    if args.format == "html":
        sys.stdout.write(html_text(result))
    elif args.format.endswith("-csv"):
        kind = "SOURCE_VARIANT" if args.format == "variants-csv" else "CITATION_OCCURRENCE"
        sys.stdout.write(csv_text(result, kind))
    else:
        sys.stdout.write(json.dumps({k: v for k, v in result.items() if k != "groups"},
                                    indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Gate, parent.Hold, ValueError, KeyError, TypeError) as exc:
        print("R103 PRIVATE HOLD: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
