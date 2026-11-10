"""Private, fail-closed subprocess boundary for six Windows desktop smoke checks.

This helper NEVER implies a passing release, malware clearance, entitlement,
code-signing or QD decision; it only validates a smoke process exit status.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable


class SmokeRunError(ValueError):
    """A smoke attempt failed without exposing private paths or child output."""


def select_smoke_runner(runner: Callable | None) -> Callable:
    """Preserve an injected runner even when its truth value is false.

    Never silently launch a real EXE because a test double implements
    __bool__ or __len__ as false. Keep provenance detection consistent with
    the caller's ``runner is not None`` check.
    """
    return subprocess.run if runner is None else runner


def run_smoke_checked(launch: Callable, exe: Path, root: Path, *,
                      name: str, timeout: int) -> None:
    """Launch one already-verified candidate without inheriting I/O streams.

    Caller MUST perform full PE, manifest, SHA and pre/post execution checks.
    Only a genuine int zero exit status succeeds; mocks with truthy or
    coercible values cannot create misleading evidence. All ordinary launch
    faults are redacted, including unexpected subprocess and result errors.
    Deliberate KeyboardInterrupt/SystemExit signals are not swallowed.
    """
    if type(timeout) is not int or not 1 <= timeout <= 600:
        raise SmokeRunError("Smoke timeout must be between 1 and 600 seconds")
    try:
        result = launch([str(exe.resolve()), "--smoke-test"],
                        cwd=str(root.resolve()), timeout=timeout,
                        check=False, stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise SmokeRunError(f"{name}: smoke timed out") from None
    except Exception:
        raise SmokeRunError(f"{name}: could not execute packaged EXE") from None
    try:
        code = result.returncode
    except Exception:
        raise SmokeRunError(f"{name}: invalid smoke result") from None
    if type(code) is not int:
        raise SmokeRunError(f"{name}: invalid smoke result")
    if code != 0:
        raise SmokeRunError(f"{name}: smoke failed with exit code {code}")
