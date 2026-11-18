"""R521: post-matrix source and manifest checks for read-only desktop evidence.

This detects source changes made by a successful final test subprocess too.
It does not attest all imported modules or resist a file changed and restored
between observations. Call only with internally reviewed custody callbacks.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable


def postflight_unchanged(
    root: Path,
    snapshots: dict[tuple[str, ...], bytes],
    source_matches: Callable[[Path, tuple[str, ...], bytes], bool],
    manifest_path: Path,
    initial_manifest: bytes | None,
    read_manifest: Callable[[Path], bytes],
) -> bool:
    """Fail closed unless every pinned source and original manifest still match.

    Caller captures snapshots before spawning any checks and revalidates each
    source immediately before use. This final pass catches changes by the last
    subprocess and to already-used sources. The source callback owns path and
    descriptor receipt checking; the manifest callback owns bounded reading.
    No customer filenames, input bytes or OS exceptions enter diagnostics.
    """
    if (type(snapshots) is not dict or not snapshots
            or (initial_manifest is not None and
                (type(initial_manifest) is not bytes or not initial_manifest))):
        return False
    try:
        for parts, digest in snapshots.items():
            if (type(parts) is not tuple or not parts
                    or any(type(part) is not str or not part for part in parts)
                    or type(digest) is not bytes or len(digest) != 32
                    or source_matches(root, parts, digest) is not True):
                return False
        # Compare actual content, not just length or a separately supplied
        # checksum. The owned reader independently rejects links/swaps/errors.
        if initial_manifest is None:
            return True  # Direct test hook; main() always pins the manifest.
        return read_manifest(manifest_path) == initial_manifest
    except Exception:
        # No private exception messages or chains cross this boolean boundary.
        return False
