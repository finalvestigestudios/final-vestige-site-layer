"""R122: record ONE human-observed Windows 11 check privately; never approve release.

An operator supplies a local observation file and explicit PASS/FAIL. This
tool does not observe NVDA, keyboard, contrast, scaling, antivirus or malware.
The note and review matrix never leave the workstation. A valid output is
ONLY reviewer testimony, not independent QA or a premium entitlement.
"""
from __future__ import annotations

import argparse
from private_review_cli_r146 import PrivateReviewParser
import copy
import hmac
import json
import os
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import windows11_manual_acceptance_r109 as qa
import windows11_witness_inventory_r124 as inventory

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


def _ordinary_file_identity(path: Path) -> tuple[int, int]:
    """Reject linked, symlinked or reparse files before trusting file identity.

    This reduces accidental reviewer substitution; it is not hostile-FS proof.
    """
    meta = path.lstat()
    if (not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1
            or path.is_symlink()
            or (hasattr(path, "is_junction") and path.is_junction())
            or (os.name == "nt" and bool(
                getattr(meta, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))):
        raise qa.ReviewHold("Untrusted private review file")
    return (meta.st_dev, meta.st_ino)


def _observation_snapshot(metadata) -> tuple[int, int, int, int, int]:
    """Bind a human note to one ordinary local file throughout its read."""
    return (metadata.st_dev, metadata.st_ino, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _read_private_observation(path: Path, *, dist: Path, review: Path,
                              witnesses: Path, r9_report: Path) -> str:
    """Read only a stable, standalone local text note; never chase file links.

    An attacker controlling the reviewer's filesystem is outside this
    cooperative gate's trust model. This prevents accidental copying of R9
    custody, an existing witness, or a symlinked financial/client file into
    the reviewer evidence bundle. No text/path is emitted on failure.
    """
    parent = _safe_dir(path.parent)
    if (parent.is_relative_to(dist.resolve(strict=True)) or
            parent.is_relative_to(_safe_dir(witnesses))):
        raise qa.ReviewHold("Human observation must be outside candidate and witness custody")
    before = path.lstat()
    _ordinary_file_identity(path)
    if (path.resolve(strict=True) == review.resolve() or
            path.resolve(strict=True) == r9_report.resolve()):
        raise qa.ReviewHold("Human observation must not be a custody record")
    if not qa.MIN_OBSERVATION_CHARS <= before.st_size <= NOTE_LIMIT:
        raise qa.ReviewHold("Human observation has invalid size")

    # NONBLOCK avoids hanging on an adversarial FIFO substituted between
    # lstat() and open() on POSIX. NOFOLLOW is used where the OS supports it.
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
             getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as source:
        opened = os.fstat(source.fileno())
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise qa.ReviewHold("Human observation is not an ordinary file")
        data = source.read(NOTE_LIMIT + 1)
        completed = os.fstat(source.fileno())
    after = path.lstat()
    _ordinary_file_identity(path)
    # Python's path-stat and descriptor-stat APIs can report differing
    # timestamp representations on Windows. Compare each view against itself,
    # and bridge the two views using device, inode and exact byte length.
    # A byte-identical path replacement still changes the path file identity.
    path_identity = (before.st_dev, before.st_ino)
    fd_identity = (opened.st_dev, opened.st_ino)
    if (path_identity != fd_identity or
            (after.st_dev, after.st_ino) != path_identity or
            (completed.st_dev, completed.st_ino) != fd_identity or
            before.st_size != opened.st_size or
            _observation_snapshot(before) != _observation_snapshot(after) or
            _observation_snapshot(opened) != _observation_snapshot(completed)):
        raise qa.ReviewHold("Human observation changed during reading")
    if not qa.MIN_OBSERVATION_CHARS <= len(data) <= NOTE_LIMIT:
        raise qa.ReviewHold("Human observation has invalid length")
    try:
        return data.decode("utf-8")
    except UnicodeError:
        raise qa.ReviewHold("Human observation must be UTF-8") from None


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
    if review_dir == witness_dir:
        raise qa.ReviewHold("Witness folder must be dedicated and separate from review matrix")

    # One exclusive lock prevents cooperating review writers from racing.
    lock = review.with_name(review.name + ".r122.lock")
    fd = None
    tmp = None
    created = False
    created_identity = None
    target = witness_dir / (app.removesuffix(".exe") + "--" + check + ".json")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     getattr(os, "O_BINARY", 0), 0o600)
        lock_identity = os.fstat(fd)
        old_identity = _ordinary_file_identity(review)
        old = qa._bytes(review, qa.MAX_REPORT_BYTES)
        matrix = qa._strict_json(old)
        if matrix.get("windows11_build") != build:
            raise qa.ReviewHold("Reviewer build mismatch")
        qa.validate_review(matrix, template, witness_dir)
        # R124: an orphan or interrupted prior R122 write is a hard HOLD.
        inventory.verify_clean(matrix, witness_dir)
        slot = matrix["apps"][app]["checks"][check]
        if slot != {"state": "NOT_RUN", "witness_sha256": None}:
            raise qa.ReviewHold("Previously recorded checks cannot be overwritten")
        if target.exists() or target.is_symlink():
            raise qa.ReviewHold("Previous witness file exists")

        observation = _read_private_observation(
            observation_file, dist=dist, review=review, witnesses=witness_dir,
            r9_report=r9_report)
        note = {
            "schema": qa.WITNESS_SCHEMA_V2, "app": app, "check": check, "state": state,
            "candidate_sha256": matrix["apps"][app]["candidate_sha256"],
            "r9_report_sha256": matrix["r9_report_sha256"],
            "reviewer_id": matrix["reviewer_id"],
            "windows11_build": matrix["windows11_build"],
            "observed_utc": matrix["observed_utc"],
            # Timestamp when this private tool recorded human testimony,
            # NOT when any physical check was independently witnessed.
            "recorded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
        with os.fdopen(wf, "wb") as out:
            created = True
            created_metadata = os.fstat(out.fileno())
            created_identity = (created_metadata.st_dev, created_metadata.st_ino)
            out.write(note_bytes)
            out.flush()
            os.fsync(out.fileno())
        qa.validate_review(updated, template, witness_dir)
        # Recheck after the new witness is on disk, before committing matrix.
        # If another actor added a stray entry, rollback only our own note.
        inventory.verify_clean(updated, witness_dir)
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
        if (_ordinary_file_identity(review) != old_identity or
                not hmac.compare_digest(qa._sha(qa._bytes(review, qa.MAX_REPORT_BYTES)),
                                        qa._sha(old))):
            raise qa.ReviewHold("Review changed concurrently")
        os.replace(tmp, review)
        tmp = None
        return {"state": state, "witness_sha256": qa._sha(note_bytes),
                "release_authorized": False}
    except Exception:
        # A witness without a matrix reference must never count as acceptance.
        # Remove only if it is still precisely our own freshly written bytes.
        if created and created_identity is not None:
            try:
                # Never delete a substituted witness, even when its bytes
                # match our freshly written note. Preserve unknown evidence.
                if (_ordinary_file_identity(target) == created_identity and
                        hmac.compare_digest(
                            qa._sha(qa._bytes(target, qa.MAX_WITNESS_BYTES)),
                            qa._sha(note_bytes)) and
                        _ordinary_file_identity(target) == created_identity):
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
                current = lock.lstat()
                if (stat.S_ISREG(current.st_mode) and current.st_size == 0 and
                        (current.st_dev, current.st_ino) ==
                        (lock_identity.st_dev, lock_identity.st_ino)):
                    lock.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = PrivateReviewParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--r9-report", type=Path, required=True)
    parser.add_argument("--expected-r9-sha256", required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--witnesses", type=Path, required=True)
    parser.add_argument("--app", required=True, choices=qa.ALL)
    parser.add_argument("--check", required=True)
    parser.add_argument("--state", required=True, choices=("PASS", "FAIL"))
    parser.add_argument("--observation-file", type=Path, required=True)
    try:
        # Redact parser failures before they reach stderr or custody storage.
        args = parser.parse_args(argv)
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
