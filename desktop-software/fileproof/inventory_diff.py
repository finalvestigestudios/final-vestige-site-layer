"""Enumerate new regular files and untracked filesystem links for FileProof.

This module never modifies files or follows symbolic links or Windows junctions.
Pre-existing links were excluded from v1 manifests, so their status is
UNTRACKED_LINK, not ADDED. Users should inspect them separately.
"""
from __future__ import annotations

import os
from pathlib import Path


def is_link(path: Path) -> bool:
    """Recognize symbolic links and Windows directory junctions."""
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def inventory_additions(
    root: Path, expected_paths: set[str], manifest_file: Path
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return unrecorded files/links and traversal errors.

    Only the exact selected manifest is excluded when it is inside root.
    Its symlinks are not excluded. This detects added regular files without
    following links outside the folder.
    """
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select a folder to verify.")
    manifest_absolute = Path(os.path.abspath(manifest_file))
    additions: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    def on_error(err: OSError) -> None:
        location = getattr(err, "filename", None)
        errors.append({"path": str(location or root), "error": str(err)})

    for directory, names, files in os.walk(root, topdown=True, followlinks=False, onerror=on_error):
        parent = Path(directory)
        traversable: list[str] = []
        for name in sorted(names):
            candidate = parent / name
            if is_link(candidate):
                relative = candidate.relative_to(root).as_posix()
                if relative not in expected_paths:
                    additions.append({"path": relative, "status": "UNTRACKED_LINK"})
            else:
                traversable.append(name)
        names[:] = traversable

        for name in sorted(files):
            candidate = parent / name
            relative = candidate.relative_to(root).as_posix()
            if relative in expected_paths:
                continue
            link = is_link(candidate)
            if not link and Path(os.path.abspath(candidate)) == manifest_absolute:
                continue
            additions.append({"path": relative, "status": "UNTRACKED_LINK" if link else "ADDED"})

    return additions, errors
