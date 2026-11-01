"""R118 native Windows CI-only end-to-end check of six PRIVATE executable bytes.

This is an ephemeral, same-runner integration check, NOT an independent
reviewer handoff, independent R9 evidence pin, Windows 11 acceptance, AV
clearance, premium authorization, or release approval. Nothing is uploaded.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import struct
import sys
import tempfile

import sealed_candidate_handoff_r117 as handoff


class RoundtripHold(ValueError):
    """No successful release/transfer assertion can follow a failed check."""


def _snapshot(paths):
    """Capture all eight source identities and digests without copying bytes."""
    result = {}
    for name, cap in zip(handoff.ENTRIES, handoff.CAPS):
        path = paths[name]
        before = handoff._regular(path, cap)
        digest = handoff._hash(path)
        handoff._same_file(path, before)
        result[name] = (before.st_size, digest)
    return result


def _same_snapshot(before, paths):
    if before != _snapshot(paths):
        raise RoundtripHold("Six-executable source or intake bytes diverged")


def _corrupt_first_ciphertext(bundle):
    """Mutate one encrypted data byte, not the header or its metadata."""
    with bundle.open("r+b") as stream:
        if stream.read(len(handoff.MAGIC)) != handoff.MAGIC:
            raise RoundtripHold("Unexpected transfer format")
        size_bytes = stream.read(4)
        if len(size_bytes) != 4:
            raise RoundtripHold("Unexpected transfer framing")
        header_size = struct.unpack(">I", size_bytes)[0]
        if not 1 <= header_size <= handoff.HEADER_MAX:
            raise RoundtripHold("Unbounded transfer header")
        stream.seek(header_size, os.SEEK_CUR)
        offset = stream.tell()
        original = stream.read(1)
        if len(original) != 1:
            raise RoundtripHold("Missing first candidate ciphertext")
        stream.seek(offset)
        stream.write(bytes((original[0] ^ 1,)))
        stream.flush()
        os.fsync(stream.fileno())


def verify_native_roundtrip(dist, r9_report, work_root):
    """Exercise real R117 seal/unseal + tamper rejection against R9-pinned EXEs.

    The R9 digest is generated locally from this very CI run. It is NOT an
    independent cross-device pin and must never be presented as such.
    """
    dist, r9_report, work_root = Path(dist), Path(r9_report), Path(work_root)
    if not work_root.is_absolute():
        raise RoundtripHold("Require an absolute runner-private scratch directory")
    handoff._private_directory(work_root)

    # CI scratch may not be placed in the checkout: never risk its inclusion in
    # source scans, accidental source commits, or later artifact globs.
    repo_root = Path(__file__).resolve().parents[3]
    resolved = work_root.resolve(strict=True)
    if resolved == repo_root or repo_root in resolved.parents:
        raise RoundtripHold("Private scratch must be outside the repository")
    source_root = dist.resolve(strict=True)
    if resolved == source_root or source_root in resolved.parents:
        raise RoundtripHold("Private scratch must not be nested under candidates")

    pin = handoff._hash(r9_report)
    handoff._custody(dist, r9_report, pin)  # Actual R9/PE/inventory gate.
    baseline = _snapshot(handoff._paths(dist, r9_report))

    stage_path = None
    with tempfile.TemporaryDirectory(prefix="fvs-r118-", dir=work_root) as name:
        stage = Path(name)
        stage_path = stage
        handoff._private_directory(stage)
        key = stage / "local-test.key"
        bundle = stage / "local-test.sealed"
        intake = stage / "local-test-intake"

        handoff.generate_key(key)
        sealed = handoff.seal(dist, r9_report, pin, key, bundle)
        if sealed.get("release_authorized") is not False or sealed.get("six_exes") != 6:
            raise RoundtripHold("Sealing supplied an unacceptable release assertion")
        unpacked = handoff.unseal(bundle, key, pin, intake)
        if unpacked.get("release_authorized") is not False or unpacked.get("six_exes") != 6:
            raise RoundtripHold("Unsealing supplied an unacceptable release assertion")

        _same_snapshot(baseline, handoff._paths(intake / "exes",
                                                intake / "evidence" / "r9-report.json"))
        _same_snapshot(baseline, handoff._paths(dist, r9_report))

        # An authenticator that accepts modified *real* executable ciphertext
        # cannot pass this end-to-end gate, even if synthetic tests pass.
        _corrupt_first_ciphertext(bundle)
        corrupted_intake = stage / "corrupted-intake"
        try:
            handoff.unseal(bundle, key, pin, corrupted_intake)
        except handoff.HandoffHold:
            pass
        else:
            raise RoundtripHold("Modified executable ciphertext was accepted")
        if corrupted_intake.exists() or corrupted_intake.is_symlink():
            raise RoundtripHold("Failed decryption left a published intake")
        _same_snapshot(baseline, handoff._paths(dist, r9_report))

    if stage_path is not None and stage_path.exists():
        raise RoundtripHold("Ephemeral key, bundle or candidate staging survived cleanup")
    return {
        "status": "CI_EPHEMERAL_REAL_EXE_ROUNDTRIP_ONLY",
        "candidate_count": 6,
        "verified_private_entries": 8,
        "ciphertext_tamper_rejected": True,
        "independent_r9_pin": False,
        "physical_windows11_acceptance": False,
        "release_authorized": False,
        "premium_distribution_authorized": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", help="Existing six Windows x64 candidates")
    parser.add_argument("r9_report", help="Same-runner R9 native smoke evidence")
    parser.add_argument("private_root", help="Absolute private runner temp, OUTSIDE checkout")
    args = parser.parse_args(argv)
    try:
        result = verify_native_roundtrip(args.dist, args.r9_report, args.private_root)
    except (OSError, ValueError, RuntimeError):
        # No private paths, executable bytes, key data, or contents in CI logs.
        print("R118 HOLD: native sealed handoff integration failed; no release permission",
              file=sys.stderr)
        return 1
    if result["release_authorized"] is not False:
        return 1
    print("R118 PASS: six private candidate roundtrips, eight byte-preserving entries, "
          "modified ciphertext rejected; ephemeral key and bundle removed. "
          "NO release, transfer, or Windows 11 clearance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
