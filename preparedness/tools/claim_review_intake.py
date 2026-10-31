#!/usr/bin/env python3
"""Preparedness R9: fingerprint-bound citation-occurrence REVIEWER REPORT intake.

Never verifies a source, reviewer identity, medical advice or publishing status.
Import R8's *actual* source-index and per-claim custody. Reviewer reports are
self-assertions, not safety clearance. No network or CMS side effects.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))  # required by python -I
import claim_occurrence_audit as r8

MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_TEXT = 4000
HEX = re.compile(r"[a-f0-9]{64}\Z")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
SOURCE_STATES = frozenset(("REACHED_SOURCE", "REDIRECTED_SOURCE", "NOT_REACHABLE", "NOT_ATTEMPTED"))
CLAIM_STATES = frozenset(("SUPPORTED_IN_INSPECTED_SCOPE", "PARTIALLY_SUPPORTED", "CONTRADICTED", "UNCERTAIN", "NOT_CHECKED"))
RISK_FLAGS = frozenset(("WATER", "FOOD", "MEDICINE", "INFANT", "POWER_CO", "FIRE", "SHELTER", "HISTORICAL_METHOD", "OTHER"))
BUNDLE_KEYS = frozenset(("schema_version", "parent_evidence_digest_sha256", "claim_responses"))
RESPONSE_KEYS = frozenset(("claim_request_sha256", "reviewer", "reviewed_on", "source_access", "observed_url", "source_locator", "claim_assessment", "proposition_quote", "evidence_basis", "reading_limits", "risk_flags"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_sha(value, name):
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(f"{name}: expected lowercase SHA256")
    return value


def plain(value, name, minimum=0, maximum=MAX_TEXT):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise ValueError(f"{name}: missing/oversized content")
    if any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise ValueError(f"{name}: control character")
    return value


def https(value, name):
    plain(value, name, 10, 2048)
    if any(ord(c) < 33 for c in value) or "\\" in value:
        raise ValueError(f"{name}: unsafe URL bytes")
    try:
        p = urlsplit(value)
        if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443) or "@" in p.netloc:
            raise ValueError("unsafe URL")
    except ValueError as ex:
        raise ValueError(f"{name}: require simple HTTPS source URL") from ex
    return value


def check_report(report: dict, *, expected_counts: dict | None = r8.BASELINE, source_rows: list[dict] | None = None) -> dict:
    """Recompute every R8 fingerprint and inventory, not just trust a manifest SHA."""
    if not isinstance(report, dict) or report.get("schema_version") != 1:
        raise ValueError("R8: unsupported report")
    if (report.get("release_state") != "HOLD" or report.get("may_publish") is not False
            or report.get("human_link_checks_documented_by_tool") != 0
            or report.get("reviewed_claim_occurrences") != 0
            or report.get("verified_citation_claims") != 0):
        raise ValueError("R8: publication/review truth gate violated")
    claims, counts = report.get("claims"), report.get("counts")
    if not isinstance(claims, list) or not isinstance(counts, dict) or not claims:
        raise ValueError("R8: empty or missing inventory")
    if expected_counts is not None and any(counts.get(k) != v for k, v in expected_counts.items()):
        raise ValueError("R8: frozen inventory baseline drift")
    if counts.get("citation_occurrences") != len(claims):
        raise ValueError("R8: occurrence count mismatch")
    physical = None
    if source_rows is not None:
        physical = {row["row_key"]: row for row in source_rows}
        if len(physical) != len(source_rows) or len(physical) != counts.get("physical_source_rows"):
            raise ValueError("R8: canonical physical source inventory drift")
        if sum(len(v) > 1 for v in r8._group_rows(source_rows).values()) != counts.get("shared_url_groups"):
            raise ValueError("R8: canonical shared-URL group drift")
    ids, seen, article_ordinals = [], {}, defaultdict(list)
    pair_ids = set()
    for c in claims:
        if not isinstance(c, dict):
            raise ValueError("R8: malformed occurrence")
        if (c.get("claim_review") != "PENDING_INDEPENDENT_HUMAN_CHECK"
                or c.get("release_state") != "HOLD" or c.get("may_publish") is not False):
            raise ValueError("R8: unsafe occurrence state")
        for k in ("claim_request_sha256", "article_evidence_sha256", "body_sha256", "context_sha256"):
            valid_sha(c.get(k), f"R8 {k}")
        for k in ("article", "source_id", "source_row_key", "source_origin", "article_source_use",
                  "contributor_claimed_support", "context_excerpt"):
            plain(c.get(k), f"R8 {k}", 1, 12000)
        https(c.get("source_url"), "R8 source URL")
        if not c["source_row_key"].startswith(c["source_origin"] + ":"):
            raise ValueError("R8: contributor source-row mismatch")
        if physical is not None:
            row = physical.get(c["source_row_key"])
            if row is None or (row["origin"], row["source_id"], row["url"], row["supports"], row.get("reading_limits")) != (
                    c["source_origin"], c["source_id"], c["source_url"], c["contributor_claimed_support"], c.get("contributor_reading_limits")):
                raise ValueError("R8: physical contributor source record has drifted")
        # Short visible contexts are wholly hash-checkable. Long excerpts need the
        # original source body: never treat a truncated excerpt as full evidence.
        if c.get("context_is_excerpt") is False:
            if r8.compact(c["context_excerpt"]) != c["context_excerpt"] or sha(c["context_excerpt"]) != c["context_sha256"]:
                raise ValueError("R8: visible claim excerpt/body hash mismatch")
        elif c.get("context_is_excerpt") is True:
            if c.get("context_chars", 0) <= 1000 or "[EXCERPT; SEE ORIGINAL BODY]" not in c["context_excerpt"]:
                raise ValueError("R8: truncated claim excerpt metadata mismatch")
        else:
            raise ValueError("R8: missing claim excerpt completeness marker")
        if not isinstance(c.get("ordinal"), int) or isinstance(c["ordinal"], bool) or c["ordinal"] < 1:
            raise ValueError("R8: malformed ordinal")
        if c.get("inherited_safety_state") not in r8.ACCEPTED_STATES:
            raise ValueError("R8: unknown inherited safety status")
        identity = {"slug": c["article"], "source_id": c["source_id"],
                    "ordinal": c["ordinal"], "source_row_key": c["source_row_key"],
                    "article_evidence_sha256": c["article_evidence_sha256"],
                    "body_sha256": c["body_sha256"], "context_sha256": c["context_sha256"],
                    "source_use_sha256": sha(c["article_source_use"]),
                    "source_support_sha256": sha(c["contributor_claimed_support"]),
                    "source_limits_sha256": sha(str(c.get("contributor_reading_limits") or ""))}
        key = c["claim_request_sha256"]
        if r8.digest(identity) != key or key in seen:
            raise ValueError("R8: altered or duplicated claim fingerprint")
        seen[key] = c
        ids.append(key)
        article_ordinals[c["article"]].append(c["ordinal"])
        pair_ids.add((c["article"], c["source_id"]))
    for a, ordinals in article_ordinals.items():
        if ordinals != list(range(1, len(ordinals) + 1)):
            raise ValueError(f"R8: missing/duplicate/out-of-order occurrence in {a}")
    if counts.get("article_source_pairs") != len(pair_ids) or counts.get("draft_items") != len(article_ordinals):
        raise ValueError("R8: article/source pair inventory drift")
    if report.get("evidence_digest_sha256") != r8.digest(ids):
        raise ValueError("R8: overall evidence digest mismatch")
    return seen


def validate_response(response: dict, request: dict, today: date) -> dict:
    if not isinstance(response, dict) or set(response) != RESPONSE_KEYS:
        raise ValueError("response: strict schema required, no approval fields")
    valid_sha(response["claim_request_sha256"], "request key")
    reviewer = plain(response["reviewer"], "reviewer label", 3, 100).strip()
    if not isinstance(response["reviewed_on"], str) or not DAY.fullmatch(response["reviewed_on"]):
        raise ValueError("response: ISO review date required")
    try:
        reviewed = date.fromisoformat(response["reviewed_on"])
    except ValueError as ex:
        raise ValueError("response: impossible date") from ex
    if reviewed > today:
        raise ValueError("response: future review date")
    source_access, claim = response["source_access"], response["claim_assessment"]
    if source_access not in SOURCE_STATES or claim not in CLAIM_STATES:
        raise ValueError("response: unsupported access/claim assessment")
    flags = response["risk_flags"]
    if not isinstance(flags, list) or not all(isinstance(x, str) and x in RISK_FLAGS for x in flags) or len(flags) != len(set(flags)):
        raise ValueError("response: invalid/duplicate risk flags")
    plain(response["evidence_basis"], "evidence basis", 20)
    plain(response["reading_limits"], "reading limitations", 12)
    locator, observed = response["source_locator"], response["observed_url"]
    if source_access in ("REACHED_SOURCE", "REDIRECTED_SOURCE"):
        https(observed, "observed source")
        plain(locator, "source section locator", 4, 400)
        if source_access == "REACHED_SOURCE" and observed != request["source_url"]:
            raise ValueError("response: moved URL must be declared redirect")
        if source_access == "REDIRECTED_SOURCE" and observed == request["source_url"]:
            raise ValueError("response: redirect without different URL")
    else:
        if observed is not None or locator != "" or claim != "NOT_CHECKED":
            raise ValueError("response: inaccessible source cannot support claim evaluation")
    quote = plain(response["proposition_quote"], "anchored proposition", 0, 240)
    if claim != "NOT_CHECKED":
        if len(quote.strip()) < 12:
            raise ValueError("response: missing claim-specific quoted proposition")
        if r8.compact(quote).casefold() not in r8.compact(request["context_excerpt"]).casefold():
            raise ValueError("response: proposition not found in original claim context excerpt")
        if source_access not in ("REACHED_SOURCE", "REDIRECTED_SOURCE"):
            raise ValueError("response: source not inspected")
    elif quote.strip():
        raise ValueError("response: unreviewed claim must not claim anchored proposition")
    follow_up = (claim != "SUPPORTED_IN_INSPECTED_SCOPE" or source_access != "REACHED_SOURCE"
                 or bool(flags) or request.get("context_is_excerpt") is True)
    return {"claim_request_sha256": response["claim_request_sha256"],
            "reviewer_label_unverified": reviewer, "reviewed_on_self_reported": response["reviewed_on"],
            "source_access_self_reported": source_access, "claim_assessment_self_reported": claim,
            "risk_flags_self_reported": sorted(flags),
            "context_truncated_requires_original": request.get("context_is_excerpt") is True,
            "triage": "FOLLOW_UP_REQUIRED" if follow_up else "SELF_REPORT_RECORDED_NOT_VERIFIED",
            "independent_link_check": False, "reviewer_authenticated": False,
            "safety_cleared": False, "may_publish": False}


def audit(report: dict, bundle: dict, *, today: date | None = None, expected_counts: dict | None = r8.BASELINE, source_rows: list[dict] | None = None) -> dict:
    indexes = check_report(report, expected_counts=expected_counts, source_rows=source_rows)
    if not isinstance(bundle, dict) or set(bundle) != BUNDLE_KEYS or bundle.get("schema_version") != 1:
        raise ValueError("response bundle: invalid schema")
    if bundle.get("parent_evidence_digest_sha256") != report["evidence_digest_sha256"]:
        raise ValueError("response bundle: stale evidence digest")
    responses = bundle.get("claim_responses")
    if not isinstance(responses, list) or len(responses) > len(indexes) * 8:
        raise ValueError("response bundle: invalid response count")
    by_claim = defaultdict(list)
    reviewer_keys = set()
    for entry in responses:
        if not isinstance(entry, dict):
            raise ValueError("response bundle: nonobject response")
        key = valid_sha(entry.get("claim_request_sha256"), "response key")
        if key not in indexes:
            raise ValueError("response bundle: stale or unknown claim occurrence")
        review = validate_response(entry, indexes[key], today or date.today())
        reviewer_key = (key, review["reviewer_label_unverified"].casefold())
        if reviewer_key in reviewer_keys:
            raise ValueError("response bundle: duplicate reviewer/occurrence submission")
        reviewer_keys.add(reviewer_key)
        by_claim[key].append(review)
    queue = []
    articles = defaultdict(lambda: {"occurrences": 0, "unreported": 0, "reviewer_reports": 0,
                                   "conflicting_reports": 0, "follow_up_occurrences": 0})
    for claim in report["claims"]:
        key, slug = claim["claim_request_sha256"], claim["article"]
        reports = sorted(by_claim[key], key=lambda x: (x["reviewer_label_unverified"].casefold(), x["reviewed_on_self_reported"]))
        assessed = {(x["source_access_self_reported"], x["claim_assessment_self_reported"]) for x in reports}
        conflicting = len(assessed) > 1
        followup = conflicting or any(x["triage"] == "FOLLOW_UP_REQUIRED" for x in reports)
        status = "DISAGREEMENT_REQUIRES_HUMAN_RECONCILIATION" if conflicting else (
            "FOLLOW_UP_REQUIRED" if followup else ("SELF_REPORTS_ONLY_NOT_VERIFIED" if reports else "PENDING_HUMAN"))
        summary = {"claim_request_sha256": key, "article": slug,
                   "ordinal": claim["ordinal"], "source_id": claim["source_id"],
                   "source_row_key": claim["source_row_key"], "source_url": claim["source_url"],
                   "status": status, "reports": reports,
                   "independent_claim_verification": False, "qualified_safety_approval": False,
                   "may_publish": False}
        queue.append(summary)
        s = articles[slug]
        s["occurrences"] += 1
        s["reviewer_reports"] += len(reports)
        s["unreported"] += not bool(reports)
        s["conflicting_reports"] += conflicting
        s["follow_up_occurrences"] += followup
    return {"schema_version": 1, "authority": "SELF_REPORTED_EDITORIAL_REVIEW_ONLY",
            "parent_evidence_digest_sha256": report["evidence_digest_sha256"],
            "response_digest_sha256": r8.digest(bundle),
            "release_state": "HOLD", "may_publish": False,
            "independent_human_source_checks_verified": 0, "qualified_safety_approvals": 0,
            "canonical_physical_source_rows_crosschecked": source_rows is not None,
            "counts": {"claim_occurrences": len(queue),
                       "distinct_occurrences_with_self_reports": sum(bool(by_claim[k]) for k in indexes),
                       "self_reported_reviews": len(responses),
                       "unreported_occurrences": sum(not bool(by_claim[k]) for k in indexes),
                       "disputed_occurrences": sum(x["status"].startswith("DISAGREEMENT") for x in queue),
                       "published_items": 0,
                       "shared_url_groups_unresolved_from_parent": report["counts"]["shared_url_groups"]},
            "articles": dict(sorted(articles.items())), "review_queue": queue}


def read_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("input missing or exceeds private review size limit")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, help="local private response file only; omit for empty HOLD queue")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tools"))
    import build, evidence_freeze, source_review_queue
    lib = build.Library(root)
    rows = source_review_queue.source_rows(root)
    report = r8.make_report(lib, rows=rows,
                            fingerprint=evidence_freeze.fingerprint, expect=r8.BASELINE)
    bundle = read_json(args.responses) if args.responses else {
        "schema_version": 1, "parent_evidence_digest_sha256": report["evidence_digest_sha256"],
        "claim_responses": []}
    result = audit(report, bundle, source_rows=rows)
    if args.json_out:
        r8.safe_export(args.json_out, json.dumps(result, ensure_ascii=False, indent=2) + "\n", root / "build")
    print(json.dumps({"release_state": "HOLD", "counts": result["counts"],
                      "response_digest_sha256": result["response_digest_sha256"]}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
