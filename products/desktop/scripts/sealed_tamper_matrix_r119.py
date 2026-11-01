"""R119 private Windows CI: 16 real-entry AES-GCM tamper-rejection checks.

This is deliberately NOT Windows 11 human review, a malware certificate,
an independent trust anchor, premium distribution or release authorization.
It runs only on disposable, privately held Windows build candidates.
"""
from __future__ import annotations

import argparse
import contextlib
import os
from pathlib import Path
import struct
import sys
import tempfile

import sealed_candidate_handoff_r117 as handoff


class MatrixHold(ValueError):
    """A failed custody or authentication check cannot authorize release."""


def _layout(bundle: Path, pin: str) -> tuple[tuple[int, int], ...]:
    """Parse authenticated-format record offsets without decrypting bytes."""
    pin = handoff._pin(pin)
    before = handoff._regular(bundle, 6 * handoff.LIMIT + 300 * 1024)
    with bundle.open("rb") as stream:
        if stream.read(len(handoff.MAGIC)) != handoff.MAGIC:
            raise MatrixHold("Sealed bundle magic invalid")
        encoded_length = stream.read(4)
        if len(encoded_length) != 4:
            raise MatrixHold("Sealed bundle header missing")
        header_size = struct.unpack(">I", encoded_length)[0]
        if not 1 <= header_size <= handoff.HEADER_MAX:
            raise MatrixHold("Sealed bundle header size invalid")
        header_raw = stream.read(header_size)
        if len(header_raw) != header_size:
            raise MatrixHold("Sealed bundle header truncated")
        entries = handoff._check_manifest(handoff._unique_json(header_raw), pin)
        position = len(handoff.MAGIC) + 4 + header_size
        offsets = []
        for record in entries:
            ciphertext_at = position
            tag_at = ciphertext_at + record["size"]
            offsets.append((ciphertext_at, tag_at))
            position = tag_at + 16
        if stream.seek(0, os.SEEK_END) != position:
            raise MatrixHold("Sealed bundle record boundaries invalid")
    after = handoff._regular(bundle, 6 * handoff.LIMIT + 300 * 1024)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise MatrixHold("Sealed bundle changed while reading record layout")
    return tuple(offsets)


def _change_one_byte(bundle: Path, offset: int, replacement: int | None = None) -> int:
    """Change exactly one byte in the private, ordinary bundle; return old byte."""
    before = handoff._regular(bundle, 6 * handoff.LIMIT + 300 * 1024)
    if type(offset) is not int or not 0 <= offset < before.st_size:
        raise MatrixHold("Tamper position outside bundle")
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(bundle, flags)
    with os.fdopen(fd, "r+b") as stream:
        st = os.fstat(stream.fileno())
        if (st.st_dev, st.st_ino, st.st_size) != (before.st_dev, before.st_ino, before.st_size):
            raise MatrixHold("Sealed bundle substituted")
        stream.seek(offset)
        previous = stream.read(1)
        if len(previous) != 1:
            raise MatrixHold("Tamper target vanished")
        altered = (previous[0] ^ 1) if replacement is None else replacement
        if type(altered) is not int or not 0 <= altered <= 255:
            raise MatrixHold("Invalid mutation")
        stream.seek(offset)
        stream.write(bytes((altered,)))
        stream.flush()
        os.fsync(stream.fileno())
    return previous[0]


@contextlib.contextmanager
def _tamper(bundle: Path, offset: int):
    """Always restore the verified one-byte mutation, including error paths."""
    prior = _change_one_byte(bundle, offset)
    try:
        yield
    finally:
        _change_one_byte(bundle, offset, prior)


def _expect_rejection(bundle: Path, key: Path, pin: str, destination: Path):
    """A rejection is valid only if no reviewer directory was published."""
    if destination.exists() or destination.is_symlink():
        raise MatrixHold("Private review destination already occupied")
    try:
        handoff.unseal(bundle, key, pin, destination)
    except handoff.HandoffHold:
        pass
    else:
        raise MatrixHold("Tampered ciphertext or authentication tag accepted")
    if destination.exists() or destination.is_symlink():
        raise MatrixHold("Failed authentication published reviewer plaintext")


def verify_all_entry_tamper_rejection(dist, r9_report, private_root):
    """Exercise eight genuine sealed records and both byte/tag corruption paths.

    R9 digest here comes from the SAME runner; it is not an independently
    communicated reviewer pin. This is an internal, release-blocked CI test.
    """
    dist, r9_report, private_root = map(Path, (dist, r9_report, private_root))
    if not private_root.is_absolute():
        raise MatrixHold("Require an absolute private runner scratch")
    handoff._private_directory(private_root)
    repo_root = Path(__file__).resolve().parents[3]
    resolved = private_root.resolve(strict=True)
    source = dist.resolve(strict=True)
    if resolved == repo_root or repo_root in resolved.parents:
        raise MatrixHold("Private runner scratch may not be under checkout")
    if resolved == source or source in resolved.parents:
        raise MatrixHold("Private runner scratch may not be under candidate tree")

    pin = handoff._hash(r9_report)
    handoff._custody(dist, r9_report, pin)
    with tempfile.TemporaryDirectory(prefix="fvs-r119-", dir=private_root) as dirname:
        private_stage = Path(dirname)
        handoff._private_directory(private_stage)
        key = private_stage / "ephemeral.key"
        sealed = private_stage / "ephemeral.sealed"
        handoff.generate_key(key)
        result = handoff.seal(dist, r9_report, pin, key, sealed)
        if result.get("release_authorized") is not False or result.get("six_exes") != 6:
            raise MatrixHold("Unexpected sealed candidate authorization")
        original_hash = handoff._hash(sealed)
        offsets = _layout(sealed, pin)
        if len(offsets) != len(handoff.ENTRIES):
            raise MatrixHold("Must test all eight authenticated records")

        case_count = 0
        for index, (cipher_at, tag_at) in enumerate(offsets):
            for kind, position in (("cipher", cipher_at), ("tag", tag_at)):
                intake = private_stage / f"rejected-{index}-{kind}"
                with _tamper(sealed, position):
                    _expect_rejection(sealed, key, pin, intake)
                if handoff._hash(sealed) != original_hash:
                    raise MatrixHold("Tamper test did not restore sealed bytes")
                case_count += 1
        handoff._custody(dist, r9_report, pin)

    if list(private_root.glob("fvs-r119-*")):
        raise MatrixHold("Ephemeral candidate bundle or key survived")
    if case_count != 16:
        raise MatrixHold("Incomplete real-record tamper coverage")
    return {"status": "CI_EPHEMERAL_ALL_ENTRY_TAMPER_REJECTION_ONLY",
            "private_records_checked": 8, "tamper_cases_rejected": case_count,
            "six_exes": 6, "independent_r9_pin": False,
            "physical_windows11_acceptance": False,
            "premium_distribution_authorized": False,
            "release_authorized": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist")
    parser.add_argument("r9_report")
    parser.add_argument("private_root")
    args = parser.parse_args(argv)
    try:
        result = verify_all_entry_tamper_rejection(
            args.dist, args.r9_report, args.private_root)
    except (OSError, ValueError, RuntimeError, TypeError):
        print("R119 HOLD: private candidate authentication matrix failed; "
              "no release permission", file=sys.stderr)
        return 1
    if result["tamper_cases_rejected"] != 16 or result["release_authorized"] is not False:
        return 1
    print("R119 PASS: eight private records, 16 ciphertext/tag mutations "
          "rejected with no published intake; ephemeral keys/bundle removed. "
          "NO release or physical Windows 11 clearance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
