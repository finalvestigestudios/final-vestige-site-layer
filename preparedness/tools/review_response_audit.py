#!/usr/bin/env python3
"""Read-only, fail-closed intake for *self-reported* Preparedness source reviews.

No reviewer identity is authenticated. No network calls, approvals, crosswalk
resolutions, source metadata mutations, safety conclusions or CMS writes occur.
A valid response is only a bound human-review *claim* requiring independent QA.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_receipts as receipts

HEX = re.compile(r"[0-9a-f]{64}\Z")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_FIELD = 4000
RISK_FLAGS = frozenset({"WATER", "FOOD", "MEDICINE", "INFANT", "POWER_CO",
                        "FIRE", "SHELTER", "HISTORICAL_METHOD", "OTHER"})
LINK_STATES = frozenset({"REACHED_SOURCE", "REDIRECTED_SOURCE", "NOT_REACHABLE", "NOT_ATTEMPTED"})
CLAIM_STATES = frozenset({"SUPPORTED_IN_INSPECTED_SCOPE", "CONTRADICTED", "UNCERTAIN", "NOT_CHECKED"})
GROUP_STATES = frozenset({"CONSISTENT_LIMITED_SCOPES", "CONFLICTING_SCOPES", "UNRESOLVED"})
ROW_STATES = frozenset({"INSPECTED", "NOT_INSPECTED"})
CITATION_KEYS = frozenset({"review_request_sha256", "reviewer", "reviewed_on", "link_check",
                          "observed_url", "source_locator", "claim_check", "evidence_notes",
                          "reading_limits", "risk_flags"})
GROUP_KEYS = frozenset({"packet_sha256", "reviewer", "reviewed_on", "url", "row_reviews",
                       "relationship", "comparison_notes"})
ROW_KEYS = frozenset({"source_row_key", "reading_status", "source_locator", "reading_notes"})
INPUT_KEYS = frozenset({"schema_version", "manifest_sha256", "citation_responses", "shared_url_responses"})


def require_object(value: object, keys: frozenset[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label}: unknown/missing fields (never accept approval or release overrides)")
    return value


def require_text(value: object, label: str, minimum: int = 1) -> str:
    if not isinstance(value, str) or not (minimum <= len(value.strip()) <= MAX_FIELD):
        raise ValueError(f"{label}: missing or invalid substantive text")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
        raise ValueError(f"{label}: control character")
    return value


def require_sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(f"{label}: invalid SHA256")
    return value


def require_date(value: object, label: str, today: date) -> str:
    if not isinstance(value, str) or not DAY.fullmatch(value):
        raise ValueError(f"{label}: expected ISO YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}: impossible calendar date") from exc
    if parsed > today:
        raise ValueError(f"{label}: future review date")
    return value


def require_https(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("https://") or any(ord(c) <= 32 for c in value):
        raise ValueError(f"{label}: expected HTTPS URL")
    try:
        parts = urlsplit(value)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.port not in (None, 443):
            raise ValueError("unsafe URL")
    except ValueError as exc:
        raise ValueError(f"{label}: invalid HTTPS URL") from exc
    if len(value) > MAX_FIELD or "\\" in value or "@" in parts.netloc:
        raise ValueError(f"{label}: malformed URL")
    return value


def validate_manifest(manifest: dict) -> tuple[dict, dict]:
    """Do not trust digest fields alone: check per-entry binding, inventory, HOLD."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("manifest: unsupported schema")
    if (manifest.get("release_state") != "HOLD" or manifest.get("may_publish") is not False
            or manifest.get("human_review_performed") is not False):
        raise ValueError("manifest: release/HOLD invariant violated")
    expected_digest = receipts.digest({k: v for k, v in manifest.items() if k != "manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_digest:
        raise ValueError("manifest: SHA256 payload mismatch")
    require_sha(manifest.get("source_queue_sha256"), "source queue")
    citations, groups = manifest.get("citations"), manifest.get("shared_url_packets")
    if not isinstance(citations, list) or not isinstance(groups, list):
        raise ValueError("manifest: missing inventories")
    counts = manifest.get("counts")
    if not isinstance(counts, dict) or counts.get("citation_requests") != len(citations) or counts.get("shared_url_packets") != len(groups):
        raise ValueError("manifest: changed citation/group inventory")
    cit_index, group_index = {}, {}
    for citation in citations:
        if not isinstance(citation, dict) or citation.get("review_state") != "PENDING_HUMAN" or citation.get("approved") is not False:
            raise ValueError("manifest: citation is not a pending request")
        key = require_sha(citation.get("review_request_sha256"), "citation")
        expected = receipts.digest({k: v for k, v in citation.items() if k not in ("review_request_sha256", "review_state", "approved")})
        if key != expected or key in cit_index:
            raise ValueError("manifest: citation request binding/uniqueness failed")
        if not isinstance(citation.get("url"), str) or not citation["url"].startswith("https://"):
            raise ValueError("manifest: invalid citation source URL")
        cit_index[key] = citation
    for group in groups:
        if not isinstance(group, dict) or group.get("review_state") != "PENDING_HUMAN" or group.get("approved") is not False:
            raise ValueError("manifest: shared URL packet is not pending")
        key = require_sha(group.get("packet_sha256"), "shared URL packet")
        expected = receipts.digest({k: v for k, v in group.items() if k not in ("packet_sha256", "review_state", "approved", "human_tasks")})
        if key != expected or key in group_index:
            raise ValueError("manifest: shared packet binding/uniqueness failed")
        require_https(group.get("url"), "packet source URL")
        if not isinstance(group.get("all_source_row_keys"), list) or not group["all_source_row_keys"] or len(group["all_source_row_keys"]) != len(set(group["all_source_row_keys"])):
            raise ValueError("manifest: malformed physical source row inventory")
        group_index[key] = group
    return cit_index, group_index


def validate_citation_response(response: dict, request: dict, today: date) -> dict:
    require_object(response, CITATION_KEYS, "citation response")
    require_sha(response["review_request_sha256"], "citation response id")
    require_text(response["reviewer"], "reviewer", minimum=3)
    require_date(response["reviewed_on"], "citation review date", today)
    link = response["link_check"]
    claim = response["claim_check"]
    if link not in LINK_STATES or claim not in CLAIM_STATES:
        raise ValueError("citation response: unsupported link/claim assessment")
    require_text(response["evidence_notes"], "evidence notes", minimum=18)
    require_text(response["reading_limits"], "reading limitations", minimum=12)
    flags = response["risk_flags"]
    if not isinstance(flags, list) or len(flags) != len(set(str(flag) for flag in flags)) or not all(isinstance(flag, str) and flag in RISK_FLAGS for flag in flags):
        raise ValueError("citation response: invalid risk flags")
    observed = response["observed_url"]
    locator = response["source_locator"]
    reached = link in ("REACHED_SOURCE", "REDIRECTED_SOURCE")
    if reached:
        require_https(observed, "observed source")
        require_text(locator, "source locator", minimum=4)
        if link == "REACHED_SOURCE" and observed != request["url"]:
            raise ValueError("citation response: URL changed without redirect declaration")
        if link == "REDIRECTED_SOURCE" and observed == request["url"]:
            raise ValueError("citation response: redirect declaration without changed URL")
    else:
        if observed is not None or locator != "":
            raise ValueError("citation response: cannot claim source/locator without access")
        if claim != "NOT_CHECKED":
            raise ValueError("citation response: inaccessible source cannot support a claim assessment")
    follow_up = (link != "REACHED_SOURCE" or claim != "SUPPORTED_IN_INSPECTED_SCOPE" or bool(flags))
    return {"review_request_sha256": response["review_request_sha256"],
            "status": "FOLLOW_UP_REQUIRED" if follow_up else "REVIEWER_REPORT_RECORDED_UNVERIFIED",
            "self_reported_link": link, "self_reported_claim": claim,
            "risk_flags": sorted(flags), "reviewed_on_reported": response["reviewed_on"],
            "reviewer_identity_authenticated": False, "source_link_independently_verified": False,
            "safety_approved": False}


def validate_group_response(response: dict, request: dict, today: date) -> dict:
    require_object(response, GROUP_KEYS, "group response")
    require_sha(response["packet_sha256"], "shared URL packet id")
    require_text(response["reviewer"], "group reviewer", minimum=3)
    require_date(response["reviewed_on"], "group review date", today)
    if response["url"] != request["url"]:
        raise ValueError("group response: source URL differs from packet")
    relationship = response["relationship"]
    if relationship not in GROUP_STATES:
        raise ValueError("group response: invalid source-scope relation")
    require_text(response["comparison_notes"], "group comparison notes", minimum=20)
    row_reviews = response["row_reviews"]
    if not isinstance(row_reviews, list):
        raise ValueError("group response: row reviews must be a list")
    index = {}
    for row in row_reviews:
        require_object(row, ROW_KEYS, "row response")
        key = require_text(row["source_row_key"], "row key")
        if key in index:
            raise ValueError("group response: duplicate physical source row")
        if row["reading_status"] not in ROW_STATES:
            raise ValueError("group response: invalid reading status")
        require_text(row["reading_notes"], "row reading limitations", minimum=12)
        if row["reading_status"] == "INSPECTED":
            require_text(row["source_locator"], "row source locator", minimum=4)
        elif row["source_locator"] != "":
            raise ValueError("group response: cannot claim locator for unread row")
        index[key] = row
    if set(index) != set(request["all_source_row_keys"]):
        raise ValueError("group response: physical source rows missing/extra")
    missing = sorted(k for k, row in index.items() if row["reading_status"] != "INSPECTED")
    if missing and relationship == "CONSISTENT_LIMITED_SCOPES":
        raise ValueError("group response: cannot claim consistent readings with uninspected variants")
    return {"packet_sha256": response["packet_sha256"],
            "status": "FOLLOW_UP_REQUIRED" if missing or relationship != "CONSISTENT_LIMITED_SCOPES" else "REVIEWER_REPORT_RECORDED_UNVERIFIED",
            "source_scope_relation_reported": relationship,
            "physical_rows_not_inspected": missing,
            "reviewer_identity_authenticated": False, "source_scope_independently_reconciled": False,
            "crosswalk_review_state_changed": False}


def audit(manifest: dict, response_bundle: dict, *, today: date | None = None) -> dict:
    """Only creates an immutable triage snapshot; every outcome is release HOLD."""
    today = today or date.today()
    cit_index, group_index = validate_manifest(manifest)
    require_object(response_bundle, INPUT_KEYS, "response bundle")
    if response_bundle["schema_version"] != 1 or response_bundle["manifest_sha256"] != manifest["manifest_sha256"]:
        raise ValueError("response bundle: stale/wrong manifest binding")
    cites, groups = response_bundle["citation_responses"], response_bundle["shared_url_responses"]
    if not isinstance(cites, list) or not isinstance(groups, list):
        raise ValueError("response bundle: response sets must be arrays")
    cited, shared = {}, {}
    for response in cites:
        if not isinstance(response, dict):
            raise ValueError("citation response: not an object")
        key = require_sha(response.get("review_request_sha256"), "citation response id")
        if key not in cit_index or key in cited:
            raise ValueError("citation response: stale/unknown/duplicate request")
        cited[key] = validate_citation_response(response, cit_index[key], today)
    for response in groups:
        if not isinstance(response, dict):
            raise ValueError("shared URL response: not an object")
        key = require_sha(response.get("packet_sha256"), "shared URL packet id")
        if key not in group_index or key in shared:
            raise ValueError("shared URL response: stale/unknown/duplicate packet")
        shared[key] = validate_group_response(response, group_index[key], today)
    cit_out = [cited.get(key) or {"review_request_sha256": key, "status": "PENDING_HUMAN_INPUT",
                                  "reviewer_identity_authenticated": False,
                                  "source_link_independently_verified": False,
                                  "safety_approved": False}
               for key in sorted(cit_index)]
    group_out = [shared.get(key) or {"packet_sha256": key, "status": "PENDING_HUMAN_INPUT",
                                    "source_scope_independently_reconciled": False,
                                    "crosswalk_review_state_changed": False}
                 for key in sorted(group_index)]
    counts = {
        "citation_requests": len(cit_out), "citation_inputs_recorded": len(cited),
        "citation_inputs_pending": len(cit_out) - len(cited),
        "citation_input_followups": sum(row["status"] == "FOLLOW_UP_REQUIRED" for row in cit_out),
        "shared_url_packets": len(group_out), "shared_url_inputs_recorded": len(shared),
        "shared_url_inputs_pending": len(group_out) - len(shared),
        "shared_url_input_followups": sum(row["status"] == "FOLLOW_UP_REQUIRED" for row in group_out),
        "source_scope_reconciliations_verified": 0,
        "independently_authenticated_reviewers": 0,
        "qualified_safety_approvals_verified": 0,
    }
    result = {"schema_version": 1, "purpose": "REVIEWER_SELF_REPORT_TRIAGE_NOT_SOURCE_OR_SAFETY_CLEARANCE",
              "release_state": "HOLD", "may_publish": False,
              "independent_review_complete": False, "source_queue_sha256": manifest["source_queue_sha256"],
              "manifest_sha256": manifest["manifest_sha256"],
              "counts": counts, "citations": cit_out, "shared_url_packets": group_out}
    result["audit_sha256"] = receipts.digest(result)
    return result


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"response JSON: duplicate object key {key!r}")
        result[key] = value
    return result


def load_response_file(path: Path, *, max_bytes: int = MAX_RESPONSE_BYTES) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("response input: must be a regular non-symlink file")
    if path.stat().st_size > max_bytes:
        raise ValueError("response input: size limit exceeded")
    with path.open("rb") as handle:
        encoded = handle.read(max_bytes + 1)
    if len(encoded) > max_bytes:
        raise ValueError("response input: size limit exceeded")
    try:
        parsed = json.loads(encoded.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_keys,
                            parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"invalid number {x}")))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("response input: malformed UTF-8 JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("response input: JSON object required")
    return parsed


def empty_response_template(manifest: dict) -> dict:
    """Generate a safely empty, digest-bound intake scaffold; no reviews are implied."""
    validate_manifest(manifest)
    return {"schema_version": 1, "manifest_sha256": manifest["manifest_sha256"],
            "citation_responses": [], "shared_url_responses": []}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument("--responses", type=Path,
                         help="local JSON self-reported evidence notes (never an approval)")
    options.add_argument("--emit-empty-template", action="store_true",
                         help="print a blank response scaffold bound to current corpus; no review is claimed")
    parser.add_argument("--require-complete-input", action="store_true",
                        help="exit 1 if any request has no response; does NOT imply publish approval")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    import evidence_freeze
    import source_review_queue
    try:
        lib = build.Library()
        fresh_queue = source_review_queue.build_review_queue(lib)
        fingerprints = {slug: evidence_freeze.fingerprint(lib, meta)
                        for slug, meta in lib.articles.items()}
        manifest = receipts.build_manifest(fresh_queue, fingerprints)
        if args.emit_empty_template:
            sys.stdout.write(json.dumps(empty_response_template(manifest), sort_keys=True, indent=2) + "\n")
            return 0
        result = audit(manifest, load_response_file(args.responses))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Review response audit FAILED CLOSED: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n")
    if args.require_complete_input and (result["counts"]["citation_inputs_pending"]
                                        or result["counts"]["shared_url_inputs_pending"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
