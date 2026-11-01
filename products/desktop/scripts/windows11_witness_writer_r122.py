"""R122: record ONE human-observed Windows 11 check privately; never approve release.

An operator supplies a local observation file and explicit PASS/FAIL. This
tool does not observe NVDA, keyboard, contrast, scaling, antivirus or malware.
The note and review matrix never leave the workstation. A valid output is
ONLY reviewer testimony, not independent QA or a premium entitlement.
"""
from __future__ import annotations

import argparse
import copy
import hmac
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

import windows11_manual_acceptance_r109 as qa

NOTE_LIMIT = 4096 * 4
HOLD = qa.ERROR


def _safe_dir(directory: Path) -> Path:
    """Reject symlink/reparse ancestors, including Windows junctions."""
    real = directory.resolve(strict=True)
    cur = directory.absolute()
    while True:
        meta = cur.lstat()
        if (not stat.S_ISDIR(meta.st_mode) or cur.is_symlink()
                or (hasattr(cur, "is_junction") and cur.is_junction())
                or (os.name == "nt" and
                    bool(getattr(meta, "st_file_attributes", 0) &
                         getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))):
            raise qa.ReviewHold("Untrusted review directory")
        if cur == cur.parent:
            break
        cur = cur.parent
    if not real.is_dir():
        raise qa.ReviewHold("Review directory is missing")
    return real


def _excluded_from_candidates(path: Path, dist: Path) -> None:
    if path.resolve().is_relative_to(dist.resolve(strict=True)):
        raise qa.ReviewHold("Review data cannot be stored inside candidate directory")


def record_one(*, dist: Path, r9_report: Path, expected_pin: str, review: Path,
               witnesses: Path, app: str, check: str, state: str,
               observation_file: Path) -> dict:
    """Fail closed on source, OS, review and prior witnesses before any write.

    The .r122.lock is cooperative; a crash may leave it behind. Never remove
    an unexplained stale lock automatically. A failed matrix update may leave
    an unreferenced witness but cannot turn a check into PASS.
    """
    pin = qa.external_r9_pin(expected_pin)
    build = qa.native_win11_build()
    if app not in qa.ALL or check not in qa._checks(app) or state not in ("PASS", "FAIL"):
        raise qa.ReviewHold("Unrecognized manual check or conclusion")
    report, actual, raw_r9 = qa.load_custody(dist, r9_report, pin)
    template = qa.make_template(report, actual, raw_r9)

    review_dir = _safe_dir(review.parent)
    witness_dir = _safe_dir(witnesses)
    _excluded_from_candidates(review, dist)
    _excluded_from_candidates(witness_dir, dist)
    _excluded_from_candidates(observation_file, dist)
    if review.parent.resolve() == dist.resolve() or review == observation_file:
        raise qa.ReviewHold("Review path must be separate")

    # One exclusive lock prevents cooperating review writers from racing.
    lock = review.with_name(review.name + ".r122.lock")
    fd = None
    tmp = None
    created = False
    target = witness_dir / (app.removesuffix(".exe") + "--" + check + ".json")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     getattr(os, "O_BINARY", 0), 0o600)
        old = qa._bytes(review, qa.MAX_REPORT_BYTES)
        matrix = qa._strict_json(old)
        if matrix.get("windows11_build") != build:
            raise qa.ReviewHold("Reviewer build mismatch")
        qa.validate_review(matrix, template, witness_dir)
        slot = matrix["apps"][app]["checks"][check]
        if slot != {"state": "NOT_RUN", "witness_sha256": None}:
            raise qa.ReviewHold("Previously recorded checks cannot be overwritten")
        if target.exists() or target.is_symlink():
            raise qa.ReviewHold("Previous witness file exists")

        observation = qa._bytes(observation_file, NOTE_LIMIT, minimum=qa.MIN_OBSERVATION_CHARS).decode("utf-8")
        note = {
            "schema": qa.WITNESS_SCHEMA, "app": app, "check": check, "state": state,
            "candidate_sha256": matrix["apps"][app]["candidate_sha256"],
            "r9_report_sha256": matrix["r9_report_sha256"],
            "reviewer_id": matrix["reviewer_id"],
            "windows11_build": matrix["windows11_build"],
            "observed_utc": matrix["observed_utc"],
            "observation": observation,
        }
        note_bytes = (json.dumps(note, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":")) + "\n").encode("utf-8")
        qa._bound_witness(note_bytes, matrix, app, check, state)

        updated = copy.deepcopy(matrix)
        updated["apps"][app]["checks"][check] = {
            "state": state, "witness_sha256": qa._sha(note_bytes)}
        # Verify new evidence against the source-bound envelope after writing.
        wf = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0), 0o600)
        created = True
        with os.fdopen(wf, "wb") as out:
            out.write(note_bytes)
            out.flush()
            os.fsync(out.fileno())
        qa.validate_review(updated, template, witness_dir)
        new_raw = (json.dumps(updated, ensure_ascii=False, sort_keys=True,
                              indent=2) + "\n").encode("utf-8")
        if len(new_raw) > qa.MAX_REPORT_BYTES:
            raise qa.ReviewHold("Review matrix exceeds safe size")

        tf, tmp_name = tempfile.mkstemp(prefix=".fv-r122-", suffix=".tmp", dir=review_dir)
        tmp = Path(tmp_name)
        with os.fdopen(tf, "wb") as out:
            out.write(new_raw)
            out.flush()
            os.fsync(out.fileno())
        # Stop if an independent actor changed the original review during writing.
        if not hmac.compare_digest(qa._sha(qa._bytes(review, qa.MAX_REPORT_BYTES)),
                                   qa._sha(old)):
            raise qa.ReviewHold("Review changed concurrently")
        os.replace(tmp, review)
        tmp = None
        return {"state": state, "witness_sha256": qa._sha(note_bytes),
                "release_authorized": False}
    except Exception:
        # A witness without a matrix reference must never count as acceptance.
        # Remove only if it is still precisely our own freshly written bytes.
        if created:
            try:
                if qa._sha(qa._bytes(target, qa.MAX_WITNESS_BYTES)) == qa._sha(note_bytes):
                    target.unlink()
            except (OSError, qa.ReviewHold):
                pass
        raise
    finally:
        if tmp is not None:
            try:
                tmp.unlink()
            except OSError:
                pass
        if fd is not None:
            os.close(fd)
            # An unexplained modified/replaced lock is not silently removed.
            try:
                if lock.is_file() and lock.stat().st_size == 0:
                    lock.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--r9-report", type=Path, required=True)
    parser.add_argument("--expected-r9-sha256", required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--witnesses", type=Path, required=True)
    parser.add_argument("--app", required=True, choices=qa.ALL)
    parser.add_argument("--check", required=True)
    parser.add_argument("--state", required=True, choices=("PASS", "FAIL"))
    parser.add_argument("--observation-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = record_one(
            dist=args.dist, r9_report=args.r9_report,
            expected_pin=args.expected_r9_sha256, review=args.review,
            witnesses=args.witnesses, app=args.app, check=args.check,
            state=args.state, observation_file=args.observation_file)
        if result["release_authorized"] is not False:
            raise qa.ReviewHold("No release authority")
        print("ONE PRIVATE MANUAL WITNESS RECORDED; release remains HOLD")
        return 0
    except (qa.ReviewHold, OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(HOLD, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
