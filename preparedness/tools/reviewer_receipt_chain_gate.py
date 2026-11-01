#!/usr/bin/env python3
"""R39: independent-key possession receipts for quarantined Preparedness notes.

This is NOT real-world reviewer identity proof, human source validation, qualified
safety sign-off, QD PASS, or publication authorization. A signature proves only
possession of one pre-provisioned symmetric key. The registry and chain head MUST
come from a separate trusted administrator, never from reviewer CSV or a receipt.

Read-only, deterministic, Python-standard-library implementation. No credentials
are stored, printed, fetched over the network, or committed by this module.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import re

_sibling = Path(__file__).with_name("reviewer_quarantine_gate.py")
if not _sibling.is_file() or _sibling.is_symlink():
    raise ValueError("missing or linked frozen R38 quarantine validator")
_spec = importlib.util.spec_from_file_location("preparedness_r39_exact_r38", _sibling)
if _spec is None or _spec.loader is None:
    raise ValueError("cannot load exact frozen R38 quarantine validator")
_r38 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r38)

AUTHORITY = "PRIVATE_KEY_POSSESSION_NOTE_RECEIPT_ONLY_NOT_HUMAN_REVIEW"
CHALLENGE_AUTHORITY = "UNSIGNED_QUARANTINED_NOTE_CHALLENGE_NOT_APPROVAL"
KEY_SCOPE = "PREPAREDNESS_UNVERIFIED_PROGRESS_ONLY"
SIGNATURE_ALGORITHM = "HMAC-SHA256"
DOMAIN = b"FV-PREPAREDNESS-ISSUE136-R39-PROGRESS-RECEIPT-V1\x00"
ZERO_HEAD = "0" * 64
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX32 = re.compile(r"[0-9a-f]{32}\Z")
KEY_ID = re.compile(r"[a-z][a-z0-9._-]{2,63}\Z")
UTC_SECOND = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ\Z")
CHAIN_KEYS = frozenset({"sequence", "receipt_sha256"})
MAX_AGE = timedelta(hours=24)
MAX_FUTURE_SKEW = timedelta(seconds=60)
SIGNED_KEYS = frozenset({"reviewer_key_id", "submission_nonce_hex",
                         "issued_at_utc", "sequence", "previous_receipt_sha256",
                         "signature_algorithm"})
RELEASE_HOLD_FLAGS = ("may_publish", "qualified_safety_clearance",
                      "independent_QD_approval", "human_source_reviews_completed",
                      "source_claim_accuracy_verified")

class ReceiptHold(ValueError):
    """Refuse unsigned, untrusted, stale, replayed, altered or approving receipts."""

def need(ok, why):
    if not ok:
        raise ReceiptHold(why)

def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, OverflowError) as exc:
        raise ReceiptHold("invalid noncanonical receipt data") from exc

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def utc_second(value):
    need(type(value) is str and UTC_SECOND.fullmatch(value) is not None,
         "receipt timestamps must be exact UTC seconds")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptHold("invalid UTC timestamp") from exc
    need(parsed.strftime("%Y-%m-%dT%H:%M:%SZ") == value,
         "noncanonical or impossible UTC timestamp")
    return parsed

def safe_key_id(value):
    need(type(value) is str and KEY_ID.fullmatch(value) is not None,
         "invalid reviewer key handle")
    return value

def validate_chain(head):
    need(type(head) is dict and set(head) == CHAIN_KEYS,
         "trusted chain head missing or malformed")
    seq, fp = head["sequence"], head["receipt_sha256"]
    need(type(seq) is int and seq >= 0 and
         type(fp) is str and HEX64.fullmatch(fp) is not None,
         "invalid trusted chain sequence or digest")
    need(not (seq == 0 and fp != ZERO_HEAD) and
         not (seq > 0 and fp == ZERO_HEAD),
         "chain genesis/sequence contradiction")
    return seq, fp

def unsigned_challenge(original_r37, edited_csv_tables):
    """Revalidate original evidence *and every edited cell* using the R38 gate.

    An edited CSV cannot claim an authority state or replace the trusted R37
    baseline. No signing key, human identity, or completed review is inferred.
    """
    try:
        quarantined = _r38.quarantine_reviewer_csv(original_r37, edited_csv_tables)
    except (_r38.IntakeHold, ValueError, TypeError, OverflowError) as exc:
        raise ReceiptHold("R38 immutable evidence/quarantine gate rejected input") from exc
    m = quarantined["manifest"]
    need(m.get("release_state") == "HOLD" and
         m.get("no_authenticated_human_reviews_or_qualified_safety_findings") is True and
         all(m.get(flag) is False for flag in RELEASE_HOLD_FLAGS) and
         type(m.get("unverified_progress_records")) is int and
         m["unverified_progress_records"] == len(quarantined["quarantine_annotations"]) and
         m.get("fingerprint_sha256") ==
             digest({k: v for k, v in m.items() if k != "fingerprint_sha256"}),
         "quarantine did not remain unapproved and fingerprint bound")
    o = {"schema_version": 1, "issue": 136, "release_state": "HOLD",
         "machine_authority": CHALLENGE_AUTHORITY,
         "parent_R37_fingerprint_sha256": m["parent_R37_fingerprint_sha256"],
         "parent_R38_fingerprint_sha256": m["fingerprint_sha256"],
         "original_R34_R35_R36_lineage_sha256":
              digest([m["parent_R34_original_reading_sha256"],
                      m["parent_R35_fingerprint_sha256"],
                      m["parent_R36_fingerprint_sha256"]]),
         "edited_worksheet_manifest_sha256": digest(m["input_csv_tables"]),
         "quarantined_observations_sha256":
              digest(quarantined["quarantine_annotations"]),
         "unverified_progress_records": m["unverified_progress_records"],
         "source_claim_accuracy_verified": False,
         "human_source_reviews_completed": False,
         "qualified_safety_clearance": False,
         "independent_QD_approval": False, "may_publish": False}
    o["challenge_sha256"] = digest(o)
    return o

def prepare_unsigned_receipt(challenge, *, reviewer_key_id, submission_nonce_hex,
                             issued_at_utc, trusted_chain_head):
    """No signatures or approvals: exact domain-separated data to be signed."""
    need(type(challenge) is dict and
         challenge.get("machine_authority") == CHALLENGE_AUTHORITY and
         challenge.get("release_state") == "HOLD" and
         challenge.get("challenge_sha256") ==
            digest({k:v for k,v in challenge.items() if k != "challenge_sha256"}),
         "unsigned evidence challenge is not intact")
    safe_key_id(reviewer_key_id)
    need(type(submission_nonce_hex) is str and
         HEX32.fullmatch(submission_nonce_hex) is not None,
         "submission nonce must be 128-bit lowercase hex")
    utc_second(issued_at_utc)
    seq, prev = validate_chain(trusted_chain_head)
    return {**challenge, "machine_authority": AUTHORITY,
            "reviewer_key_id": reviewer_key_id,
            "submission_nonce_hex": submission_nonce_hex,
            "issued_at_utc": issued_at_utc,
            "sequence": seq + 1,
            "previous_receipt_sha256": prev,
            "signature_algorithm": SIGNATURE_ALGORITHM}

def sign_progress_receipt(unsigned_receipt, secret):
    """Low-level offline signer for holders of separately provisioned keys.

    Key management, key ownership, and persisting accepted chain state MUST
    occur outside this code. Never include this secret in a PR or CSV.
    """
    need(type(secret) is bytes and len(secret) >= 32,
         "signing key must be at least 256 bits and externally provisioned")
    need(type(unsigned_receipt) is dict and
         unsigned_receipt.get("machine_authority") == AUTHORITY and
         unsigned_receipt.get("release_state") == "HOLD" and
         unsigned_receipt.get("signature_algorithm") == SIGNATURE_ALGORITHM and
         "signature_hex" not in unsigned_receipt and
         "challenge_sha256" in unsigned_receipt,
         "cannot sign an approving, incomplete or already-signed receipt")
    signature = hmac.new(secret, DOMAIN + canonical(unsigned_receipt),
                         hashlib.sha256).hexdigest()
    return {**unsigned_receipt, "signature_hex": signature}

def verify_progress_receipt(original_r37, edited_csv_tables, submitted_receipt,
                            *, trusted_registry, trusted_chain_head, trusted_now):
    """Verify key possession + evidence binding; never certify human identity.

    Caller MUST supply an independently controlled registry, UTC clock and
    durable chain state. Do not pass a reviewer-provided registry/head/clock.
    State is NOT persisted here: accepting multiple receipts from the same old
    head without an atomic outside update can still permit forks/replay.
    """
    challenge = unsigned_challenge(original_r37, edited_csv_tables)
    need(type(submitted_receipt) is dict and
         set(submitted_receipt) == set(challenge) | SIGNED_KEYS | {"signature_hex"},
         "receipt fields missing, extra or substituted")
    need(challenge["unverified_progress_records"] > 0,
         "blank worksheets cannot masquerade as reviewer activity")
    key_id = safe_key_id(submitted_receipt["reviewer_key_id"])
    need(type(trusted_registry) is dict and key_id in trusted_registry,
         "reviewer key is absent from external trusted registry")
    entry = trusted_registry[key_id]
    need(type(entry) is dict and
         set(entry) == {"secret", "state", "scope", "not_before", "not_after"} and
         entry["state"] == "ACTIVE" and entry["scope"] == KEY_SCOPE and
         type(entry["secret"]) is bytes and len(entry["secret"]) >= 32,
         "reviewer key revoked, wrongly scoped or insecure")
    need(type(trusted_now) is datetime and
         trusted_now.tzinfo is not None and
         trusted_now.utcoffset() == timedelta(0),
         "independent timezone-aware UTC verification clock required")
    issued = utc_second(submitted_receipt["issued_at_utc"])
    begin, expiry = utc_second(entry["not_before"]), utc_second(entry["not_after"])
    need(begin <= issued <= expiry and begin <= trusted_now <= expiry and
         -MAX_FUTURE_SKEW <= trusted_now - issued <= MAX_AGE,
         "receipt timestamp expired, premature, future or outside key validity")
    seq, prev = validate_chain(trusted_chain_head)
    need(type(submitted_receipt["sequence"]) is int and
         submitted_receipt["sequence"] == seq + 1 and
         type(submitted_receipt["previous_receipt_sha256"]) is str and
         submitted_receipt["previous_receipt_sha256"] == prev,
         "receipt replay, fork or incorrect independently trusted chain head")
    need(type(submitted_receipt["signature_hex"]) is str and
         HEX64.fullmatch(submitted_receipt["signature_hex"]) is not None,
         "malformed HMAC authentication tag")
    expected = prepare_unsigned_receipt(
        challenge, reviewer_key_id=key_id,
        submission_nonce_hex=submitted_receipt["submission_nonce_hex"],
        issued_at_utc=submitted_receipt["issued_at_utc"],
        trusted_chain_head=trusted_chain_head)
    unsigned = {k:v for k,v in submitted_receipt.items() if k != "signature_hex"}
    need(unsigned == expected,
         "receipt altered, approval fields introduced or evidence not bound")
    correct = hmac.new(entry["secret"], DOMAIN + canonical(unsigned),
                       hashlib.sha256).hexdigest()
    need(hmac.compare_digest(submitted_receipt["signature_hex"], correct),
         "invalid receipt key-possession authentication tag")
    fp = digest(submitted_receipt)
    head = {"sequence": seq + 1, "receipt_sha256": fp}
    return {"schema_version":1, "issue":136, "release_state":"HOLD",
            "machine_authority":"INDEPENDENT_KEY_POSSESSION_CHECK_NOT_IDENTITY",
            "key_possession_verified":True, "reviewer_real_identity_verified":False,
            "human_source_reviews_completed":False,
            "qualified_safety_clearance":False,
            "independent_QD_approval":False, "may_publish":False,
            "quarantine_observations_remain_unverified":
                 challenge["unverified_progress_records"],
            "parent_R37_fingerprint_sha256":
                 challenge["parent_R37_fingerprint_sha256"],
            "parent_R38_fingerprint_sha256":
                 challenge["parent_R38_fingerprint_sha256"],
            "receipt_sha256":fp, "proposed_next_trusted_chain_head":head,
            "limitations":"Only possession of a provisioned symmetric key is demonstrated. "
                 "Trusted key-to-person binding and an atomic, durable replay "
                 "ledger must be maintained independently. No source, clinical, "
                 "safety, editorial, QD or publication review is completed."}
