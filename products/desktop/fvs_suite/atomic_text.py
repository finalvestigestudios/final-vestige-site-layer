"""Complete, bounded, non-overwriting publication of local UTF-8 evidence.

Stage and fsync report bytes in the destination directory before creating its
final name. This protects individual policy diffs and grant hash manifests from
ordinary I/O failures; it is not a multi-file transaction or power-loss proof.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

# Limit direct API text/manifest writes independently of upstream input caps.
# A policy diff may expand its source: the final UTF-8 bytes, not Python code
# points, determine disk exposure. Match the CSV report's 64 MiB ceiling.
MAX_TEXT_REPORT_BYTES = 64 * 1024 * 1024


def _report_bytes(contents: str) -> bytes:
    """Validate actual, plain UTF-8 evidence before creating a staging file.

    The length fast-path avoids encoding a huge ASCII text buffer. The second
    size check catches 2-4-byte UTF-8 expansion. Callers cannot smuggle
    alternate evidence through str subclass conversion or encoding hooks.
    """
    if type(contents) is not str:
        raise TypeError("Text report content must be a plain string")
    if len(contents) > MAX_TEXT_REPORT_BYTES:
        raise ValueError("Text report byte limit exceeded")
    if "\x00" in contents or any(0xD800 <= ord(ch) <= 0xDFFF for ch in contents):
        raise ValueError("Invalid text report content")
    encoded = contents.encode("utf-8")
    if len(encoded) > MAX_TEXT_REPORT_BYTES:
        raise ValueError("Text report byte limit exceeded")
    return encoded


def publish_text(destination: str | Path, contents: str) -> Path:
    """Publish a complete, <=64 MiB UTF-8 TXT/manifest with no overwrite.

    NUL, lone UTF-16 surrogates, or fabricated str subclasses fail *before*
    staging. Errors do not contain customer content. Exact bytes and line
    endings are preserved; no BOM is inserted. On POSIX an exclusive hard
    link publishes; on Windows os.rename refuses an existing destination.
    Filesystems without these semantics fail closed.
    """
    payload = _report_bytes(contents)
    target = Path(destination)
    if not target.parent.is_dir():
        raise ValueError("Choose an existing output folder")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.stem}-", suffix=".partial", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
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
