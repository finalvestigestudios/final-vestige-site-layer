"""Local-only, read-only inspection of restored premium evidence bundles.

This checks internal consistency of the plaintext bundle emitted by the premium
AES-GCM restore flow; the plaintext manifest is NOT a signature. An attacker
able to edit both files and manifest can forge a consistent bundle. This does
not authenticate the encrypted source, license, reviewer, or compliance result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from datetime import datetime

REPORT = "exception-report.csv"
JOURNAL = "exception-report.review.jsonl"
MANIFEST = "sealed-evidence-manifest.json"
MAX_BYTES = {REPORT: 64 * 1024 * 1024, JOURNAL: 16 * 1024 * 1024,
             MANIFEST: 64 * 1024}
FIELDS = frozenset(("schema", "product", "sealed_utc", "report_filename",
                    "report_sha256", "journal_filename", "journal_sha256",
                    "journal_present", "review_event_count"))
ERROR = "Private evidence bundle failed consistency verification"
HEX = re.compile(r"[a-f0-9]{64}\Z")
_BLOCK = 256 * 1024
MAX_EVENTS = 20_000


class BundleHold(ValueError):
    """A fixed, private-path-free, non-release verification failure."""


def _identity(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def _folder_identity(folder: Path):
    info = os.lstat(folder)
    if not stat.S_ISDIR(info.st_mode) or info.st_ino == 0:
        raise ValueError(ERROR)
    return _identity(info)


def _inventory(folder: Path, directory_id, allowed: set[str]):
    if _folder_identity(folder) != directory_id:
        raise ValueError(ERROR)
    names = os.listdir(folder)
    if (len(names) != len(allowed) or set(names) != allowed):
        raise ValueError(ERROR)
    if _folder_identity(folder) != directory_id:
        raise ValueError(ERROR)


def _read_member(folder: Path, directory_id, filename: str, *, materialize=False):
    """Bounded descriptor read, with before/after file and directory custody.

    No user-controlled filename reaches this helper: callers select constants.
    Rechecking the path AFTER closing is a best-effort TOCTOU detection, not an
    OS-level lock against a hostile simultaneous writer.
    Nonblocking descriptor opening prevents a raced POSIX FIFO hang.
    """
    if _folder_identity(folder) != directory_id:
        raise ValueError(ERROR)
    path = folder / filename
    before = os.lstat(path)
    if (not stat.S_ISREG(before.st_mode) or before.st_ino == 0 or
            before.st_nlink != 1 or not 0 <= before.st_size <= MAX_BYTES[filename]):
        raise ValueError(ERROR)
    # lstat() and os.open() are separate operations: a concurrent writer can
    # replace a checked regular member with a FIFO. O_NONBLOCK prevents a
    # POSIX FIFO reader from hanging; fstat identity/type custody still
    # rejects the replacement. Windows native acceptance remains required.
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
             getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        if _identity(opened) != _identity(before):
            raise ValueError(ERROR)
        digest = hashlib.sha256()
        chunks = [] if materialize else None
        size = 0
        while True:
            chunk = os.read(fd, min(_BLOCK, MAX_BYTES[filename] + 1 - size))
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_BYTES[filename] or size > before.st_size:
                raise ValueError(ERROR)
            digest.update(chunk)
            if materialize:
                chunks.append(chunk)
        if size != before.st_size or _identity(os.fstat(fd)) != _identity(before):
            raise ValueError(ERROR)
    finally:
        os.close(fd)
    if (_identity(os.lstat(path)) != _identity(before) or
            _folder_identity(folder) != directory_id):
        raise ValueError(ERROR)
    return digest.hexdigest(), b"".join(chunks) if materialize else None


def _unique(pairs):
    result = {}
    for key, val in pairs:
        if key in result:
            raise ValueError(ERROR)
        result[key] = val
    return result


def _reject_constant(_):
    raise ValueError(ERROR)


def _source_name(value, suffix):
    return (type(value) is str and 1 <= len(value) <= 255 and
            value.lower().endswith(suffix) and value not in (".", "..") and
            not any(ord(char) < 32 or ord(char) == 127 or char in "/\\:" for char in value))


def _manifest(raw: bytes):
    entry = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique,
                       parse_constant=_reject_constant)
    if type(entry) is not dict or set(entry) != FIELDS:
        raise ValueError(ERROR)
    if type(entry["schema"]) is not int or entry["schema"] != 1:
        raise ValueError(ERROR)
    if type(entry["product"]) is not str or entry["product"] not in ("grants", "procurement"):
        raise ValueError(ERROR)
    if not _source_name(entry["report_filename"], ".csv"):
        raise ValueError(ERROR)
    if type(entry["sealed_utc"]) is not str or len(entry["sealed_utc"]) > 40:
        raise ValueError(ERROR)
    timestamp = datetime.fromisoformat(entry["sealed_utc"])
    if timestamp.utcoffset() is None:
        raise ValueError(ERROR)
    if type(entry["report_sha256"]) is not str or not HEX.fullmatch(entry["report_sha256"]):
        raise ValueError(ERROR)
    if type(entry["journal_present"]) is not bool or type(entry["review_event_count"]) is not int:
        raise ValueError(ERROR)
    if not 0 <= entry["review_event_count"] <= 20_000:
        raise ValueError(ERROR)
    if entry["journal_present"]:
        if (not _source_name(entry["journal_filename"], ".jsonl") or
                type(entry["journal_sha256"]) is not str or
                not HEX.fullmatch(entry["journal_sha256"])):
            raise ValueError(ERROR)
    elif (entry["journal_filename"] is not None or
          entry["journal_sha256"] is not None or entry["review_event_count"] != 0):
        raise ValueError(ERROR)
    return entry


def _verify_journal_structure(data: bytes, expected_count: int) -> int:
    """Confirm bounded JSONL framing and manifest count using witnessed bytes.

    Structural consistency only: this is NOT journal chain authentication,
    proof of an actual reviewer or a compliance or release authorization.
    Authenticated vault restore still checks all review-event hashes and case
    binding with the source report before an evidence bundle is accepted.
    """
    if (type(data) is not bytes or type(expected_count) is not int or
            not 0 <= expected_count <= MAX_EVENTS or
            len(data) > MAX_BYTES[JOURNAL]):
        raise ValueError(ERROR)
    if data and not data.endswith(b"\n"):
        raise ValueError(ERROR)
    # Only LF and CRLF are JSONL record separators. bytes.splitlines() also
    # accepts bare CR, creating ambiguous audit record boundaries.
    records = data[:-1].split(b"\n") if data else []
    if len(records) != expected_count:
        raise ValueError(ERROR)
    for record in records:
        if record.endswith(b"\r"):
            record = record[:-1]
        if not record or b"\x00" in record or b"\r" in record:
            raise ValueError(ERROR)
        try:
            event = json.loads(record.decode("utf-8"),
                               object_pairs_hook=_unique,
                               parse_constant=_reject_constant,
                               parse_float=_reject_constant)
            # The supported premium review writer produces integer-only
            # numeric fields and Unicode scalar text. Reject escaped lone
            # surrogates instead of treating them as valid review evidence.
            json.dumps(event, ensure_ascii=False).encode("utf-8")
        except (ValueError, UnicodeError, RecursionError):
            raise ValueError(ERROR) from None
        if type(event) is not dict:
            raise ValueError(ERROR)
    return len(records)


def inspect_bundle(path: str | Path) -> dict[str, object]:
    """Inspect immutable-at-observation bundle bytes; never write or decrypt.

    Return evidence of two internally consistent read passes. This is an
    UNAUTHENTICATED consistency check and NOT a release or compliance decision.
    The source vault must be authenticated independently with the passphrase.
    """
    failed = False
    try:
        folder = Path(path)
        directory_id = _folder_identity(folder)
        manifest_digest, manifest_raw = _read_member(folder, directory_id, MANIFEST,
                                                      materialize=True)
        meta = _manifest(manifest_raw)
        allowed = {REPORT, MANIFEST} | ({JOURNAL} if meta["journal_present"] else set())
        _inventory(folder, directory_id, allowed)
        checks = {}
        for name in (REPORT, JOURNAL) if meta["journal_present"] else (REPORT,):
            checks[name] = _read_member(folder, directory_id, name)[0]
        if checks[REPORT] != meta["report_sha256"] or (meta["journal_present"] and
                checks[JOURNAL] != meta["journal_sha256"]):
            raise ValueError(ERROR)
        # Re-read the entire report/journal to catch observed mutations after
        # the first hash and ensure the manifest remained byte-identical.
        for name, digest in checks.items():
            observed, snapshot = _read_member(folder, directory_id, name,
                                              materialize=(name == JOURNAL))
            if observed != digest:
                raise ValueError(ERROR)
            if name == JOURNAL:
                # A matching file digest alone does not establish that the
                # manifest's claimed event count reflects the JSONL records.
                # Use the custody-checked second pass, never a raw path read.
                _verify_journal_structure(snapshot, meta["review_event_count"])
        if _read_member(folder, directory_id, MANIFEST)[0] != manifest_digest:
            raise ValueError(ERROR)
        _inventory(folder, directory_id, allowed)
        return {"schema": "fvs-restored-bundle-check-r320-v1",
                "product": meta["product"], "report_sha256": checks[REPORT],
                "journal_sha256": checks.get(JOURNAL),
                "members_verified": len(allowed), "source_authenticated": False,
                "review_required": True, "compliance_approved": False,
                "release_authorized": False}
    except Exception:
        # Deliberately re-raise OUTSIDE the except block to prevent leaking
        # private source paths in chained exception context / tracebacks.
        failed = True
    if failed:
        raise BundleHold(ERROR)
    raise BundleHold(ERROR)



def inspect_with_external_witness(path: str | Path, *, product: str,
                                  report_sha256: str,
                                  journal_sha256: str | None) -> dict[str, object]:
    """Match inspected bytes to a separately held, operator-supplied SHA-256 witness.

    `None` for journal_sha256 explicitly requires that NO journal be present.
    The witness must come from a trusted, independent channel to have evidential
    value. Matching hashes do not authenticate the vault, signer, or reviewer.
    Neither the witness nor the folder is modified or transmitted.
    """
    if (type(product) is not str or product not in ("grants", "procurement") or
            type(report_sha256) is not str or not HEX.fullmatch(report_sha256) or
            (journal_sha256 is not None and
             (type(journal_sha256) is not str or not HEX.fullmatch(journal_sha256)))):
        raise BundleHold(ERROR)
    result = inspect_bundle(path)
    if (result["product"] != product or
            result["report_sha256"] != report_sha256 or
            result["journal_sha256"] != journal_sha256):
        raise BundleHold(ERROR)
    return {**result, "external_witness_matched": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only local premium restored-bundle consistency check")
    parser.add_argument("folder", type=Path, help="Local restored evidence folder (never uploaded)")
    parser.add_argument("--expect-product", choices=("grants", "procurement"))
    parser.add_argument("--expect-report-sha256")
    journal = parser.add_mutually_exclusive_group()
    journal.add_argument("--expect-journal-sha256")
    journal.add_argument("--expect-no-journal", action="store_true")
    args = parser.parse_args(argv)
    witness_mode = (args.expect_product is not None or
                    args.expect_report_sha256 is not None or
                    args.expect_journal_sha256 is not None or args.expect_no_journal)
    try:
        if witness_mode:
            # A partial witness is never silently downgraded to consistency-only.
            if (args.expect_product is None or args.expect_report_sha256 is None or
                    (args.expect_journal_sha256 is None and not args.expect_no_journal)):
                raise BundleHold(ERROR)
            result = inspect_with_external_witness(
                args.folder, product=args.expect_product,
                report_sha256=args.expect_report_sha256,
                journal_sha256=args.expect_journal_sha256)
        else:
            result = inspect_bundle(args.folder)
    except BundleHold:
        print("HOLD: evidence bundle failed; no authentication or review approval", file=sys.stderr)
        return 1
    phrase = ("matches operator-supplied SHA-256 witness" if witness_mode
              else "bundle internally consistent")
    print("PASS: " + result["product"] + " " + phrase + "; "
          "NOT AUTHENTICATED; human review and QD/founder HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
