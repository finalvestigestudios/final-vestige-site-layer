#!/usr/bin/env python3
"""R105 deterministic, non-extracting transport gate for PRIVATE R104 source packets.

An archive is a byte-for-byte carrier, not a source or human-review attestation.
Never network, CMS, publishing, review promotion, extraction or repo writes.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import stat
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r104_review_export_custody as parent

SCHEMA = "r105-deterministic-private-source-transport-v1"
ZIP_NAME = "r105-private-source-citation-packet-HOLD.zip"
DOS_TIME = (1980, 1, 1, 0, 0, 0)
MODE = (stat.S_IFREG | 0o600) << 16
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
NAMES = tuple([name for name, _ in parent.EXPORTS] + [parent.MANIFEST])


class Gate(ValueError):
    """Fail closed on original evidence, archive, or release custody drift."""


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Gate(reason)


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def original_payload() -> dict[str, bytes]:
    """Always re-read and independently reconstruct original authored records."""
    result = parent.create_payload(parent.original_packet())
    need(tuple(result) == NAMES and len(result) == 5
         and all(type(v) is bytes and 0 < len(v) <= parent.MAX_FILE_BYTES
                 for v in result.values()), "R104 original packet roster drift")
    manifest = json.loads(result[parent.MANIFEST])
    need(manifest["release_state"] == "HOLD"
         and manifest["may_publish"] is False
         and manifest["may_merge"] is False
         and manifest["unreviewed_literal_url_groups"] == 30
         and manifest["original_article_drafts"] == 35
         and manifest["complete_tool_drafts"] == 1
         and manifest["unfinished_tools"] == 5
         and manifest["human_source_review"] == "NOT_REVIEWED"
         and manifest["human_claim_review"] == "NOT_REVIEWED"
         and manifest["qualified_safety_review"] == "NOT_REVIEWED"
         and manifest["independent_QD"] == "NOT_REVIEWED",
         "original corpus or review/safety HOLD state drift")
    return result


def encode_zip(payload: dict[str, bytes]) -> bytes:
    """Pure deterministic encoder. Caller MUST provide independently replayed R104 bytes."""
    need(type(payload) is dict and tuple(payload) == NAMES,
         "out-of-order, added or missing R104 files")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_STORED,
                         allowZip64=False) as zf:
        for name in NAMES:
            body = payload[name]
            need(type(body) is bytes and 0 < len(body) <= parent.MAX_FILE_BYTES,
                 "invalid or oversized source evidence")
            info = zipfile.ZipInfo(name, date_time=DOS_TIME)
            info.create_system = 3
            info.external_attr = MODE
            info.compress_type = zipfile.ZIP_STORED
            info.extra = b""
            info.comment = b""
            zf.writestr(info, body)
    raw = buf.getvalue()
    need(0 < len(raw) <= MAX_ARCHIVE_BYTES,
         "oversized/private evidence archive")
    return raw


def original_archive() -> bytes:
    return encode_zip(original_payload())


def verify_bytes(raw: bytes, *, expected: bytes | None = None,
                 expected_payload: dict[str, bytes] | None = None) -> dict:
    """Parse without extraction, then verify exact independently replayed archive.

    Optional expected parameters are for internal synthetic tests; production
    callers must omit them so original source records are replayed every time.
    """
    need(type(raw) is bytes and 0 < len(raw) <= MAX_ARCHIVE_BYTES,
         "missing or oversized ZIP evidence")
    payload = original_payload() if expected_payload is None else expected_payload
    reference = encode_zip(payload) if expected is None else expected
    need(tuple(payload) == NAMES and type(reference) is bytes,
         "invalid expected original evidence")
    try:
        with zipfile.ZipFile(io.BytesIO(raw), mode="r", allowZip64=False) as zf:
            infos = zf.infolist()
            need(zf.comment == b"" and len(infos) == len(NAMES),
                 "ZIP archive comment, duplicate or missing evidence entry")
            need(tuple(x.filename for x in infos) == NAMES,
                 "ZIP entry order, name, traversal or alias mismatch")
            for member, name in zip(infos, NAMES):
                body = payload[name]
                need(member.filename == name and not member.is_dir()
                     and member.date_time == DOS_TIME
                     and member.compress_type == zipfile.ZIP_STORED
                     and member.file_size == len(body)
                     and member.compress_size == len(body)
                     and member.file_size <= parent.MAX_FILE_BYTES
                     and member.create_system == 3 and member.external_attr == MODE
                     and member.flag_bits == 0 and member.extra == b""
                     and member.comment == b"",
                     "ZIP unsafe metadata, compression, or content length: " + name)
                observed = zf.read(member)
                need(len(observed) == len(body)
                     and hmac.compare_digest(digest(observed), digest(body))
                     and observed == body,
                     "ZIP source/citation bytes changed: " + name)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError,
            RuntimeError, OSError, NotImplementedError) as exc:
        raise Gate("invalid private ZIP: " + type(exc).__name__) from exc
    need(len(raw) == len(reference)
         and hmac.compare_digest(digest(raw), digest(reference))
         and raw == reference,
         "ZIP byte stream, extra fields, preamble, footer or custody drift")
    return {"schema": SCHEMA, "release_state": "HOLD",
            "verification": "EXACT_UNAPPROVED_SOURCE_PACKET_CUSTODY",
            "archive_bytes": len(raw), "archive_sha256": digest(raw),
            "entries": len(NAMES), "original_articles": 35,
            "complete_tools": 1, "unfinished_tools": 5,
            "source_url_groups_pending_human_review": 30,
            "human_source_claim_safety_and_QD_review": "NOT_REVIEWED",
            "may_publish": False, "may_merge": False}


def verify_file(raw_path: str) -> dict:
    target = Path(raw_path)
    need(target.name == ZIP_NAME and not target.is_symlink()
         and target.is_file(), "not a regular, correctly named source ZIP")
    directory = parent.safe_directory(str(target.parent))
    path = directory / ZIP_NAME
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and
             0 < info.st_size <= MAX_ARCHIVE_BYTES,
             "not a bounded regular source archive")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            raw = handle.read(MAX_ARCHIVE_BYTES + 1)
        need(len(raw) == info.st_size, "truncated or changed private source ZIP")
    finally:
        os.close(fd)
    # The on-disk manifest is NOT the anchor; reconstruct every original record.
    return verify_bytes(raw)


def emit_dir(raw_dir: str) -> dict:
    directory = parent.safe_directory(raw_dir)
    need(not any(directory.iterdir()),
         "export requires a pre-existing EMPTY private scratch directory")
    raw = original_archive()
    target = directory / ZIP_NAME
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(raw)
            file.flush()
            os.fsync(file.fileno())
        return verify_file(str(target))
    except Exception:
        try:
            target.unlink()
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    option = parser.add_mutually_exclusive_group(required=True)
    option.add_argument("--dry-check", action="store_true")
    option.add_argument("--emit-dir", metavar="EMPTY_PRIVATE_SCRATCH_DIR")
    option.add_argument("--verify-zip", metavar="EXISTING_PRIVATE_ZIP")
    args = parser.parse_args(argv)
    if args.emit_dir:
        result = emit_dir(args.emit_dir)
    elif args.verify_zip:
        result = verify_file(args.verify_zip)
    else:
        result = verify_bytes(original_archive())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Gate, parent.Gate, ValueError, TypeError, KeyError,
            OSError, zipfile.BadZipFile) as error:
        print("R105 PRIVATE HOLD: " + str(error), file=sys.stderr)
        raise SystemExit(2)
