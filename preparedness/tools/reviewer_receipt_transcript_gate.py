#!/usr/bin/env python3
"""R40: bounded offline transcript audit for R39 quarantined review receipts.

CUSTODY / HOLD ONLY. This does not create a durable log, authenticate a real
person, validate cited science, grant QD, or allow publication. Anchors, clock,
keyring and previously accepted nonces must come from a trusted system outside
these submitted receipts. A trusted service must atomically persist successors.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import importlib.util
from pathlib import Path

_UPSTREAM = Path(__file__).with_name("reviewer_receipt_chain_gate.py")
if not _UPSTREAM.is_file() or _UPSTREAM.is_symlink():
    raise ValueError("missing or linked exact R39 receipt gate")
_spec = importlib.util.spec_from_file_location("preparedness_r40_exact_r39", _UPSTREAM)
if _spec is None or _spec.loader is None:
    raise ValueError("R39 receipt gate cannot be imported")
_r39 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r39)

class TranscriptHold(ValueError):
    """Absent independent anchors or unverifiable/quarantined receipt segment."""

AUTHORITY = "RECENT_OFFLINE_RECEIPT_TRANSCRIPT_CUSTODY_NOT_AUTHORIZATION"
MAX_SEGMENT = 128
MAX_PRIOR_NONCES = 100000
FLAGS = ("may_publish", "source_claim_accuracy_verified",
         "human_source_reviews_completed", "qualified_safety_clearance",
         "independent_QD_approval")


def need(ok, reason):
    if not ok:
        raise TranscriptHold(reason)


def _head(value, label):
    try:
        return _r39.validate_chain(value)
    except (_r39.ReceiptHold, TypeError, ValueError) as exc:
        raise TranscriptHold("untrusted " + label + " chain anchor") from exc


def _nonces(value):
    # Never reconstruct prior replay state from the untrusted transcript.
    need(type(value) is frozenset and len(value) <= MAX_PRIOR_NONCES,
         "external prior-nonce register must be a bounded frozenset")
    for item in value:
        need(type(item) is tuple and len(item) == 2,
             "malformed independently trusted previous nonce pair")
        try:
            _r39.safe_key_id(item[0])
        except (_r39.ReceiptHold, TypeError) as exc:
            raise TranscriptHold("invalid previous key identity handle") from exc
        need(type(item[1]) is str and _r39.HEX32.fullmatch(item[1]) is not None,
             "invalid previous nonce")
    return set(value)


def _clock(now):
    need(type(now) is datetime and now.tzinfo is not None and
         now.utcoffset() == timedelta(0),
         "a separately trusted timezone-aware UTC clock is required")


def preflight_unsigned_baseline(original_r37, original_zero_progress_challenge):
    """CI-only check: NO fabricated reviewer, key, receipt, or ledger."""
    try:
        expected = _r39.unsigned_challenge(
            original_r37, original_r37["csv_tables"])
    except (_r39.ReceiptHold, KeyError, ValueError, TypeError) as exc:
        raise TranscriptHold("R37/R38/R39 baseline no longer has frozen HOLD custody") from exc
    need(type(original_zero_progress_challenge) is dict and
         original_zero_progress_challenge == expected,
         "unsigned original challenge drift or substituted evidence")
    need(expected["release_state"] == "HOLD" and
         expected["unverified_progress_records"] == 0 and
         all(expected.get(flag) is False for flag in FLAGS) and
         expected["parent_R37_fingerprint_sha256"] ==
             original_r37["manifest"]["fingerprint_sha256"],
         "zero-progress baseline must never grant a safety/review PASS")
    return {"schema_version": 1, "issue": 136, "release_state": "HOLD",
            "machine_authority": "R40_UNSIGNED_ZERO_PROGRESS_CUSTODY_ONLY",
            "parent_R37_fingerprint_sha256":
                expected["parent_R37_fingerprint_sha256"],
            "challenge_sha256": expected["challenge_sha256"],
            "verified_human_receipts": 0,
            "key_possession_verified": False,
            "reviewer_real_identity_verified": False,
            **{flag: False for flag in FLAGS}}


def audit_recent_segment(original_r37, submissions, *, trusted_registry,
                         trusted_start_head, trusted_end_head,
                         trusted_prior_nonces, trusted_now):
    """Check every receipt against its ORIGINAL edited CSV and independent pins.

    A submission is EXACTLY {"edited_csv_tables": {four original CSV tables},
    "receipt": R39_signed_receipt}. The caller supplies *separately pinned*
    start/end heads and the accumulated replay register. A self-asserted final
    head/nonce register from a submission is invalid as an authority source.
    This read-only function returns proposals; it never commits any state.

    R39's 24-hour freshness bound means this is a CURRENT short-segment check,
    not long-term retrospective proof of all historical reviewer activity.
    """
    need(type(submissions) is list and 1 <= len(submissions) <= MAX_SEGMENT,
         "receipt segment missing, too large, or not a list")
    _clock(trusted_now)
    start_seq, _ = _head(trusted_start_head, "start")
    end_seq, _ = _head(trusted_end_head, "end")
    need(end_seq - start_seq == len(submissions),
         "independently pinned sequence span does not match submissions")
    seen = _nonces(trusted_prior_nonces)
    need(type(trusted_registry) is dict,
         "a separately provisioned trusted key registry is required")

    head = dict(trusted_start_head)
    hashes, novel, counts = [], [], []
    previous_issued = None
    expected_r37 = original_r37.get("manifest", {}).get("fingerprint_sha256") if type(original_r37) is dict else None
    need(type(expected_r37) is str and _r39.HEX64.fullmatch(expected_r37) is not None,
         "missing trusted original R37 fingerprint")
    for index, entry in enumerate(submissions):
        need(type(entry) is dict and set(entry) == {"edited_csv_tables", "receipt"},
             "receipt entry is missing CSV evidence or adds unauthorized fields")
        receipt, edits = entry["receipt"], entry["edited_csv_tables"]
        need(type(receipt) is dict and type(edits) is dict,
             "receipt and edited evidence must be mappings")
        try:
            issued = _r39.utc_second(receipt.get("issued_at_utc"))
            key = _r39.safe_key_id(receipt.get("reviewer_key_id"))
        except (_r39.ReceiptHold, TypeError, ValueError) as exc:
            raise TranscriptHold("invalid receipt timestamp/key at index " + str(index)) from exc
        need(previous_issued is None or issued >= previous_issued,
             "out-of-order receipt issuance in trusted sequence")
        previous_issued = issued
        nonce = receipt.get("submission_nonce_hex")
        need(type(nonce) is str and _r39.HEX32.fullmatch(nonce) is not None,
             "invalid cryptographic submission nonce")
        pair = (key, nonce)
        need(pair not in seen, "duplicate key/nonce in prior or current segment")
        try:
            verified = _r39.verify_progress_receipt(
                original_r37, edits, receipt, trusted_registry=trusted_registry,
                trusted_chain_head=head, trusted_now=trusted_now)
        except (_r39.ReceiptHold, KeyError, ValueError, TypeError,
                OverflowError) as exc:
            raise TranscriptHold("R39 verification rejected submission " + str(index)) from exc
        need(verified.get("release_state") == "HOLD" and
             verified.get("key_possession_verified") is True and
             verified.get("reviewer_real_identity_verified") is False and
             all(verified.get(flag) is False for flag in FLAGS if flag in verified) and
             verified.get("parent_R37_fingerprint_sha256") == expected_r37 and
             verified.get("quarantine_observations_remain_unverified", 0) > 0,
             "verified segment attempted reviewer, source or safety authority escalation")
        seen.add(pair)
        novel.append(pair)
        hashes.append(verified["receipt_sha256"])
        counts.append(verified["quarantine_observations_remain_unverified"])
        head = verified["proposed_next_trusted_chain_head"]
    need(head == trusted_end_head,
         "actual transcript does not match independently pinned final chain head")
    report = {
        "schema_version": 1, "issue": 136, "release_state": "HOLD",
        "machine_authority": AUTHORITY,
        "parent_R37_fingerprint_sha256": expected_r37,
        "verified_key_possession_receipt_count": len(hashes),
        "unverified_annotation_records_per_receipt": counts,
        "original_trusted_start_head": dict(trusted_start_head),
        "externally_pinned_end_head": dict(trusted_end_head),
        "verified_receipt_sha256": hashes,
        "proposed_nonce_additions": [list(x) for x in novel],
        "reviewer_real_identity_verified": False,
        "source_claim_accuracy_verified": False,
        "human_source_reviews_completed": False,
        "qualified_safety_clearance": False,
        "independent_QD_approval": False,
        "may_publish": False,
        "limitations": "Recent-window key-possession and transcript custody only. "
            "External trusted anchors, key issuance/identity checks, an atomic "
            "durable ledger and qualified independent human review remain "
            "separately required. This report grants no safety/QD/publication PASS."
    }
    report["fingerprint_sha256"] = _r39.digest(report)
    return report
