"""R514: least-privilege environment for read-only desktop source-test children.

This is host-environment minimization, not filesystem or process sandboxing.
No unknown variables, provider config, package-registry URLs, or runtime
injection knobs are inherited merely because their names lack a known suffix.
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

# OS plumbing required to start Python and create ephemeral local test files.
# HOME/APPDATA paths may remain readable; this policy does not isolate files.
# Audit any addition: an allowlisted value can itself contain private data.
_SAFE_HOST_NAMES = frozenset({
    "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC",
    "TEMP", "TMP", "TMPDIR", "HOME", "HOMEDRIVE", "HOMEPATH",
    "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA",
    "PROGRAMFILES", "PROGRAMFILES(X86)", "COMMONPROGRAMFILES",
    "COMMONPROGRAMFILES(X86)", "ALLUSERSPROFILE",
    "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "TZ",
    "CI", "GITHUB_ACTIONS", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_IDENTIFIER", "OS", "WINDIR", "SYSTEMDRIVE",
})


def child_environment(root: Path, host: Mapping[str, str]) -> dict[str, str]:
    """Inherit only reviewed OS/CI keys; reject case-folded duplicates.

    Never mutate the host mapping, and always overwrite Python startup controls
    with deterministic values. Windows environment names are case-insensitive,
    so duplicate case variants are dropped rather than picking a winner.
    """
    allowed: dict[str, str] = {}
    seen: dict[str, str] = {}
    ambiguous: set[str] = set()
    for name, value in host.items():
        if type(name) is not str or type(value) is not str:
            continue
        key = name.upper()
        if key not in _SAFE_HOST_NAMES or key in ambiguous:
            continue
        if key in seen:
            allowed.pop(seen[key], None)
            ambiguous.add(key)
            continue
        seen[key] = name
        allowed[name] = value
    allowed["PYTHONPATH"] = str(root / "products" / "desktop")
    allowed["PYTHONDONTWRITEBYTECODE"] = "1"
    allowed["PYTHONHASHSEED"] = "0"
    return allowed
