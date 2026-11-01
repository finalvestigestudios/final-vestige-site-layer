#!/usr/bin/env python3
"""R41: private, lossless retrospective custody for R40-verified receipt segments.

Read-only HOLD gate. It never writes a ledger, provisions keys, certifies review,
authenticates people, or authorizes any publication. Only an independent,
access-controlled, atomic service can pin archive tips and prevent forks.
A historical archived segment cannot be re-authorized via the R39 24-hour
freshness window: it preserves the *full original private submission evidence*
and verifies hash custody relative to independently trusted archive endpoints.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ISSUE = 136
MAX_ARCHIVE_SEGMENT = 128
MAX_TOTAL_SUBMISSIONS = 4096
MAX_PRIOR_NONCES = 100000
ZERO = "0" * 64
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX32 = re.compile(r"[0-9a-f]{32}\Z")
KEY_ID = re.compile(r"[a-z][a-z0-9._-]{2,63}\Z")
HEAD_FIELDS = frozenset({"event_index", "archive_tip_sha256",
                         "receipt_chain_head", "parent_R37_fingerprint_sha256"})
REC_FIELDS = frozenset({"schema_version", "issue", "release_state",
                        "machine_authority", "previous_archive_head",
                        "r40_audit_report", "complete_private_submissions",
                        "submissions_sha256", "record_sha256",
                        "may_publish", "qualified_safety_clearance",
                        "independent_QD_approval", "human_source_reviews_completed",
                        "source_claim_accuracy_verified", "reviewer_real_identity_verified"})
FLAGS = ("may_publish", "qualified_safety_clearance", "independent_QD_approval",
         "human_source_reviews_completed", "source_claim_accuracy_verified",
         "reviewer_real_identity_verified")
AUTHORITY = "PRIVATE_HISTORICAL_R40_RECEIPT_EVIDENCE_CUSTODY_NOT_APPROVAL"
R40_AUTHORITY = "RECENT_OFFLINE_RECEIPT_TRANSCRIPT_CUSTODY_NOT_AUTHORIZATION"

class HistoryHold(ValueError):
    """Do not trust an incomplete, altered, unpinned, or falsely approving history."""


def need(ok, reason):
    if not ok:
        raise HistoryHold(reason)


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise HistoryHold("noncanonical archival evidence") from exc


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha64(value):
    return type(value) is str and HEX64.fullmatch(value) is not None


def _receipt_head(value):
    need(type(value) is dict and set(value) == {"sequence", "receipt_sha256"},
         "R39 chain head is not exact")
    seq, sha = value["sequence"], value["receipt_sha256"]
    need(type(seq) is int and 0 <= seq <= 2 ** 53 and sha64(sha) and
         ((seq == 0 and sha == ZERO) or (seq > 0 and sha != ZERO)),
         "invalid R39 receipt sequence or digest")
    return seq


def validate_archive_head(value):
    need(type(value) is dict and set(value) == HEAD_FIELDS,
         "independently pinned archive head is missing or malformed")
    seq = value["event_index"]
    need(type(seq) is int and 0 <= seq <= 2 ** 53 and
         sha64(value["archive_tip_sha256"]) and
         sha64(value["parent_R37_fingerprint_sha256"]) and
         value["parent_R37_fingerprint_sha256"] != ZERO,
         "invalid archive event index or parent evidence digest")
    _receipt_head(value["receipt_chain_head"])
    need((seq == 0 and value["archive_tip_sha256"] == ZERO) or
         (seq > 0 and value["archive_tip_sha256"] != ZERO),
         "archive genesis and tip contradict each other")
    if seq == 0:
        need(value["receipt_chain_head"]["sequence"] == 0,
             "genesis archive cannot contain unaccounted signed receipts")
    else:
        need(value["receipt_chain_head"]["sequence"] >= seq,
             "archive cannot contain more events than signed receipts")
    return seq


def genesis(parent_r37_sha256):
    need(sha64(parent_r37_sha256) and parent_r37_sha256 != ZERO,
         "trusted R37 original evidence fingerprint is required")
    return {"event_index": 0, "archive_tip_sha256": ZERO,
            "receipt_chain_head": {"sequence": 0, "receipt_sha256": ZERO},
            "parent_R37_fingerprint_sha256": parent_r37_sha256}


def _nonce_register(value):
    need(type(value) is frozenset and len(value) <= MAX_PRIOR_NONCES,
         "prior-nonce register must be a separately trusted bounded frozenset")
    for pair in value:
        need(type(pair) is tuple and len(pair) == 2 and
             type(pair[0]) is str and KEY_ID.fullmatch(pair[0]) is not None and
             type(pair[1]) is str and HEX32.fullmatch(pair[1]) is not None,
             "invalid external prior key/nonce pair")
    return set(value)


def _require_hold(mapping, source):
    need(type(mapping) is dict and mapping.get("release_state") == "HOLD" and
         all(mapping.get(f) is False for f in FLAGS if f in mapping) and
         mapping.get("issue") == ISSUE and type(mapping.get("issue")) is int,
         "false human, safety, QD, or publishing authority in " + source)


def _r40_report_shape(report, start, *, expected_parent):
    """Historical verification of frozen R40 report STRUCTURE, not HMAC/key validity."""
    _require_hold(report, "R40 report")
    need(report.get("schema_version") == 1 and
         report.get("machine_authority") == R40_AUTHORITY and
         type(report.get("fingerprint_sha256")) is str and
         sha64(report["fingerprint_sha256"]) and
         digest({k: v for k, v in report.items() if k != "fingerprint_sha256"}) ==
             report["fingerprint_sha256"] and
         report.get("parent_R37_fingerprint_sha256") == expected_parent,
         "R40 report fingerprint, authority, or frozen parent is invalid")
    need(set(FLAGS).issubset(report) and all(report[f] is False for f in FLAGS),
         "R40 transcript cannot assert review, identity, QD, or safety approval")
    need(report.get("original_trusted_start_head") == start and
         type(report.get("verified_key_possession_receipt_count")) is int and
         1 <= report["verified_key_possession_receipt_count"] <= 128,
         "R40 anchored transcript/start/count is invalid")
    end = report.get("externally_pinned_end_head")
    start_seq, end_seq = _receipt_head(start), _receipt_head(end)
    count = report["verified_key_possession_receipt_count"]
    need(end_seq == start_seq + count,
         "R40 trusted receipt chain sequence not contiguous")
    hashes = report.get("verified_receipt_sha256")
    nonces = report.get("proposed_nonce_additions")
    counts = report.get("unverified_annotation_records_per_receipt")
    need(type(hashes) is list and len(hashes) == count and all(sha64(h) for h in hashes) and
         type(nonces) is list and len(nonces) == count and
         type(counts) is list and len(counts) == count and
         all(type(c) is int and c > 0 for c in counts),
         "R40 receipt hashes, nonce additions or unverified note counts incomplete")
    return end, hashes, nonces


def _verify_record(record, previous, seen):
    need(type(record) is dict and set(record) == REC_FIELDS,
         "archived record has missing or extra fields")
    _require_hold(record, "archival record")
    need(record["schema_version"] == 1 and record["machine_authority"] == AUTHORITY and
         all(record[f] is False for f in FLAGS),
         "archival record is not strictly unapproved HOLD")
    need(record["previous_archive_head"] == previous,
         "archival record history fork or wrong previous head")
    need(sha64(record["record_sha256"]) and
         digest({k: v for k, v in record.items() if k != "record_sha256"}) ==
             record["record_sha256"], "archival record fingerprint does not match")
    submissions = record["complete_private_submissions"]
    report = record["r40_audit_report"]
    need(type(submissions) is list and
         1 <= len(submissions) <= 128 and
         record["submissions_sha256"] == digest(submissions),
         "full original private R40 submissions missing or altered")
    end, hashes, nonces = _r40_report_shape(
        report, previous["receipt_chain_head"],
        expected_parent=previous["parent_R37_fingerprint_sha256"])
    need(len(submissions) == len(hashes), "receipt evidence was truncated")
    for i, entry in enumerate(submissions):
        need(type(entry) is dict and set(entry) == {"edited_csv_tables", "receipt"} and
             type(entry["edited_csv_tables"]) is dict and
             type(entry["receipt"]) is dict,
             "private archived receipt lacks complete edited CSV evidence")
        receipt = entry["receipt"]
        need(digest(receipt) == hashes[i],
             "archived signed receipt differs from original R40 audit")
        nonce = nonces[i]
        pair = (receipt.get("reviewer_key_id"), receipt.get("submission_nonce_hex"))
        need(type(nonce) is list and len(nonce) == 2 and
             nonce == list(pair) and type(pair[0]) is str and
             KEY_ID.fullmatch(pair[0]) is not None and
             type(pair[1]) is str and HEX32.fullmatch(pair[1]) is not None and
             pair not in seen, "archived signed receipt nonce missing or replayed")
        seen.add(pair)
        need(type(receipt.get("sequence")) is int and
             receipt.get("sequence") == previous["receipt_chain_head"]["sequence"] + i + 1 and
             (receipt.get("previous_receipt_sha256") ==
              (previous["receipt_chain_head"]["receipt_sha256"] if i == 0 else hashes[i-1])),
             "archived signed receipt R39 chain continuity failed")
    need(end["receipt_sha256"] == hashes[-1],
         "R40 end receipt digest does not bind final signed receipt")
    return {"event_index": previous["event_index"] + 1,
            "archive_tip_sha256": record["record_sha256"],
            "receipt_chain_head": copy.deepcopy(end),
            "parent_R37_fingerprint_sha256": previous["parent_R37_fingerprint_sha256"]}


def audit_archive_segment(records, *, trusted_start_head, trusted_end_head,
                          trusted_prior_nonces):
    """Audit full immutable private evidence against OUT-OF-BAND pinned tips.

    This checks archival continuity and retained original bytes/receipt hashes,
    not the original 24-hour verifier, source truth, or the real reviewer.
    The external authority must vouch for each R40 report's actual ingestion.
    """
    need(type(records) is list and 1 <= len(records) <= MAX_ARCHIVE_SEGMENT,
         "missing, oversized, or malformed historical record segment")
    start_index = validate_archive_head(trusted_start_head)
    end_index = validate_archive_head(trusted_end_head)
    need(end_index - start_index == len(records),
         "independently pinned archive-tip span disagrees with records")
    seen = _nonce_register(trusted_prior_nonces)
    head = copy.deepcopy(trusted_start_head)
    total = 0
    record_hashes = []
    for record in records:
        head = _verify_record(record, head, seen)
        total += len(record["complete_private_submissions"])
        need(total <= MAX_TOTAL_SUBMISSIONS,
             "archive segment exceeds bounded receipt work limit")
        record_hashes.append(record["record_sha256"])
    need(head == trusted_end_head,
         "archived evidence does not match independently pinned final tip")
    report = {"schema_version": 1, "issue": 136, "release_state": "HOLD",
              "machine_authority": "RETROSPECTIVE_HASH_CUSTODY_ONLY_NOT_HUMAN_APPROVAL",
              "original_trusted_start_head": copy.deepcopy(trusted_start_head),
              "externally_pinned_end_head": copy.deepcopy(trusted_end_head),
              "verified_history_record_count": len(records),
              "retained_signed_receipt_count": total,
              "retained_complete_private_submissions": True,
              "record_sha256": record_hashes,
              "reverified_historical_key_validity": False,
              "authenticated_human_reviewer_identity": False,
              **{flag: False for flag in FLAGS}}
    report["fingerprint_sha256"] = digest(report)
    return report


def append_recent_candidate(original_r37, submissions, *, trusted_registry,
                            trusted_archive_head, trusted_end_receipt_head,
                            trusted_prior_nonces, trusted_now):
    """Re-run actual R40 recent audit, then RETURN an uncommitted private entry.

    Caller must compare-and-swap trusted archive head + nonce register in ONE
    external durable transaction. No filesystem/cloud/CMS mutation occurs here.
    """
    validate_archive_head(trusted_archive_head)
    need(type(original_r37) is dict and
         original_r37.get("manifest", {}).get("fingerprint_sha256") ==
         trusted_archive_head["parent_R37_fingerprint_sha256"],
         "untrusted or changed original R37 evidence baseline")
    location = Path(__file__).with_name("reviewer_receipt_transcript_gate.py")
    need(location.is_file() and not location.is_symlink(),
         "exact nonsymlink R40 auditor required")
    spec = importlib.util.spec_from_file_location("preparedness_r41_frozen_r40", location)
    need(spec is not None and spec.loader is not None,
         "R40 module cannot load")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        report = module.audit_recent_segment(
            original_r37, submissions, trusted_registry=trusted_registry,
            trusted_start_head=trusted_archive_head["receipt_chain_head"],
            trusted_end_head=trusted_end_receipt_head,
            trusted_prior_nonces=trusted_prior_nonces,
            trusted_now=trusted_now)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise HistoryHold("exact R40 recent signed receipt audit rejected candidate") from exc
    record = {"schema_version": 1, "issue": 136, "release_state": "HOLD",
              "machine_authority": AUTHORITY,
              "previous_archive_head": copy.deepcopy(trusted_archive_head),
              "r40_audit_report": copy.deepcopy(report),
              "complete_private_submissions": copy.deepcopy(submissions),
              "submissions_sha256": digest(submissions),
              **{flag: False for flag in FLAGS}}
    record["record_sha256"] = digest(record)
    new_nonces = _nonce_register(trusted_prior_nonces)
    next_head = _verify_record(record, trusted_archive_head, new_nonces)
    need(len(new_nonces) - len(trusted_prior_nonces) == len(submissions),
         "nonce register did not account for all new submissions")
    return {"release_state": "HOLD", "issue": 136,
            "record_uncommitted": record, "proposed_next_archive_head": next_head,
            "proposed_nonce_additions": report["proposed_nonce_additions"],
            "independently_atomic_commit_performed": False,
            **{flag: False for flag in FLAGS}}


def preflight_unsigned_history(unsigned_r40):
    """CI-only zero-progress preflight; no made-up reviewers or archive tips."""
    need(type(unsigned_r40) is dict and
         unsigned_r40.get("issue") == 136 and
         unsigned_r40.get("machine_authority") ==
             "R40_UNSIGNED_ZERO_PROGRESS_CUSTODY_ONLY" and
         unsigned_r40.get("release_state") == "HOLD" and
         unsigned_r40.get("verified_human_receipts") == 0 and
         unsigned_r40.get("key_possession_verified") is False and
         unsigned_r40.get("reviewer_real_identity_verified") is False and
         all(unsigned_r40.get(f) is False for f in FLAGS if f in unsigned_r40) and
         sha64(unsigned_r40.get("parent_R37_fingerprint_sha256")) and
         sha64(unsigned_r40.get("challenge_sha256")),
         "R41 unsigned archival preflight cannot manufacture receipt or review")
    o = {"schema_version": 1, "issue": 136, "release_state": "HOLD",
         "machine_authority": "UNSIGNED_NO_LEDGER_NO_REVIEW_HISTORY_PREFLIGHT",
         "parent_R37_fingerprint_sha256":
             unsigned_r40["parent_R37_fingerprint_sha256"],
         "parent_R40_challenge_sha256": unsigned_r40["challenge_sha256"],
         "archived_signed_receipt_records": 0,
         "trusted_external_ledger_present": False,
         "reviewer_real_identity_verified": False,
         **{flag: False for flag in FLAGS}}
    o["fingerprint_sha256"] = digest(o)
    return o
