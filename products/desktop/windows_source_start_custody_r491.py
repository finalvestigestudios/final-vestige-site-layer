"""Start Windows source checks behind a one-byte, parent-controlled job gate.

Only Python's isolated/-S bootstrap runs before the parent assigns its Job
Object. This is a startup race mitigation, not an operating-system sandbox.
"""
from __future__ import annotations

from pathlib import Path
import re

# The interpreter starts in isolated mode with site imports disabled. Nothing
# from the workspace, site packages, or the actual unittest module is loaded
# until the parent has assigned Job custody and writes the release byte.
_BOOTSTRAP = (
    "import sys\n"
    "if sys.stdin.buffer.read(1) != b'G': raise SystemExit(93)\n"
    "sys.stdin.close()\n"
    "import site\n"
    "site.main()\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "sys.argv = ['unittest', *sys.argv[2:]]\n"
    "import runpy\n"
    "runpy.run_module('unittest', run_name='__main__', alter_sys=True)\n"
)
_PATTERN = re.compile(r"test_[a-z0-9_]+\.py\Z")


def guarded_windows_command(cmd: tuple[str, ...], desktop: Path) -> tuple[str, ...]:
    """Allow only the runner's fixed unittest discovery invocation.

    Reject any unexpected command rather than letting a malicious caller
    change pre-custody Python interpreter flags or execute arbitrary code.
    """
    if (type(cmd) is not tuple or len(cmd) not in (11, 12)
            or any(type(arg) is not str for arg in cmd)
            or not isinstance(desktop, Path)):
        raise ValueError("Unsafe Windows source check command")
    opt = ("-OO",) if len(cmd) == 12 and cmd[1] == "-OO" else ()
    args = cmd[1 + len(opt):]
    if (len(args) != 10 or args[:8] != ("-B", "-W", "error", "-m",
             "unittest", "discover", "-s", str(desktop / "tests"))
            or args[8] != "-p" or _PATTERN.fullmatch(args[9]) is None):
        raise ValueError("Unsafe Windows source check command")
    return (cmd[0], *opt, "-I", "-S", "-B", "-W", "error", "-c",
            _BOOTSTRAP, str(desktop), "discover", "-s", args[7], "-p", args[9])
