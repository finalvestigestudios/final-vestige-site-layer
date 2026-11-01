"""Offline encrypted custody handoff for six UNRELEASED Windows x64 candidates.

Not a release, license, AV clearance, code-signing certificate, or independent
review. No key material in flags, environment variables, metadata, or reports.
An independent R9 SHA-256 pin is mandatory on both endpoints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import stat
import struct
import sys
import tempfile

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b"FV-LABS-R117-SEALED\n"
SCHEMA = "fv-labs-six-exe-sealed-handoff-r117-v1"
NAMES = ("LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
         "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe")
ENTRIES = tuple("exes/" + n for n in NAMES) + (
    "exes/SHA256SUMS.txt", "evidence/r9-report.json")
LIMIT = 512 * 1024 * 1024
CAPS = (LIMIT,) * 6 + (8192, 256 * 1024)
HEADER_MAX = 8192
CHUNK = 1024 * 1024
HEX = set("0123456789abcdef")


class HandoffHold(ValueError):
    """No release or transfer clearance may be inferred from failure."""


def _hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for part in iter(lambda: stream.read(CHUNK), b""):
            h.update(part)
    return h.hexdigest()


def _pin(value):
    if type(value) is not str or len(value) != 64 or any(c not in HEX for c in value):
        raise HandoffHold("Independent lowercase R9 SHA-256 pin required")
    return value


def _private_directory(parent):
    if not parent.is_dir() or parent.is_symlink():
        raise HandoffHold("Require ordinary existing parent directory")
    if os.name != "nt" and (parent.stat().st_mode & 0o077):
        raise HandoffHold("Private parent must be owner-only (0700) on POSIX")


def _regular(path, cap):
    if path.is_symlink():
        raise HandoffHold("Symlink custody denied")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 1 <= before.st_size <= cap:
        raise HandoffHold("Input size/identity outside custody policy")
    return before


def _same_file(path, before):
    after = _regular(path, LIMIT)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise HandoffHold("Input changed during encrypted transfer")


def _key(path):
    if not path.is_absolute():
        raise HandoffHold("Key file path must be absolute")
    before = _regular(path, 32)
    if before.st_size != 32 or (os.name != "nt" and (before.st_mode & 0o077)):
        raise HandoffHold("Key must be exactly 32 private bytes")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        stat_fd = os.fstat(fd)
        if (stat_fd.st_dev, stat_fd.st_ino, stat_fd.st_size) != (
                before.st_dev, before.st_ino, before.st_size):
            raise HandoffHold("Key substituted")
        raw = os.read(fd, 33)
        if len(raw) != 32:
            raise HandoffHold("Key length changed")
    finally:
        os.close(fd)
    _same_file(path, before)
    return raw


def _unique_json(raw):
    def no_duplicates(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise HandoffHold("Duplicate transfer metadata key")
            value[key] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=no_duplicates)
    except (ValueError, UnicodeError):
        raise HandoffHold("Invalid transfer metadata") from None


def _manifest(paths, expected_r9):
    entries = []
    used = set()
    for name, cap in zip(ENTRIES, CAPS):
        path = paths[name]
        identity = _regular(path, cap)
        nonce = secrets.token_bytes(12)
        if nonce in used:
            raise HandoffHold("Repeated nonce")
        used.add(nonce)
        entries.append({"name": name, "size": identity.st_size,
                        "sha256": _hash(path), "nonce": nonce.hex()})
        _same_file(path, identity)
    if entries[-1]["sha256"] != expected_r9:
        raise HandoffHold("R9 source evidence changed")
    return {"schema": SCHEMA, "release_authorized": False,
            "premium_distribution_authorized": False,
            "r9_report_sha256": expected_r9, "entries": entries}


def _check_manifest(header, expected_r9):
    if not isinstance(header, dict) or set(header) != {
            "schema", "release_authorized", "premium_distribution_authorized",
            "r9_report_sha256", "entries"} or header["schema"] != SCHEMA or (
            header["release_authorized"] is not False or
            header["premium_distribution_authorized"] is not False) or (
            header["r9_report_sha256"] != expected_r9):
        raise HandoffHold("Transfer header not bound to pinned candidate evidence")
    records = header["entries"]
    if type(records) is not list or len(records) != len(ENTRIES):
        raise HandoffHold("Incomplete six-app handoff")
    nonces = set()
    for item, name, cap in zip(records, ENTRIES, CAPS):
        if (type(item) is not dict or set(item) != {"name", "size", "sha256", "nonce"}
                or item["name"] != name or type(item["size"]) is not int
                or not 1 <= item["size"] <= cap or
                type(item["sha256"]) is not str or len(item["sha256"]) != 64
                or any(c not in HEX for c in item["sha256"]) or
                type(item["nonce"]) is not str or len(item["nonce"]) != 24
                or any(c not in HEX for c in item["nonce"]) or
                item["nonce"] in nonces):
            raise HandoffHold("Unexpected or duplicated sealed file metadata")
        nonces.add(item["nonce"])
    if records[-1]["sha256"] != expected_r9:
        raise HandoffHold("Independent R9 pin mismatch")
    return records


def _custody(root, r9, expected):
    # Existing R9 attestation checks real PE/SHA files against six R9 smokes.
    # The CLI is invoked from scripts/, but report_attestation lives in desktop/.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from report_attestation import verify_report, _read_verified_report, _validate_report
    try:
        proof = verify_report(r9, root, expected_report_sha256=expected)
        raw, fingerprint = _read_verified_report(r9, root)
        historical = _validate_report(raw)
        if (proof.get("candidate_consistency") != "PASS"
                or proof.get("evidence_pin") != "PINNED"
                or fingerprint != expected
                or historical.get("status") != "windows_smoke_passed"
                or historical.get("windows_executables_verified") is not True
                or historical.get("smoke_simulated") is not False):
            raise HandoffHold("Six genuinely smoke-checked candidates are required")
    except (OSError, ValueError, KeyError):
        raise HandoffHold("Six-candidate R9 custody unavailable") from None


def _paths(root, r9):
    return {**{"exes/" + name: root / name for name in NAMES},
            "exes/SHA256SUMS.txt": root / "SHA256SUMS.txt",
            "evidence/r9-report.json": r9}


def seal(dist, r9, expected_r9, key_file, destination):
    expected_r9 = _pin(expected_r9)
    dist, r9, destination = Path(dist), Path(r9), Path(destination)
    _private_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        raise HandoffHold("Never overwrite a sealed handoff")
    key = _key(Path(key_file))
    _custody(dist, r9, expected_r9)
    paths = _paths(dist, r9)
    header = _manifest(paths, expected_r9)
    raw = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("ascii")
    if len(raw) > HEADER_MAX:
        raise HandoffHold("Handoff metadata too large")
    fd, temporary = tempfile.mkstemp(prefix=".fvs-sealed-", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(MAGIC + struct.pack(">I", len(raw)) + raw)
            for index, item in enumerate(header["entries"]):
                path = paths[item["name"]]
                before = _regular(path, CAPS[index])
                encryptor = Cipher(algorithms.AES(key),
                                   modes.GCM(bytes.fromhex(item["nonce"]))).encryptor()
                encryptor.authenticate_additional_data(raw + index.to_bytes(2, "big"))
                digest = hashlib.sha256()
                total = 0
                with open(path, "rb") as inp:
                    while True:
                        chunk = inp.read(CHUNK)
                        if not chunk:
                            break
                        total += len(chunk)
                        digest.update(chunk)
                        target.write(encryptor.update(chunk))
                target.write(encryptor.finalize() + encryptor.tag)
                if total != item["size"] or digest.hexdigest() != item["sha256"]:
                    raise HandoffHold("Candidate bytes changed during encryption")
                _same_file(path, before)
            target.flush()
            os.fsync(target.fileno())
        _custody(dist, r9, expected_r9)
        os.link(temporary, destination)  # exclusive; no replace or clobber
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {"status": "ENCRYPTED_PRIVATE_HANDOFF_ONLY", "six_exes": 6,
            "release_authorized": False}


def unseal(bundle, key_file, expected_r9, destination):
    expected_r9 = _pin(expected_r9)
    bundle, destination = Path(bundle), Path(destination)
    _private_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        raise HandoffHold("Never overwrite a reviewer intake")
    _regular(bundle, 6 * LIMIT + 300 * 1024)
    key = _key(Path(key_file))
    temp = Path(tempfile.mkdtemp(prefix=".fvs-intake-", dir=destination.parent))
    try:
        with open(bundle, "rb") as stream:
            if stream.read(len(MAGIC)) != MAGIC:
                raise HandoffHold("Unrecognized sealed handoff format")
            count = stream.read(4)
            if len(count) != 4:
                raise HandoffHold("Truncated transfer header")
            length = struct.unpack(">I", count)[0]
            if not 1 <= length <= HEADER_MAX:
                raise HandoffHold("Unbounded sealed metadata")
            raw = stream.read(length)
            if len(raw) != length:
                raise HandoffHold("Truncated transfer metadata")
            records = _check_manifest(_unique_json(raw), expected_r9)
            for index, item in enumerate(records):
                out = temp / item["name"]
                out.parent.mkdir(parents=True, exist_ok=True)
                remaining = item["size"]
                # The tag follows ciphertext of precisely the recorded size.
                # No unverified plaintext is published out of the staging area.
                with tempfile.TemporaryFile() as ciphertext:
                    while remaining:
                        chunk = stream.read(min(CHUNK, remaining))
                        if not chunk:
                            raise HandoffHold("Truncated encrypted candidate")
                        ciphertext.write(chunk)
                        remaining -= len(chunk)
                    tag = stream.read(16)
                    if len(tag) != 16:
                        raise HandoffHold("Missing authentication tag")
                    decryptor = Cipher(algorithms.AES(key), modes.GCM(
                        bytes.fromhex(item["nonce"]), tag)).decryptor()
                    decryptor.authenticate_additional_data(raw + index.to_bytes(2, "big"))
                    digest = hashlib.sha256()
                    ciphertext.seek(0)
                    with open(out, "xb") as dest:
                        for encrypted in iter(lambda: ciphertext.read(CHUNK), b""):
                            clear = decryptor.update(encrypted)
                            digest.update(clear)
                            dest.write(clear)
                        try:
                            tail = decryptor.finalize()
                        except InvalidTag:
                            raise HandoffHold("Transfer authentication failed") from None
                        digest.update(tail)
                        dest.write(tail)
                        dest.flush()
                        os.fsync(dest.fileno())
                if digest.hexdigest() != item["sha256"]:
                    raise HandoffHold("Decrypted candidate hash mismatch")
            if stream.read(1):
                raise HandoffHold("Trailing bytes after sealed candidates")
        _custody(temp / "exes", temp / "evidence" / "r9-report.json", expected_r9)
        if destination.exists() or destination.is_symlink():
            raise HandoffHold("Reviewer destination became occupied")
        os.rename(temp, destination)
        return {"status": "PRIVATE_REVIEWER_INTAKE_UNCERTIFIED",
                "six_exes": 6, "release_authorized": False}
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def generate_key(destination):
    destination = Path(destination)
    _private_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        raise HandoffHold("Key file already exists")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    fd = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(secrets.token_bytes(32))
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return {"status": "PRIVATE_KEY_CREATED_DO_NOT_UPLOAD", "release_authorized": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("keygen", "seal", "unseal"))
    parser.add_argument("--key-file", required=True, type=Path)
    parser.add_argument("--dist", type=Path)
    parser.add_argument("--r9-report", type=Path)
    parser.add_argument("--expected-r9-sha256")
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "keygen":
            if args.output or args.bundle or args.dist or args.r9_report or args.expected_r9_sha256:
                raise HandoffHold("Key generation accepts only --key-file")
            result = generate_key(args.key_file)
        elif args.action == "seal":
            if not all((args.dist, args.r9_report, args.expected_r9_sha256, args.bundle)):
                raise HandoffHold("Seal requires exact candidate, R9, key and output")
            result = seal(args.dist, args.r9_report, args.expected_r9_sha256,
                          args.key_file, args.bundle)
        else:
            if not all((args.bundle, args.expected_r9_sha256, args.output)):
                raise HandoffHold("Unseal requires sealed input, independent R9 pin, key and destination")
            result = unseal(args.bundle, args.key_file, args.expected_r9_sha256, args.output)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (HandoffHold, OSError, ValueError, TypeError):
        print("HOLD: six-app private handoff incomplete; NO release authorization", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
