"""Deterministic, fail-closed SHA256SUMS builder for six private Windows candidates.

Runs after packaging and before the independent release gate. Does not inspect
PE safety, execute binaries, authenticate a build or authorize distribution.
It never deletes a candidate executable or overwrites existing evidence.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
import stat
import sys
import tempfile
from pathlib import Path


# Python -I deliberately omits the script directory from sys.path. Resolve
# only this Git-owned desktop module directory, not cwd or PYTHONPATH, so the
# private runner's isolated child commands can import local verification code.
DESKTOP = Path(__file__).resolve().parent
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

from candidate_guard import (
    CandidateGuardError, MAX_CHECKSUM_BYTES, MAX_EXE_BYTES,
    check_candidate_directory, read_checksum_candidate, sha256_candidate,
)

EXPECTED = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)
MANIFEST = "SHA256SUMS.txt"


class InventoryBuildError(ValueError):
    """Unsafe or incomplete candidate: stop; do not distribute any executable."""


def _membership(root: Path, expected: set[str]) -> None:
    """Reject stale manifests, links, directories and any surplus private file."""
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise InventoryBuildError("Candidate root must be a real directory")
    members = list(root.iterdir())
    if len(members) != len(expected) or {p.name for p in members} != expected:
        raise InventoryBuildError("Candidate folder has missing or unexpected files")
    for path in members:
        item = path.lstat()
        if (not stat.S_ISREG(item.st_mode) or item.st_nlink != 1
                or item.st_size < 1 or item.st_size > MAX_EXE_BYTES):
            raise InventoryBuildError("Candidate binaries must be distinct bounded ordinary files")


def _fingerprints(root: Path) -> tuple[str, ...]:
    return tuple(sha256_candidate(root / name, maximum=MAX_EXE_BYTES)
                 for name in EXPECTED)


@contextmanager
def _private_inventory_writer(stream):
    """Always close an owned staging stream, even if context entry fails.

    Do not let a filesystem or test-wrapper exception reveal private build
    paths in the CLI. System interruptions still propagate after cleanup.
    """
    try:
        with stream:
            yield stream
    except InventoryBuildError:
        raise
    except Exception:
        raise InventoryBuildError("Cannot safely stage checksum inventory") from None
    finally:
        try:
            stream.close()
        except Exception:
            # Cleanup exceptions must not leak customer paths or mask interrupts.
            pass


def _write_inventory(fd: int, inventory: bytes) -> None:
    """Take ownership of mkstemp's raw descriptor and verify complete writes."""
    try:
        stream = os.fdopen(fd, "wb")
    except BaseException as exc:
        try:
            os.close(fd)
        except OSError:
            pass
        if isinstance(exc, Exception):
            raise InventoryBuildError("Cannot safely stage checksum inventory") from None
        raise
    with _private_inventory_writer(stream) as writer:
        count = writer.write(inventory)
        # bool is a subclass of int; it is not a trustworthy byte count.
        if type(count) is not int or count != len(inventory):
            raise InventoryBuildError("Incomplete checksum inventory staging")
        writer.flush()
        os.fsync(writer.fileno())


def build_inventory(candidate_dir: str | Path) -> str:
    """Publish one canonical inventory only if all six source images stay stable.

    The completed seven-file bundle STILL requires release_gate.verify() and real
    Windows smoke tests. A failed post-publication check preserves the linked
    inventory for human review; pathname rollback has a check/delete race.
    """
    stage: Path | None = None
    published_identity: tuple[int, int] | None = None
    root = Path(candidate_dir)
    target = root / MANIFEST
    try:
        _membership(root, set(EXPECTED))
        original = _fingerprints(root)
        inventory = "".join(f"{digest}  {name}\n"
                            for name, digest in zip(EXPECTED, original)).encode("ascii")
        if len(inventory) > MAX_CHECKSUM_BYTES:
            raise InventoryBuildError("Checksum manifest exceeds safe bound")

        # Stage privately on the same volume. Hardlink publication is exclusive
        # and atomic: no empty/half-written manifest becomes available to others.
        fd, path = tempfile.mkstemp(prefix=".fvs-inventory-", dir=root)
        stage = Path(path)
        _write_inventory(fd, inventory)
        # Stage is expected here; independently reject any other new file.
        _membership_with_stage(root, stage)
        # Never briefly expose an incomplete or same-size corrupted inventory
        # through the exclusive hardlink publication step. The older final
        # post-publication comparison remains as a separate race/drift defense.
        if read_checksum_candidate(stage) != inventory:
            raise InventoryBuildError("Staged checksum inventory differs from canonical evidence")
        if _fingerprints(root) != original:
            raise InventoryBuildError("Candidate binaries changed during inventory build")
        # Pin the staging inode identity BEFORE publication. A successful
        # os.link must expose this exact inode; never assume that an observed
        # pathname still refers to the inode after the check.
        staged_info = stage.lstat()
        if not stat.S_ISREG(staged_info.st_mode) or staged_info.st_nlink != 1:
            raise InventoryBuildError("Inventory staging identity changed")
        published_identity = (staged_info.st_dev, staged_info.st_ino)
        os.link(stage, target)
        published_info = target.lstat()
        if (not stat.S_ISREG(published_info.st_mode)
                or (published_info.st_dev, published_info.st_ino) != published_identity):
            raise InventoryBuildError("Published inventory identity changed")
        stage.unlink()
        stage = None
        check_candidate_directory(root, EXPECTED)
        if read_checksum_candidate(target) != inventory or _fingerprints(root) != original:
            raise InventoryBuildError("Candidate changed after manifest publication")
        return target.name
    except InventoryBuildError:
        raise
    except (OSError, CandidateGuardError, UnicodeError):
        raise InventoryBuildError("Candidate inventory could not be generated safely") from None
    finally:
        if stage is not None:
            try:
                stage.unlink(missing_ok=True)
            except OSError:
                pass
        # Never auto-unlink a published SHA256SUMS path after a failed build.
        # Even an inode check followed by unlink has a race: another local
        # writer can replace the path between those operations. Keep evidence
        # for explicit operator review, and require a NEW clean folder/retry.

def _membership_with_stage(root: Path, stage: Path) -> None:
    _membership_staged = list(root.iterdir())
    if (len(_membership_staged) != len(EXPECTED) + 1
            or {p.name for p in _membership_staged} != set(EXPECTED) | {stage.name}):
        raise InventoryBuildError("Candidate folder changed during inventory build")
    info = stage.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise InventoryBuildError("Inventory staging file is not ordinary")
    for name in EXPECTED:
        item = (root / name).lstat()
        if (not stat.S_ISREG(item.st_mode) or item.st_nlink != 1
                or item.st_size < 1 or item.st_size > MAX_EXE_BYTES):
            raise InventoryBuildError("Candidate changed during inventory build")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", help="Directory containing ONLY the six approved EXEs")
    args = parser.parse_args(argv)
    try:
        name = build_inventory(args.dist)
    except InventoryBuildError as exc:
        print("REJECTED: " + str(exc), file=sys.stderr)
        return 1
    print(f"Wrote {name} for six candidates. NOT release authorized; run independent gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
