"""R522: fail-closed postflight custody for shared six-app financial engine source.

This supplements the pinned test/script and manifest checks. It protects the
flat fvs_suite Python package from addition, removal, or modification during
source evidence execution. R523 also blocks unreviewed import surfaces.
This is not an atomic filesystem attestation.
"""
from __future__ import annotations

from pathlib import Path
import re

from source_path_snapshot_r515 import (
    SourceSnapshotRejected, matches_source_fingerprint, source_fingerprint,
)

PACKAGE_PARTS = ("products", "desktop", "fvs_suite")
MAX_MODULES = 256
_MODULE_NAME = re.compile(r"(?:__init__|[a-z][a-z0-9_]*)\.py\Z", re.ASCII)
_IMPORTABLE_SUFFIXES = frozenset({".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".pyw"})


class EngineSourceRejected(ValueError):
    """The shared financial-engine source inventory cannot be trusted."""


def _engine_paths(root: Path) -> tuple[tuple[str, ...], ...]:
    if not isinstance(root, Path) or not root.is_absolute() or ".." in root.parts:
        raise EngineSourceRejected("Unsafe engine source inventory")
    package = root.joinpath(*PACKAGE_PARTS)
    if not package.is_dir() or package.is_symlink():
        raise EngineSourceRejected("Unsafe engine source inventory")
    junction = getattr(package, "is_junction", None)
    if junction is not None and junction():
        raise EngineSourceRejected("Unsafe engine source inventory")
    names = []
    for entry in package.iterdir():
        # An introduced subpackage, sourceless bytecode or native extension
        # can change imported code without changing any top-level *.py hash.
        # Ordinary CPython caches remain permitted, but not linked caches.
        linked = entry.is_symlink()
        junction = getattr(entry, "is_junction", None)
        if linked or (junction is not None and junction()):
            raise EngineSourceRejected("Unsafe engine source inventory")
        if entry.name == "__pycache__":
            if not entry.is_dir():
                raise EngineSourceRejected("Unsafe engine source inventory")
            continue
        if entry.is_dir() or entry.suffix.lower() in _IMPORTABLE_SUFFIXES:
            raise EngineSourceRejected("Unsafe engine source inventory")
        if entry.suffix.lower() != ".py":
            continue
        if (_MODULE_NAME.fullmatch(entry.name) is None or
                not entry.is_file() or entry.is_symlink()):
            raise EngineSourceRejected("Unsafe engine source inventory")
        names.append(entry.name)
    names.sort()
    if (not 2 <= len(names) <= MAX_MODULES or
            "__init__.py" not in names or "engine.py" not in names):
        raise EngineSourceRejected("Unsafe engine source inventory")
    return tuple(PACKAGE_PARTS + (name,) for name in names)


def snapshot_engine_sources(root: Path) -> dict[tuple[str, ...], bytes]:
    """Fingerprint every top-level fvs_suite Python module before tests run."""
    failed = False
    try:
        return {parts: source_fingerprint(root, parts) for parts in _engine_paths(root)}
    except (EngineSourceRejected, SourceSnapshotRejected, OSError, ValueError):
        failed = True
    if failed:
        # Emit no OS filename/error context, even on private host paths.
        raise EngineSourceRejected("Unsafe engine source inventory")
    raise EngineSourceRejected("Unsafe engine source inventory")


def engine_sources_unchanged(root: Path,
                             snapshots: dict[tuple[str, ...], bytes]) -> bool:
    """Require the same exact module set and all original content fingerprints."""
    if type(snapshots) is not dict or not snapshots:
        return False
    try:
        paths = _engine_paths(root)
        if tuple(snapshots) != paths:
            return False
        for parts in paths:
            digest = snapshots[parts]
            if (type(digest) is not bytes or len(digest) != 32 or
                    matches_source_fingerprint(root, parts, digest) is not True):
                return False
        return True
    except (EngineSourceRejected, SourceSnapshotRejected, OSError, ValueError, KeyError):
        return False
