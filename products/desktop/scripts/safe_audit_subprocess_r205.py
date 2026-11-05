"""Run the strict R200 audited matrix with OS-level log isolation.

R201's sys.stdout/sys.stderr redirection protects Python writes but not raw
file-descriptor writes, sys.__stderr__, or grandchildren. A separate child
with all three standard handles bound to DEVNULL closes this CI log channel.
Child environment is restricted to platform launch and temporary-file keys.
Source tests remain an internal gate, never executable/release approval.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "products" / "desktop" / "scripts" / "safe_recent_regressions_r200.py"

# Permit only launch/path and temporary-file infrastructure. Never pass CI
# credentials, cloud tokens, proxy credentials, Python overrides or user profile
# data to a test process. Uppercase comparison handles Windows casing.
_CHILD_ENV_ALLOW = frozenset({
    "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
})


def _child_environment() -> dict[str, str]:
    """Construct a minimal inherited environment; this is NOT a sandbox."""
    return {name: value for name, value in os.environ.items()
            if name.upper() in _CHILD_ENV_ALLOW}


def run_private(runner: Path = AUDIT, *, timeout: int = 300) -> bool:
    """Return PASS only for a complete zero-exit child; print no child data.

    The runner itself enforces the R194-R199 148-case strict matrix and
    counts. This wrapper suppresses all descendant output, even os.write(1/2).
    It intentionally does not purport to sandbox arbitrary malicious code;
    file/network access by test code is not restricted.
    """
    try:
        if type(timeout) is not int or not 1 <= timeout <= 600:
            raise ValueError("invalid timeout")
        if not isinstance(runner, Path) or runner.is_symlink():
            raise ValueError("invalid runner")
        mode = runner.stat().st_mode
        if not stat.S_ISREG(mode):
            raise ValueError("missing or nonregular runner")
        flags = ["-I", "-B"]
        if sys.flags.optimize >= 2:
            flags.append("-OO")
        completed = subprocess.run(
            [sys.executable, *flags, str(runner)],
            cwd=str(ROOT),
            env=_child_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=timeout,
        )
        if type(completed.returncode) is not int or completed.returncode != 0:
            raise RuntimeError("child matrix did not pass")
    except BaseException:
        # No exception messages, paths, stderr, tracebacks, or fixture values.
        print("HOLD: R205 private audit matrix did not complete", file=sys.stderr)
        return False
    print("R205: strict audited matrix PASS (private child output suppressed; NOT release approval)")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if run_private() else 1)
