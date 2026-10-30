#!/usr/bin/env python3
"""Offline, read-only comparison of *unverified* Preparedness reviewer reports.

This tool makes differences in multiple self-reported source reviews visible. It
cannot authenticate reviewers, establish independent source inspection, approve
safety advice, change the citation crosswalk or authorize publication. Its output
is always HOLD. Digest bindings detect accidental edits, NOT deliberate forgery.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_receipts as receipts
import review_response_audit as intake

MAX_BUNDLES = 64
MAX_LABEL = 200
MAX_PREVIOUS_BYTES = 2 * 1024 * 1024
REPORT_SCHEMA = 1
ALL_CITATION_FLAGS = ("link_check", "observed_url", "source_locator", "claim_check", "risk_flags")
ALL_GROUP_FLAGS = ("relationship", "row_reading_status", "row_source_locator")


def normalized_reviewer(value: object) -> str:
    """Prevent *obvious* label duplication; names are NOT verified identities."""
    intake.require_text(value, "reviewer label", minimum=3)
    text = unicodedata.normalize("NFKC", value)
    if any(unicodedata.category(char).startswith("C") for char in text):
        raise ValueError("reviewer label contains invisible/control character")
    text = " ".join(text.split()).casefold()
    if not 3 <= len(text) <= MAX_LABEL:
        raise ValueError("reviewer label too short/long after normalization")
    return text


def require_manifest_references(manifest: dict) -> tuple[dict, dict]:
    """Verify all shared-URL packet links are actually in the citation inventory.

    The upstream intake validates each SHA independently. This additional
    crosswalk gate also detects a signed-looking manifest with missing, shifted,
    duplicated or foreign cross-references.
    """
    citations, groups = intake.validate_manifest(manifest)
    linked: set[str] = set()
    grouped_urls: set[str] = set()
    for key, group in groups.items():
        url = group["url"]
        if url in grouped_urls:
            raise ValueError("shared URL packet duplicates source URL")
        grouped_urls.add(url)
        records = group.get("citations")
        if not isinstance(records, list) or not records:
            raise ValueError("shared URL packet has no citation references")
        physical = group["all_source_row_keys"]
        cited_rows = group.get("cited_source_row_keys")
        uncited_rows = group.get("uncited_source_row_keys")
        if (not isinstance(cited_rows, list) or not isinstance(uncited_rows, list)
                or len(cited_rows) != len(set(cited_rows))
                or len(uncited_rows) != len(set(uncited_rows))
                or set(physical) != set(cited_rows) | set(uncited_rows)
                or set(cited_rows) & set(uncited_rows)):
            raise ValueError("shared URL physical row partition does not match packet")
        actual_rows: set[str] = set()
        for reference in records:
            if not isinstance(reference, dict):
                raise ValueError("shared URL packet reference must be an object")
            ref = intake.require_sha(reference.get("review_request_sha256"), "linked citation")
            citation = citations.get(ref)
            if ref in linked or citation is None or citation.get("url") != url or citation.get("shared_url") is not True:
                raise ValueError("shared URL packet links foreign or duplicate citation")
            if (reference.get("article") != citation.get("article")
                    or reference.get("source_id") != citation.get("source_id")
                    or reference.get("source_row_key") != citation.get("source_row_key")
                    or reference.get("article_claim_scope") != citation.get("article_claim_scope")
                    or reference.get("contributor_claim_scope") != citation.get("contributor_claim_scope")
                    or reference.get("contributor_reading_limits") != citation.get("contributor_reading_limits")):
                raise ValueError("shared URL packet linked claim/scope differs from citation")
            actual_rows.add(citation["source_row_key"])
            linked.add(ref)
        if actual_rows != set(cited_rows):
            raise ValueError("shared URL packet cited physical rows differ from linked claims")
    if linked != {ref for ref, c in citations.items() if c.get("shared_url") is True}:
        raise ValueError("shared URL packet omitted or added shared citation")
    if any(c.get("shared_url") is True and c["url"] not in grouped_urls for c in citations.values()):
        raise ValueError("shared citation URL has no packet")
    return citations, groups


def _canonical_record(row: dict, *, field: str) -> dict:
    """Array order is not evidence; preserve all material content before hashing."""
    copy = dict(row)
    if field == "packet_sha256":
        copy["row_reviews"] = sorted(row["row_reviews"], key=lambda x: x["source_row_key"])
    return copy


def _record_digest(row: dict, field: str) -> str:
    return receipts.digest(_canonical_record(row, field=field))


def _bundle_digest(bundle: dict) -> str:
    canonical = dict(bundle)
    canonical["citation_responses"] = sorted(
        (_canonical_record(row, field="review_request_sha256") for row in bundle["citation_responses"]),
        key=lambda row: row["review_request_sha256"])
    canonical["shared_url_responses"] = sorted(
        (_canonical_record(row, field="packet_sha256") for row in bundle["shared_url_responses"]),
        key=lambda row: row["packet_sha256"])
    return receipts.digest(canonical)


def _compare_citation(records: list[dict], request_id: str) -> dict:
    n = len(records)
    flags: set[str] = set()
    link = {r["link_check"] for r in records}
    urls = {r["observed_url"] for r in records}
    scopes = {r["source_locator"].strip() for r in records}
    claims = {r["claim_check"] for r in records}
    risks = {tuple(sorted(r["risk_flags"])) for r in records}
    if len(link) > 1:
        flags.add("link_check")
    if len(urls) > 1:
        flags.add("observed_url")
    if len(scopes) > 1:
        flags.add("source_locator")
    if len(claims) > 1:
        flags.add("claim_check")
    if len(risks) > 1:
        flags.add("risk_flags")
    any_followup = any(r["link_check"] != "REACHED_SOURCE"
                       or r["claim_check"] != "SUPPORTED_IN_INSPECTED_SCOPE"
                       or bool(r["risk_flags"]) for r in records)
    if n == 0:
        state = "PENDING_HUMAN_INPUT"
    elif n == 1:
        state = "SINGLE_SELF_REPORT_UNVERIFIED"
    elif flags:
        state = "DISAGREEMENT_ESCALATE"
    elif any_followup:
        state = "FOLLOW_UP_ESCALATE"
    else:
        state = "MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED"
    return {
        "review_request_sha256": request_id,
        "reports_received": n,
        "unverified_reviewer_labels": n,
        "state": state,
        "disagreement_dimensions": sorted(flags),
        "risk_flags_reported_union": sorted({flag for r in records for flag in r["risk_flags"]}),
        "follow_up_required_by_any_report": any_followup,
        "input_record_sha256": sorted(_record_digest(r, "review_request_sha256") for r in records),
        "reviewer_identity_authenticated": False,
        "source_link_independently_verified": False,
        "claim_independently_verified": False,
        "safety_approved": False,
    }


def _compare_group(records: list[dict], group: dict, citations: dict) -> dict:
    n = len(records)
    diffs: set[str] = set()
    kinds = {r["relationship"] for r in records}
    if len(kinds) > 1:
        diffs.add("relationship")
    expected = set(group["all_source_row_keys"])
    for key in expected:
        statuses = {next(x for x in r["row_reviews"] if x["source_row_key"] == key)["reading_status"]
                    for r in records}
        locators = {next(x for x in r["row_reviews"] if x["source_row_key"] == key)["source_locator"].strip()
                    for r in records}
        if len(statuses) > 1:
            diffs.add("row_reading_status")
        if len(locators) > 1:
            diffs.add("row_source_locator")
    requires_followup = any(r["relationship"] != "CONSISTENT_LIMITED_SCOPES"
                            or any(x["reading_status"] != "INSPECTED" for x in r["row_reviews"])
                            for r in records)
    dependencies = [citations[x["review_request_sha256"]] for x in group["citations"]]
    missing_second = sum(c["reports_received"] < 2 for c in dependencies)
    dependent_flags = sum(c["state"] not in ("MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED",)
                          for c in dependencies)
    if n == 0:
        state = "PENDING_HUMAN_INPUT"
    elif n == 1:
        state = "SINGLE_SELF_REPORT_UNVERIFIED"
    elif diffs:
        state = "DISAGREEMENT_ESCALATE"
    elif requires_followup:
        state = "FOLLOW_UP_ESCALATE"
    elif dependent_flags:
        state = "CITATION_DEPENDENCY_HOLD"
    else:
        state = "MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED"
    return {
        "packet_sha256": group["packet_sha256"],
        "reports_received": n,
        "unverified_reviewer_labels": n,
        "state": state,
        "disagreement_dimensions": sorted(diffs),
        "follow_up_required_by_any_report": requires_followup,
        "cited_claims_missing_second_report": missing_second,
        "cited_claims_not_self_report_aligned": dependent_flags,
        "input_record_sha256": sorted(_record_digest(r, "packet_sha256") for r in records),
        "reviewer_identity_authenticated": False,
        "source_scope_independently_reconciled": False,
        "crosswalk_review_state_changed": False,
        "safety_approved": False,
    }


def verify_previous(previous: dict, current: dict) -> None:
    """An optional local prior snapshot prevents silently deleting old findings.

    Digests here are integrity checks, not signatures; a malicious operator can
    forge them, so this is not independent review.
    """
    if not isinstance(previous, dict) or previous.get("schema_version") != REPORT_SCHEMA:
        raise ValueError("previous audit: incompatible schema")
    old_sha = previous.get("audit_sha256")
    if old_sha != receipts.digest({k: v for k, v in previous.items() if k != "audit_sha256"}):
        raise ValueError("previous audit: digest mismatch")
    if (previous.get("manifest_sha256") != current["manifest_sha256"]
            or previous.get("release_state") != "HOLD" or previous.get("may_publish") is not False):
        raise ValueError("previous audit: corpus binding or HOLD state changed")
    for field, identity in (("citations", "review_request_sha256"),
                            ("shared_url_packets", "packet_sha256")):
        before, after = previous.get(field), current[field]
        if not isinstance(before, list) or len(before) != len(after):
            raise ValueError("previous audit: review inventory changed")
        prior_index = {}
        for row in before:
            if not isinstance(row, dict) or row.get(identity) in prior_index:
                raise ValueError("previous audit: duplicate/malformed request")
            prior_index[row[identity]] = row
        for row in after:
            old = prior_index.get(row[identity])
            if old is None:
                raise ValueError("previous audit: request identity changed")
            old_inputs = old.get("input_record_sha256")
            new_inputs = row["input_record_sha256"]
            if (not isinstance(old_inputs, list) or not all(isinstance(x, str) and intake.HEX.fullmatch(x) for x in old_inputs)
                    or not set(old_inputs).issubset(new_inputs)):
                raise ValueError("previous audit: previously recorded review disappeared or was edited")


def audit_discrepancies(manifest: dict, bundles: list[dict], *, today: date | None = None,
                        previous: dict | None = None) -> dict:
    """Cross-check valid review inputs without granting any independent approval."""
    if not isinstance(bundles, list) or not 1 <= len(bundles) <= MAX_BUNDLES:
        raise ValueError("response bundles: require 1 to 64 independently prepared files")
    citations, groups = require_manifest_references(manifest)
    seen_bundles: set[str] = set()
    citation_records: dict[str, list[dict]] = defaultdict(list)
    group_records: dict[str, list[dict]] = defaultdict(list)
    reviewer_by_request: dict[tuple[str, str], set[str]] = defaultdict(set)
    for bundle in bundles:
        # This fully validates individual response records with the established
        # fail-closed intake, including dates, URLs, all physical group rows.
        intake.audit(manifest, bundle, today=today)
        bsha = _bundle_digest(bundle)
        if bsha in seen_bundles:
            raise ValueError("duplicate response bundle")
        seen_bundles.add(bsha)
        for key, field, store in (("citation_responses", "review_request_sha256", citation_records),
                                  ("shared_url_responses", "packet_sha256", group_records)):
            for row in bundle[key]:
                normalized = normalized_reviewer(row["reviewer"])
                request = (key, row[field])
                if normalized in reviewer_by_request[request]:
                    raise ValueError("duplicate self-reported reviewer label for same request")
                reviewer_by_request[request].add(normalized)
                store[row[field]].append(row)
    cited = {key: _compare_citation(citation_records[key], key) for key in sorted(citations)}
    shared = {key: _compare_group(group_records[key], groups[key], cited) for key in sorted(groups)}
    citation_rows = list(cited.values())
    group_rows = list(shared.values())
    all_rows = citation_rows + group_rows
    counts = {
        "response_bundles": len(bundles),
        "citation_requests": len(cited),
        "citation_self_reports": sum(c["reports_received"] for c in citation_rows),
        "citation_requests_with_fewer_than_two_reports": sum(c["reports_received"] < 2 for c in citation_rows),
        "shared_url_packets": len(shared),
        "shared_url_self_reports": sum(g["reports_received"] for g in group_rows),
        "shared_url_packets_with_fewer_than_two_reports": sum(g["reports_received"] < 2 for g in group_rows),
        "disagreements_requiring_human_review": sum(c["state"] == "DISAGREEMENT_ESCALATE" for c in all_rows),
        "followup_and_dependency_holds": sum(c["state"] in ("FOLLOW_UP_ESCALATE", "CITATION_DEPENDENCY_HOLD")
                                             for c in all_rows),
        "independently_authenticated_reviewers": 0,
        "independently_verified_source_links": 0,
        "independently_reconciled_shared_url_scopes": 0,
        "qualified_safety_approvals_verified": 0,
    }
    result = {
        "schema_version": REPORT_SCHEMA,
        "purpose": "SELF_REPORTED_DISCREPANCIES_NOT_CORROBORATED_SOURCE_OR_SAFETY_CLEARANCE",
        "release_state": "HOLD", "may_publish": False,
        "independent_review_complete": False,
        "manifest_sha256": manifest["manifest_sha256"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "bundle_sha256": sorted(seen_bundles),
        "counts": counts,
        "citations": citation_rows,
        "shared_url_packets": group_rows,
        "human_review_required": True,
        "note": ("Names and evidence notes omitted; observed agreement is self-reported and cannot establish "
                 "credentialed source verification, safety clearance, editorial QD or permission to publish."),
    }
    result["audit_sha256"] = receipts.digest(result)
    if previous is not None:
        verify_previous(previous, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, action="append", required=True,
                        help="repeat for separately prepared local reviewer response JSON files")
    parser.add_argument("--previous-report", type=Path,
                        help="optional prior output; refuse silent removal or revision of its reviews")
    parser.add_argument("--require-no-discrepancies", action="store_true",
                        help="status 1 if any report disagreement/followup/missing input; NOT a safety approval")
    parser.add_argument("--require-release-ready", action="store_true",
                        help="ALWAYS status 1; review reports cannot grant publication clearance")
    args = parser.parse_args(argv)
    if len(args.responses) > MAX_BUNDLES:
        print("Review discrepancy audit FAILED CLOSED: too many response files", file=sys.stderr)
        return 2
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    import evidence_freeze
    import source_review_queue
    try:
        lib = build.Library()
        source_queue = source_review_queue.build_review_queue(lib)
        fingerprints = {slug: evidence_freeze.fingerprint(lib, meta)
                        for slug, meta in lib.articles.items()}
        manifest = receipts.build_manifest(source_queue, fingerprints)
        loaded = [intake.load_response_file(p) for p in args.responses]
        old = intake.load_response_file(args.previous_report, max_bytes=MAX_PREVIOUS_BYTES) if args.previous_report else None
        result = audit_discrepancies(manifest, loaded, previous=old)
    except (ValueError, KeyError, TypeError, OSError, OverflowError) as exc:
        print(f"Review discrepancy audit FAILED CLOSED: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    if args.require_release_ready:
        return 1
    if args.require_no_discrepancies and (
        result["counts"]["citation_requests_with_fewer_than_two_reports"]
        or result["counts"]["shared_url_packets_with_fewer_than_two_reports"]
        or result["counts"]["disagreements_requiring_human_review"]
        or result["counts"]["followup_and_dependency_holds"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
