"""Passphrase-encrypted, authenticated *copies* of premium exception evidence.

No cloud, logging, telemetry, key files or password persistence.  This does not
replace the local plaintext source report/journal, authenticate a reviewer or
assert accounting compliance.  The format is intentionally fixed and versioned.
"""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .exception_review import (
    MAX_JOURNAL_BYTES, MAX_REPORT_BYTES, read_cases, read_journal,
)
from .review_identity import require_snapshot_match
from .vault_decode_privacy import decrypt_evidence, parse_evidence_json, decode_evidence_b64
from .vault_input_snapshot import read_vault_input
from .vault_publish import publish_vault
from .vault_restore_cleanup import rollback_owned_restore
from .vault_restore_writer import make_private_restore_folder, write_private_restore_member
from .vault_restore_verify import verify_private_restore_members
from .vault_product_gate import require_restore_product

MAGIC = b"FVS-EVIDENCE-VAULT-v1\x00"
SALT_SIZE = 16
NONCE_SIZE = 12
KDF_N = 2**15
KDF_R = 8
KDF_P = 1
MAX_VAULT_BYTES = 120 * 1024 * 1024
FIELDS = frozenset((
    "schema", "product", "sealed_utc", "report_filename", "report_sha256",
    "report_b64", "journal_filename", "journal_sha256", "journal_b64",
    "journal_present", "review_event_count",
))


def _unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("Duplicate encrypted evidence field")
        result[k] = v
    return result


def _read_regular(path: Path, limit: int, label: str) -> bytes:
    """One stable, private descriptor snapshot for sealing and restoring."""
    return read_vault_input(path, limit, label)


def _password(password: str) -> bytes:
    if not isinstance(password, str) or not (16 <= len(password) <= 1024):
        raise ValueError("Vault passphrase must contain 16 to 1024 characters")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in password):
        raise ValueError("Vault passphrase cannot contain control characters")
    return password.encode("utf-8")


def _key(password: bytes, salt: bytes) -> bytes:
    return Scrypt(salt=salt, length=32, n=KDF_N, r=KDF_R, p=KDF_P).derive(password)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _name(value: str, extension: str) -> str:
    # Use stable filenames on restore; source filename is informational only.
    if not isinstance(value, str) or len(value) > 255 or not value.lower().endswith(extension):
        raise ValueError("Invalid archived source filename")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("Invalid archived source filename")
    if Path(value).name != value or "/" in value or "\\" in value or ":" in value:
        raise ValueError("Archived source filename contains a path")
    if value in (".", ".."):
        raise ValueError("Invalid archived source filename")
    return value


def seal_evidence(report: str | Path, product: str, journal: str | Path,
                  folder: str | Path, passphrase: str, *,
                  expected_report_sha256: str | None = None) -> Path:
    """Verify evidence, then write an exclusive AES-256-GCM encrypted backup.

    Originals remain plaintext and unchanged.  The caller must protect them.
    """
    password = _password(passphrase)
    source, journal_path, destination = Path(report), Path(journal), Path(folder)
    if not destination.is_dir() or destination.is_symlink():
        raise ValueError("Choose a regular, existing vault destination folder")
    if source.resolve() == journal_path.resolve():
        raise ValueError("Journal and report cannot be the same file")
    batch = read_cases(source, product)
    require_snapshot_match(expected_report_sha256, batch.report_sha256)
    data = _read_regular(source, MAX_REPORT_BYTES, "Report")
    if batch.report_sha256 != _sha(data):
        raise ValueError("Report changed while preparing encrypted evidence")
    included = journal_path.exists() or journal_path.is_symlink()
    journal_data = _read_regular(journal_path, MAX_JOURNAL_BYTES, "Journal") if included else b""
    events = read_journal(journal_path, batch)
    if included and journal_data != _read_regular(journal_path, MAX_JOURNAL_BYTES, "Journal"):
        raise ValueError("Review journal changed while preparing encrypted evidence")
    if not included and (journal_path.exists() or journal_path.is_symlink()):
        raise ValueError("Review journal appeared while preparing encrypted evidence")
    if data != _read_regular(source, MAX_REPORT_BYTES, "Report"):
        raise ValueError("Report changed while preparing encrypted evidence")
    if not included and events:
        raise ValueError("Unrecorded review events are not allowed")
    require_snapshot_match(expected_report_sha256, _sha(data))
    payload = {
        "schema": 1, "product": product,
        "sealed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "report_filename": _name(source.name, ".csv"), "report_sha256": _sha(data),
        "report_b64": base64.b64encode(data).decode("ascii"),
        "journal_filename": _name(journal_path.name, ".jsonl") if included else None,
        "journal_sha256": _sha(journal_data) if included else None,
        "journal_b64": base64.b64encode(journal_data).decode("ascii") if included else None,
        "journal_present": included, "review_event_count": len(events),
    }
    plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False).encode("utf-8")
    salt, nonce = secrets.token_bytes(SALT_SIZE), secrets.token_bytes(NONCE_SIZE)
    prefix = MAGIC + salt + nonce
    ciphertext = AESGCM(_key(password, salt)).encrypt(nonce, plaintext, prefix)
    vault_bytes = prefix + ciphertext
    if len(vault_bytes) > MAX_VAULT_BYTES:
        raise ValueError("Sealed evidence would exceed maximum vault size")
    filename = ("fvs-" + product + "-" + datetime.now(timezone.utc).strftime(
        "%Y%m%d-%H%M%S") + "-" + secrets.token_hex(5) + ".fvault")
    target = destination / filename
    # Keep ciphertext private until a complete byte-verified, fsynced,
    # no-clobber staging file can be exclusively published.
    return publish_vault(target, vault_bytes)


def restore_evidence(vault: str | Path, folder: str | Path, passphrase: str,
                     *, expected_product: str | None = None) -> Path:
    """Authenticate and restore evidence to a new exclusive private subfolder.

    Fails without writing plaintext on a bad password, altered ciphertext,
    malformed schema, invalid hashes, oversized content, or an unsafe path.
    """
    password = _password(passphrase)
    source, destination = Path(vault), Path(folder)
    if source.suffix.lower() != ".fvault":
        raise ValueError("Choose an .fvault encrypted evidence archive")
    if not destination.is_dir() or destination.is_symlink():
        raise ValueError("Choose a regular, existing restore destination folder")
    blob = _read_regular(source, MAX_VAULT_BYTES, "Encrypted archive")
    prefix_size = len(MAGIC) + SALT_SIZE + NONCE_SIZE
    if len(blob) < prefix_size + 16 or not blob.startswith(MAGIC):
        raise ValueError("Unsupported or incomplete evidence vault format")
    salt = blob[len(MAGIC):len(MAGIC) + SALT_SIZE]
    nonce = blob[len(MAGIC) + SALT_SIZE:prefix_size]
    clear = decrypt_evidence(_key(password, salt), nonce, blob[prefix_size:], blob[:prefix_size])
    payload = parse_evidence_json(clear, _unique_pairs)
    if not isinstance(payload, dict) or set(payload) != FIELDS:
        raise ValueError("Encrypted evidence has an unsupported schema")
    if type(payload["schema"]) is not int or payload["schema"] != 1:
        raise ValueError("Unsupported encrypted evidence format version")
    # Match the authenticated archive to the already-entitled GUI workflow
    # before creating any plaintext directory. Trusted unscoped API callers
    # retain backward compatibility; this check does not grant entitlement.
    require_restore_product(payload["product"], expected_product)
    if type(payload["journal_present"]) is not bool or type(payload["review_event_count"]) is not int:
        raise ValueError("Invalid encrypted evidence metadata")
    if not (0 <= payload["review_event_count"] <= 20_000):
        raise ValueError("Invalid review event count")
    _name(payload["report_filename"], ".csv")
    included = payload["journal_present"]
    if included:
        _name(payload["journal_filename"], ".jsonl")
    elif (payload["journal_filename"] is not None or payload["journal_b64"] is not None or
          payload["journal_sha256"] is not None or payload["review_event_count"]):
        raise ValueError("Inconsistent encrypted journal metadata")
    data = decode_evidence_b64(payload["report_b64"])
    journal_data = decode_evidence_b64(payload["journal_b64"]) if included else None
    if len(data) > MAX_REPORT_BYTES or (journal_data is not None and len(journal_data) > MAX_JOURNAL_BYTES):
        raise ValueError("Encrypted evidence exceeds safe restore limits")
    if not isinstance(payload["report_sha256"], str) or payload["report_sha256"] != _sha(data):
        raise ValueError("Encrypted report digest mismatch")
    if included and (not isinstance(payload["journal_sha256"], str) or
                     payload["journal_sha256"] != _sha(journal_data)):
        raise ValueError("Encrypted review journal digest mismatch")
    restored = destination / ("fvs-evidence-restored-" + datetime.now(timezone.utc).strftime(
        "%Y%m%d-%H%M%S") + "-" + secrets.token_hex(5))
    # Folder creation and metadata faults must not expose customer paths.
    owned_directory = make_private_restore_folder(restored)
    created = []
    try:
        report_file = restored / "exception-report.csv"
        files = [(report_file, data)]
        journal_file = restored / "exception-report.review.jsonl"
        if included:
            files.append((journal_file, journal_data))
        metadata_file = restored / "sealed-evidence-manifest.json"
        manifest = {k: payload[k] for k in (
            "schema", "product", "sealed_utc", "report_filename", "report_sha256",
            "journal_filename", "journal_sha256", "journal_present", "review_event_count")}
        files.append((metadata_file, (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")))
        for file, contents in files:
            write_private_restore_member(file, contents, created)
        # Check the full plaintext bundle, including the non-parsed manifest.
        verify_private_restore_members(restored, owned_directory, created, files)
        batch = read_cases(report_file, payload["product"])
        if batch.report_sha256 != payload["report_sha256"]:
            raise ValueError("Restored exception report no longer matches its evidence digest")
        restored_events = read_journal(journal_file, batch)
        if len(restored_events) != payload["review_event_count"]:
            raise ValueError("Review journal event count does not match sealed evidence")
        # Parsers may have modified files in place; do not return a changed bundle.
        verify_private_restore_members(restored, owned_directory, created, files)
    except BaseException:
        # Even interruption must attempt rollback, but never delete a
        # detectably swapped pathname or hide the original failure.
        rollback_owned_restore(restored, owned_directory, created)
        raise
    return restored
