"""R211 fail-closed local I/O for Preparedness evidence tools (Issue #136).

No existing file is ever written; report creation is exclusive and outside the
checked-out source tree. Descriptor-relative opens block symlinked ancestors,
leaf symlinks, and path-component swap attacks during traversal. These are
integrity gates, not evidence of medical review or permission to publish.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path, PurePosixPath
import stat

class GuardViolation(ValueError):
    """Unsafe local source/report path; fail closed."""

_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
_READ = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
_WRITE_NEW = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC


def _absolute(path: Path) -> Path:
    """Lexically normalize, WITHOUT silently following symlinks."""
    return Path(os.path.abspath(os.fspath(path)))


@contextmanager
def _directory(path: Path):
    """Open each ancestor by descriptor, never traversing a symlink."""
    absolute = _absolute(path)
    fd = os.open('/', _DIR)
    try:
        for component in absolute.parts[1:]:
            try:
                child = os.open(component, _DIR, dir_fd=fd)
            except OSError as exc:
                raise GuardViolation('unsafe, missing or symlinked directory: ' + str(absolute)) from exc
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def _relative_components(path: str) -> tuple[str, ...]:
    if not isinstance(path, str) or not path or '\\' in path:
        raise GuardViolation('invalid relative source path')
    parsed = PurePosixPath(path)
    parts = parsed.parts
    if parsed.is_absolute() or any(p in ('', '.', '..') for p in parts) or str(parsed) != path:
        raise GuardViolation('noncanonical or unsafe source path')
    return parts


def read_files(checkout: Path, names) -> dict[str, bytes]:
    """Read only ordinary files beneath a non-symlinked checkout directory."""
    result = {}
    with _directory(checkout) as root:
        for name in names:
            parts = _relative_components(name)
            cur = os.dup(root)
            try:
                for component in parts[:-1]:
                    try:
                        child = os.open(component, _DIR, dir_fd=cur)
                    except OSError as exc:
                        raise GuardViolation('unsafe, missing or symlinked source directory: ' + name) from exc
                    os.close(cur)
                    cur = child
                try:
                    leaf = os.open(parts[-1], _READ, dir_fd=cur)
                except OSError as exc:
                    raise GuardViolation('unsafe, missing or symlinked source file: ' + name) from exc
                with os.fdopen(leaf, 'rb') as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        raise GuardViolation('non-regular source file: ' + name)
                    result[name] = stream.read()
            finally:
                os.close(cur)
    return result


def write_new_report(report: Path, checkout: Path, content: str) -> None:
    """Atomically create private output outside checkout; refuse ALL overwrites.

    Does not create directories, follow symlinks or replace preexisting files.
    Rejects paths inside checkout, even when the checkout itself is absent.
    """
    root = _absolute(checkout)
    target = _absolute(report)
    if target == root or root in target.parents:
        raise GuardViolation('report path is inside protected checkout')
    if not target.name or target.name in ('.', '..'):
        raise GuardViolation('invalid report basename')
    with _directory(target.parent) as parent:
        try:
            fd = os.open(target.name, _WRITE_NEW, 0o600, dir_fd=parent)
        except OSError as exc:
            raise GuardViolation('report already exists or is unsafe: ' + str(target)) from exc
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(content)
