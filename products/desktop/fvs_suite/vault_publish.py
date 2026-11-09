"""Local-only, exclusive, byte-verified publication of encrypted vault archives.

A .fvault name never points at a partially written file during an ordinary
write/fsync failure: stage privately in the same directory, verify the bytes,
then publish with a no-overwrite operation. Does not promise power-loss atomic
filesystem metadata durability or defend against a hostile directory owner.
"""
from __future__ import annotations

import errno
import os
import stat
import tempfile
from pathlib import Path

MAX_VAULT_PUBLICATION_BYTES = 120 * 1024 * 1024
_BLOCK = 256 * 1024


def _sanitize_io(exc: OSError) -> OSError:
    if isinstance(exc, FileExistsError):
        return FileExistsError("Encrypted evidence destination already exists")
    code = exc.errno if type(exc.errno) is int and exc.errno > 0 else errno.EIO
    return OSError(code, "Encrypted evidence publication failed")


def _read_exact(fd: int, count: int) -> bytes:
    """Read one verification block even when the OS returns valid short reads.

    A premature EOF, non-byte result or overread is a verification failure, not
    a reason to publish. The bounded block size caps transient read memory.
    """
    parts = bytearray()
    while len(parts) < count:
        chunk = os.read(fd, count - len(parts))
        if type(chunk) is not bytes or not chunk or len(chunk) > count - len(parts):
            raise OSError(errno.EIO, "Incomplete encrypted evidence staging read")
        parts.extend(chunk)
    return bytes(parts)


def _write_and_verify(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        amount = os.write(fd, payload[offset:offset + _BLOCK])
        if type(amount) is not int or not (0 < amount <= min(_BLOCK, len(payload) - offset)):
            raise OSError(errno.EIO, "Incomplete encrypted evidence staging write")
        offset += amount
    if os.fstat(fd).st_size != len(payload):
        raise OSError(errno.EIO, "Encrypted evidence staging length mismatch")
    os.lseek(fd, 0, os.SEEK_SET)
    offset = 0
    while offset < len(payload):
        expected = payload[offset:offset + _BLOCK]
        actual = _read_exact(fd, len(expected))
        if actual != expected:
            raise OSError(errno.EIO, "Encrypted evidence staging byte mismatch")
        offset += len(expected)
    if os.read(fd, 1) != b"":
        raise OSError(errno.EIO, "Encrypted evidence staging extra bytes")
    os.fsync(fd)


def _same_stage_identity(actual: os.stat_result, owned: os.stat_result) -> bool:
    """Check ownership by the OS file identity, not a user-controlled path name."""
    return (stat.S_ISREG(actual.st_mode)
            and actual.st_dev == owned.st_dev
            and actual.st_ino == owned.st_ino)


def _owned_stage(path: str, owned: os.stat_result) -> os.stat_result | None:
    """Never unlink or publish a replacement staged pathname or a symlink."""
    try:
        actual = os.lstat(path)
    except FileNotFoundError:
        return None
    return actual if _same_stage_identity(actual, owned) else None


def _recheck_staged_bytes(path: str, owned: os.stat_result, payload: bytes) -> None:
    """Reject an in-place mutation after initial descriptor verification.

    This binds a second byte-for-byte read to the actual staged pathname before
    exclusive publication. It narrows, but cannot eliminate, same-user races.
    On Windows, O_BINARY prevents newline translation in raw descriptors.
    """
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        initial = os.fstat(fd)
        if (not _same_stage_identity(initial, owned) or initial.st_nlink != 1
                or initial.st_size != len(payload)):
            raise OSError(errno.EIO, "Encrypted evidence staged source changed")
        offset = 0
        while offset < len(payload):
            expected = payload[offset:offset + _BLOCK]
            if _read_exact(fd, len(expected)) != expected:
                raise OSError(errno.EIO, "Encrypted evidence staged bytes changed")
            offset += len(expected)
        if os.read(fd, 1) != b"":
            raise OSError(errno.EIO, "Encrypted evidence staged bytes appended")
        final = os.fstat(fd)
        if (not _same_stage_identity(final, owned) or final.st_nlink != 1
                or final.st_size != len(payload)
                or final.st_mtime_ns != initial.st_mtime_ns
                or final.st_ctime_ns != initial.st_ctime_ns):
            raise OSError(errno.EIO, "Encrypted evidence staged source mutated")
    finally:
        os.close(fd)
    named = _owned_stage(path, owned)
    if (named is None or named.st_nlink != 1 or named.st_size != len(payload)
            or named.st_mtime_ns != final.st_mtime_ns
            or named.st_ctime_ns != final.st_ctime_ns):
        raise OSError(errno.EIO, "Encrypted evidence staged name mutated")


def _verify_published_bytes(target: Path, owned: os.stat_result, payload: bytes) -> None:
    """Verify the *final* pathname after linking, not just its source stage.

    A different regular file or symlink can replace the staged pathname after
    the last prepublication check. The final descriptor, name and exact bytes
    must still identify our original ciphertext. This is a postcondition, not a
    lock against an adversary that continues mutating the directory afterward.
    """
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags)
    try:
        initial = os.fstat(fd)
        if not _same_stage_identity(initial, owned) or initial.st_size != len(payload):
            raise OSError(errno.EIO, "Encrypted evidence final file identity changed")
        offset = 0
        while offset < len(payload):
            expected = payload[offset:offset + _BLOCK]
            if _read_exact(fd, len(expected)) != expected:
                raise OSError(errno.EIO, "Encrypted evidence final bytes changed")
            offset += len(expected)
        if os.read(fd, 1) != b"":
            raise OSError(errno.EIO, "Encrypted evidence final size changed")
        final = os.fstat(fd)
        if (not _same_stage_identity(final, owned) or final.st_size != len(payload)
                or final.st_mtime_ns != initial.st_mtime_ns
                or final.st_ctime_ns != initial.st_ctime_ns):
            raise OSError(errno.EIO, "Encrypted evidence final file mutated")
    finally:
        os.close(fd)
    named = os.lstat(target)
    if (not _same_stage_identity(named, owned) or named.st_size != len(payload)
            or named.st_mtime_ns != final.st_mtime_ns
            or named.st_ctime_ns != final.st_ctime_ns):
        raise OSError(errno.EIO, "Encrypted evidence final name changed")


def _rollback_published_name(target: Path, observed: os.stat_result) -> None:
    """Best-effort cleanup; never unlink a *detectably* replaced final name."""
    try:
        current = os.lstat(target)
    except FileNotFoundError:
        return
    if (current.st_dev == observed.st_dev and current.st_ino == observed.st_ino
            and stat.S_IFMT(current.st_mode) == stat.S_IFMT(observed.st_mode)):
        os.unlink(target)


def _publish(target: Path, payload: bytes) -> None:
    # Avoid accidental publication through a symlinked destination directory.
    folder = target.parent
    parent = folder.lstat()
    if not stat.S_ISDIR(parent.st_mode):
        raise ValueError("Choose an existing regular vault output folder")
    try:
        target.lstat()
    except FileNotFoundError:
        pass
    else:
        raise FileExistsError("Encrypted evidence destination already exists")

    temporary = None
    descriptor = None
    owned = None
    try:
        descriptor, temporary = tempfile.mkstemp(
            prefix=".fvs-vault-", suffix=".partial", dir=folder)
        # Capture the private temp file's identity before writing. On filesystems
        # without useful file IDs, fail closed rather than link an unknown path.
        owned = os.lstat(temporary)
        if not stat.S_ISREG(owned.st_mode) or owned.st_ino == 0 or owned.st_nlink != 1:
            raise OSError(errno.EIO, "Invalid encrypted evidence staging identity")
        try:
            _write_and_verify(descriptor, payload)
            if not _same_stage_identity(os.fstat(descriptor), owned):
                raise OSError(errno.EIO, "Encrypted evidence staging descriptor changed")
        finally:
            # Clear ownership before close: a failed close must not trigger a
            # second close on an fd the OS may already have recycled.
            to_close, descriptor = descriptor, None
            os.close(to_close)
        # Check the name immediately before exclusive publication: a replaced
        # name must not cause unverified bytes or a symlink to be published.
        observed = _owned_stage(temporary, owned)
        if observed is None or observed.st_nlink != 1 or observed.st_size != len(payload):
            raise OSError(errno.EIO, "Encrypted evidence staging pathname changed")
        _recheck_staged_bytes(temporary, owned, payload)
        # An existing destination must NEVER be overwritten. POSIX rename
        # replaces, so use link; Windows rename refuses existing destinations.
        if os.name == "nt":
            os.rename(temporary, target)
        else:
            os.link(temporary, target)
        # The exclusive operation guarantees no clobber, but not which bytes
        # were behind the stage name in the final race window. Fail closed if
        # the published inode/contents do not match our verified ciphertext.
        published = os.lstat(target)
        try:
            _verify_published_bytes(target, owned, payload)
        except BaseException:
            _rollback_published_name(target, published)
            raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None and owned is not None:
            # POSIX link raises link count to two, so only compare stable
            # identity. Never delete an unrelated replacement at the temp path.
            if _owned_stage(temporary, owned) is not None:
                os.unlink(temporary)


def publish_vault(target: str | Path, payload: bytes) -> Path:
    """Atomically expose a complete ciphertext file, never replacing a name.

    Reject non-plain bytes and over-limit data before touching the disk. All
    expected OS errors use safe diagnostics without private exception chains;
    interrupts are not swallowed. Source documents are never modified.
    """
    if type(payload) is not bytes or len(payload) > MAX_VAULT_PUBLICATION_BYTES:
        raise ValueError("Invalid or oversized encrypted evidence bytes")
    destination = Path(target)
    redacted = None
    try:
        _publish(destination, payload)
    except OSError as exc:
        redacted = _sanitize_io(exc)
    if redacted is not None:
        # Raised outside the handler: no private __context__ or __cause__.
        raise redacted
    return destination
