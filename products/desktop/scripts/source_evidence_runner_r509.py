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


_PRIVATE_ENV_NAMES = frozenset({
    "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_ENV", "GITHUB_PATH", "GITHUB_OUTPUT",
    "GIT_ASKPASS", "SSH_ASKPASS", "AWS_ACCESS_KEY_ID",
    "PYTHONHOME", "PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONUSERBASE",
    "PYTHONOPTIMIZE", "PYTHONWARNINGS", "PYTHONBREAKPOINT", "PYTHONPYCACHEPREFIX",
    "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH",
})
_PRIVATE_ENV_SUFFIXES = (
    "_TOKEN", "_SECRET", "_PASSWORD", "_KEY", "_CREDENTIAL", "_CREDENTIALS",
    "_COOKIE", "_SESSION",
)


# Preserve only the public GitHub Actions boolean across the GITHUB_* boundary.
# Job command files and event payloads are not needed by desktop source tests.
_CI_ENV_MARKER = "GITHUB_ACTIONS"
# Cloud, package-registry and container configuration may carry credentials
# in *_FILE, *_URL or *_PROFILE, not just token/password-suffixed variables.
# Do not pass ambient host credentials into financial source regression tests.
# This is environment minimization, NOT filesystem or OS process isolation.
_UNTRUSTED_ENV_PREFIXES = (
    "PYTHON", "GITHUB_", "GIT_", "SSH_",
    "AWS_", "AZURE_", "GOOGLE_", "GCLOUD_", "CLOUDSDK_",
    "GH_", "DOCKER_", "KUBE_", "NPM_", "PIP_", "PYPI_",
    "TWINE_", "POETRY_", "UV_", "GPG_", "TF_", "TERRAFORM_",
)
_UNTRUSTED_ENV_NAMES = frozenset({"KUBECONFIG", "GNUPGHOME"})


def _child_environment(root: Path) -> dict[str, str]:
    env = {}
    for name, value in os.environ.items():
        key = name.upper()
        if (key in _PRIVATE_ENV_NAMES or key in _UNTRUSTED_ENV_NAMES
                or key.endswith(_PRIVATE_ENV_SUFFIXES)
                or (key.startswith(_UNTRUSTED_ENV_PREFIXES)
                    and key != _CI_ENV_MARKER)):
            continue
        env[name] = value
    env["PYTHONPATH"] = str(root / "products" / "desktop")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
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
        if not _is_unlinked_repo_file(
            ROOT, ("products", "desktop", "ci", "source_evidence_commands_r509.txt")
        ):
            raise EvidenceRejected("Unsafe source evidence manifest path")
        return execute(load_commands(MANIFEST.read_bytes()))
    except (OSError, EvidenceRejected):
        print("REJECTED: immutable source evidence unavailable", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
