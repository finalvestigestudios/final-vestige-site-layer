"""Minimal child environment for the private six-EXE candidate builder.

This limits credential and Python override *inheritance*, not filesystem or
network access. Candidate children are still trusted code and must be run on a
trusted offline Windows workstation with a private, access-controlled workspace.
"""
from __future__ import annotations

import os

# Case-insensitive allowlist accommodates Windows' environment-key semantics.
# PATH is required for native build subprocesses; TEMP/TMP and SystemRoot are
# required by Windows and PyInstaller. No profile, proxy, token, pip, or Python
# injection variables should reach the child via the parent environment.
_OS_LAUNCH_KEYS = frozenset({
    "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
})


def private_child_environment() -> dict[str, str]:
    """Construct a fresh, minimal process environment; never mutate the parent.

    GITHUB_SHA is optional source metadata, not an authorization token. Retain
    only canonical lowercase Git SHA-1/SHA-256 values; no other GitHub Actions
    variables or injected Python/PyInstaller configuration is inherited.
    """
    result = {name: value for name, value in os.environ.items()
              if name.upper() in _OS_LAUNCH_KEYS}
    commit = os.environ.get("GITHUB_SHA", "")
    if (type(commit) is str and len(commit) in (40, 64)
            and all(char in "0123456789abcdef" for char in commit)):
        result["GITHUB_SHA"] = commit
    result["PYTHONNOUSERSITE"] = "1"
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    result["PIP_NO_INDEX"] = "1"
    return result
