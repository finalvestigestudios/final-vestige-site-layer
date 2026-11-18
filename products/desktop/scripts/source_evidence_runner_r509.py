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

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "products/desktop/ci/source_evidence_commands_r509.txt"
MANIFEST_GIT_SHA1 = "a55a9b5bcbee5b9f075a39fc581ed5a4716eaca3"
ORIGINAL_GIT_SHA1 = "cbebff514baf4244754125c6d73e429b74f6b4e1"
ORIGINAL_COUNT = 414
TOTAL_COUNT = 416
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


def git_blob_sha(raw: bytes) -> str:
    if type(raw) is not bytes:
        raise EvidenceRejected("Invalid manifest bytes")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def load_commands(raw: bytes, root: Path = ROOT, *,
                  expected_sha: str = MANIFEST_GIT_SHA1,
                  expected_count: int = TOTAL_COUNT) -> tuple[tuple[str, ...], ...]:
    if (type(raw) is not bytes or not raw or len(raw) > 65536 or
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
            source = root / "products" / "desktop" / "tests" / match.group(1)
            if not source.is_file() or source.is_symlink():
                raise EvidenceRejected("Required source test unavailable")
        elif line not in SCRIPT_COMMANDS:
            raise EvidenceRejected("Unreviewed source command")
        approved.append(tuple(line.split(" ")[1:]))
    return tuple(approved)


def _child_environment(root: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not (k.upper() in {"GITHUB_TOKEN", "GH_TOKEN", "PYTHONHOME",
                                 "PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONUSERBASE"}
                   or k.upper().endswith("_TOKEN") or k.upper().endswith("_SECRET")
                   or k.upper().endswith("_PASSWORD"))}
    env["PYTHONPATH"] = str(root / "products" / "desktop")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def execute(commands: tuple[tuple[str, ...], ...], root: Path = ROOT,
            *, spawn=None) -> int:
    if (type(commands) is not tuple or not commands or
            any(type(x) is not tuple or not x or
                any(type(y) is not str for y in x) for x in commands)):
        print("REJECTED: empty or invalid source evidence matrix", file=sys.stderr)
        return 1
    run = subprocess.run if spawn is None else spawn
    env = _child_environment(root)
    for index, args in enumerate(commands, 1):
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
    print(f"PASS: {len(commands)} source commands; NOT Windows EXE, QD, or release approval")
    return 0


def main() -> int:
    try:
        return execute(load_commands(MANIFEST.read_bytes()))
    except (OSError, EvidenceRejected):
        print("REJECTED: immutable source evidence unavailable", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
