"""Complete, non-overwriting publication of local UTF-8 text evidence.

Stage and fsync report bytes in the destination directory before creating its
final name. This protects individual policy diffs and grant hash manifests from
ordinary I/O failures; it is not a multi-file transaction or power-loss proof.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def publish_text(destination: str | Path, contents: str) -> Path:
    """Create a completed UTF-8 text report without replacing prior evidence.

    The caller must construct fully validated content before calling. On POSIX
    publishing uses an exclusive hard link; on Windows os.rename refuses an
    existing destination. Filesystems without these semantics fail closed.
    """
    if not isinstance(contents, str):
        raise TypeError("Text report content must be a string")
    target = Path(destination)
    if not target.parent.is_dir():
        raise ValueError("Choose an existing output folder")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.stem}-", suffix=".partial", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == "nt":
            # Windows os.rename rejects a destination that already exists.
            os.rename(temporary, target)
        else:
            # POSIX os.rename can replace; link creation fails on collisions.
            os.link(temporary, target)
            os.unlink(temporary)
        return target
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
