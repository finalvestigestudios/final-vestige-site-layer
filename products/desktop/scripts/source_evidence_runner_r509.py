"""R509: fail-closed, read-only source evidence executor (NOT a release gate).

The immutable manifest preserves all 414 ordered R508 source commands, including
the normal and -OO test matrix. No shell, untrusted code, artifacts, or private
failure output. Any changed/missing instruction requires a reviewed new digest.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys

from source_child_env_r514 import child_environment
from source_engine_custody_r522 import (
    EngineSourceRejected, engine_sources_unchanged, snapshot_engine_sources,
)
from source_manifest_guard_r520 import ManifestReadRejected, read_manifest_custodied
from source_postflight_r521 import postflight_unchanged
from source_path_snapshot_r515 import (
    SourceSnapshotRejected, matches_source_fingerprint, source_fingerprint,
)

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "products/desktop/ci/source_evidence_commands_r509.txt"
MANIFEST_GIT_SHA1 = "a55a9b5bcbee5b9f075a39fc581ed5a4716eaca3"
ORIGINAL_GIT_SHA1 = "cbebff514baf4244754125c6d73e429b74f6b4e1"
ORIGINAL_COUNT = 414
TOTAL_COUNT = 416
MAX_MANIFEST_BYTES = 65_536
TEST_COMMAND = re.compile(
    r"python (?:-OO )?(?:-B )?-W error -m unittest discover -s "
    r"products/desktop/tests -p (test_[a-z0-9_]+\.py)"
)
SCRIPT_COMMANDS = frozenset({
    "python -W error products/desktop/scripts/source_smoke_gate.py",
    "python -OO -W error products/desktop/scripts/source_smoke_gate.py",
    "python -I products/desktop/offline_source_smoke_r408.py",
    "python -B products/desktop/offline_regression_gate_r459.py",
})


class EvidenceRejected(ValueError):
    """Input or source evidence failed its reviewed custody contract."""


def _is_unlinked_repo_file(root: Path, parts: tuple[str, ...]) -> bool:
    """Reject linked source files, parents and Windows junctions before launch.

    This is preflight custody, not an atomic or race-proof file open.
    """
    if not parts or any(not p or p in (".", "..") or "/" in p or "\\" in p for p in parts):
        return False
    target = root
    try:
        for part in parts:
            target = target / part
            if target.is_symlink():
                return False
            junction = getattr(target, "is_junction", None)
            if junction is not None and junction():
                return False
        return target.is_file()
    except (OSError, ValueError):
        return False


def _is_unlinked_test_file(root: Path, name: str) -> bool:
    """Apply the same custody rule to every manifest-listed source test."""
    return _is_unlinked_repo_file(root, ("products", "desktop", "tests", name))


def git_blob_sha(raw: bytes) -> str:
    if type(raw) is not bytes:
        raise EvidenceRejected("Invalid manifest bytes")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def read_manifest_bounded(path: Path) -> bytes:
    """Descriptor-verified bounded manifest read with private failure redaction.

    R520 refuses linked, replaced, nonregular or mutated source manifests
    before the immutable Git blob digest and 416-command allowlist are checked.
    """
    try:
        return read_manifest_custodied(path, MAX_MANIFEST_BYTES)
    except ManifestReadRejected:
        # Raise outside the catch block to avoid retaining private OS/path
        # metadata in the public runner's chained exception state.
        pass
    raise EvidenceRejected("Unsafe source evidence manifest")


def load_commands(raw: bytes, root: Path = ROOT, *,
                  expected_sha: str = MANIFEST_GIT_SHA1,
                  expected_count: int = TOTAL_COUNT) -> tuple[tuple[str, ...], ...]:
    if (type(raw) is not bytes or not raw or len(raw) > MAX_MANIFEST_BYTES or
            b"\0" in raw or b"\r" in raw or b"\t" in raw or not raw.endswith(b"\n")):
        raise EvidenceRejected("Unsafe source evidence manifest")
    if git_blob_sha(raw) != expected_sha:
        raise EvidenceRejected("Source command inventory changed")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError:
        raise EvidenceRejected("Invalid command encoding") from None
    if len(lines) != expected_count:
        raise EvidenceRejected("Missing or extra source checks")
    approved: list[tuple[str, ...]] = []
    for line in lines:
        if not line or line != line.strip() or "  " in line:
            raise EvidenceRejected("Malformed source command")
        match = TEST_COMMAND.fullmatch(line)
        if match is not None:
            if not _is_unlinked_test_file(root, match.group(1)):
                raise EvidenceRejected("Required source test unavailable")
        elif line in SCRIPT_COMMANDS:
            script_path = line.split(" ")[-1]
            if not _is_unlinked_repo_file(root, tuple(script_path.split("/"))):
                raise EvidenceRejected("Required source script unavailable")
        else:
            raise EvidenceRejected("Unreviewed source command")
        approved.append(tuple(line.split(" ")[1:]))
    return tuple(approved)


def _source_parts_for_argv(args: tuple[str, ...]) -> tuple[str, ...]:
    """Map a pinned test command to the *actual* file it will launch.

    Recheck source paths after initial manifest validation: earlier matrix
    processes must not replace later Python source files unnoticed.
    """
    if type(args) is not tuple or any(type(x) is not str for x in args):
        raise EvidenceRejected("Invalid source evidence command")
    line = "python " + " ".join(args)
    match = TEST_COMMAND.fullmatch(line)
    if match is not None:
        return ("products", "desktop", "tests", match.group(1))
    if line in SCRIPT_COMMANDS:
        return tuple(line.split(" ")[-1].split("/"))
    raise EvidenceRejected("Unreviewed source evidence command")


def _child_environment(root: Path) -> dict[str, str]:
    """Run child checks with reviewed OS/CI variables only (R514).

    The historical blacklist admitted arbitrary new credential/config names.
    This module-level wrapper preserves the runner's established test API.
    """
    return child_environment(root, os.environ)


def _engine_receipt_current(root: Path, receipt: dict[tuple[str, ...], bytes]) -> bool:
    """Reject any engine inventory mismatch without disclosing private paths.

    A failed or exception-raising verifier must never authorize subprocesses.
    Only the exact boolean True is sufficient evidence.
    """
    try:
        return engine_sources_unchanged(root, receipt) is True
    except Exception:
        return False


def execute(commands: tuple[tuple[str, ...], ...], root: Path = ROOT,
            *, spawn=None, verify_source_snapshots: bool = False,
            manifest_snapshot: bytes | None = None,
            engine_source_snapshot: dict[tuple[str, ...], bytes] | None = None) -> int:
    if (type(commands) is not tuple or not commands or
            any(type(x) is not tuple or not x or
                any(type(y) is not str for y in x) for x in commands)):
        print("REJECTED: empty or invalid source evidence matrix", file=sys.stderr)
        return 1
    # The immutable manifest checked all paths only once. Capture each
    # unique source-file hash before starting ANY subprocess, then verify it
    # immediately before every (potentially much later) launch.
    # Direct isolated execute() fixtures retain their historical test hook;
    # the real main() *always* enables prelaunch source custody.
    planned_paths: list[tuple[str, ...]] = []
    snapshots: dict[tuple[str, ...], bytes] = {}
    if verify_source_snapshots:
        try:
            for args in commands:
                parts = _source_parts_for_argv(args)
                planned_paths.append(parts)
                if parts not in snapshots:
                    snapshots[parts] = source_fingerprint(root, parts)
        except (EvidenceRejected, SourceSnapshotRejected):
            print("REJECTED: source-file snapshot unavailable", file=sys.stderr)
            return 1
    if manifest_snapshot is not None and (
            not verify_source_snapshots or type(manifest_snapshot) is not bytes
            or not manifest_snapshot):
        print("REJECTED: invalid source manifest snapshot", file=sys.stderr)
        return 1
    if engine_source_snapshot is not None and (
            not verify_source_snapshots or manifest_snapshot is None
            or type(engine_source_snapshot) is not dict or not engine_source_snapshot):
        print("REJECTED: invalid engine source snapshot", file=sys.stderr)
        return 1
    run = subprocess.run if spawn is None else spawn
    env = _child_environment(root)
    for index, args in enumerate(commands, 1):
        if verify_source_snapshots:
            parts = planned_paths[index - 1]
            if not matches_source_fingerprint(root, parts, snapshots[parts]):
                print(f"REJECTED: source check {index}/{len(commands)} changed", file=sys.stderr)
                return 1
        # R523 rechecks the shared six-app engines before EVERY command, not
        # only at matrix end. A changed engine must not run in a later test and
        # then be restored to its initial bytes to manufacture a PASS.
        if (engine_source_snapshot is not None and
                not _engine_receipt_current(root, engine_source_snapshot)):
            print(f"REJECTED: shared engine source changed before check {index}/{len(commands)}",
                  file=sys.stderr)
            return 1
        try:
            result = run([sys.executable, *args], cwd=str(root), env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         timeout=600, check=False)
            if type(result.returncode) is not int or result.returncode != 0:
                print(f"REJECTED: source check {index}/{len(commands)} failed", file=sys.stderr)
                return 1
        except (OSError, ValueError, subprocess.TimeoutExpired):
            print(f"REJECTED: source check {index}/{len(commands)} blocked", file=sys.stderr)
            return 1
    # A final subprocess can alter its own file or an already-run source.
    # The prelaunch checks alone could still falsely print PASS. Revalidate
    # every pinned source after the last process exits, and in real main()
    # reread the descriptor-bound manifest against the original exact bytes.
    if verify_source_snapshots and not postflight_unchanged(
            root, snapshots, matches_source_fingerprint,
            MANIFEST, manifest_snapshot, read_manifest_bounded):
        print("REJECTED: source matrix changed after checks", file=sys.stderr)
        return 1
    # Preserve the R522 postflight; the last child could still edit engine
    # source after its own prelaunch verification. main() always supplies it.
    if (engine_source_snapshot is not None and
            not _engine_receipt_current(root, engine_source_snapshot)):
        print("REJECTED: shared engine source changed after checks", file=sys.stderr)
        return 1
    print(f"PASS: {len(commands)} source commands; NOT Windows EXE, QD, or release approval")
    return 0


def main() -> int:
    try:
        if not _is_unlinked_repo_file(
            ROOT, ("products", "desktop", "ci", "source_evidence_commands_r509.txt")
        ):
            raise EvidenceRejected("Unsafe source evidence manifest path")
        original_manifest = read_manifest_bounded(MANIFEST)
        # Capture BEFORE the matrix runs; no production/network/customer data.
        original_engines = snapshot_engine_sources(ROOT)
        return execute(load_commands(original_manifest),
                       verify_source_snapshots=True, manifest_snapshot=original_manifest,
                       engine_source_snapshot=original_engines)
    except (OSError, EvidenceRejected, EngineSourceRejected):
        print("REJECTED: immutable source evidence unavailable", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
