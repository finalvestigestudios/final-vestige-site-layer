"""Locate Defender exclusively through native Windows known folders (R116).

The ProgramData/ProgramFiles *environment variables are untrusted input* and
must not choose a security scanner. This is a path-origin guard, not proof of
Authenticode validity, active malware protection or distribution approval.
"""
from __future__ import annotations

import ctypes
import os
import re
import stat
import sys
from pathlib import Path
from uuid import UUID


class InstallHold(ValueError):
    """Cannot establish a native, non-reparse Defender installation path."""


class _GUID(ctypes.Structure):
    _fields_ = [("Data1", ctypes.c_uint32), ("Data2", ctypes.c_uint16),
                ("Data3", ctypes.c_uint16), ("Data4", ctypes.c_ubyte * 8)]


PROGRAM_DATA = "62ab5d82-fdc1-4dc3-a9dd-070d1d495d97"
PROGRAM_FILES = "905e63b6-c1bf-494e-b29c-65b732d3d21a"
VERSION = re.compile(r"\A[0-9]+(?:\.[0-9]+){2,4}(?:-[0-9]+)?\Z", re.ASCII)


def _known_folder(identifier: str) -> Path:
    """SHGetKnownFolderPath rather than environment, PATH or an inferred drive."""
    if os.name != "nt" or sys.maxsize <= 2**32:
        raise InstallHold("Native 64-bit Windows known folders required")
    output = ctypes.c_wchar_p()
    try:
        guid = _GUID.from_buffer_copy(UUID(identifier).bytes_le)
        shell = ctypes.WinDLL("shell32", use_last_error=True)
        lookup = shell.SHGetKnownFolderPath
        lookup.argtypes = [ctypes.POINTER(_GUID), ctypes.c_ulong,
                           ctypes.c_void_p, ctypes.POINTER(ctypes.c_wchar_p)]
        lookup.restype = ctypes.c_long
        code = lookup(ctypes.byref(guid), 0, None, ctypes.byref(output))
        if code != 0 or not output.value:
            raise InstallHold("Windows known-folder resolution failed")
        return Path(output.value)
    except InstallHold:
        raise
    except (AttributeError, OSError, TypeError, ValueError, OverflowError):
        raise InstallHold("Windows known-folder resolution unavailable") from None
    finally:
        if output.value:
            try:
                free = ctypes.WinDLL("ole32").CoTaskMemFree
                free.argtypes = [ctypes.c_void_p]
                free.restype = None
                free(ctypes.cast(output, ctypes.c_void_p))
            except (AttributeError, OSError, TypeError):
                # Cannot safely trust the attempt if the native contract fails.
                raise InstallHold("Windows known-folder cleanup unavailable") from None


def _no_reparse(path: Path) -> None:
    """Reject symlinks and junctions along the *entire* path ancestry."""
    for node in (path, *path.parents):
        if node.is_symlink() or (getattr(node, "is_junction", lambda: False)()):
            raise InstallHold("Reparse-linked Defender path prohibited")


def _root(path: Path) -> Path:
    try:
        if not isinstance(path, Path) or not path.is_absolute():
            raise InstallHold("Known folder is not absolute")
        _no_reparse(path)
        if not path.is_dir():
            raise InstallHold("Known folder is unavailable")
        return path
    except InstallHold:
        raise
    except (OSError, ValueError, RuntimeError):
        raise InstallHold("Known folder cannot be verified") from None


def native_roots() -> tuple[Path, Path]:
    """Return verified ProgramData and native 64-bit Program Files roots."""
    data = _root(_known_folder(PROGRAM_DATA))
    files = _root(_known_folder(PROGRAM_FILES))
    if data == files:
        raise InstallHold("Defender roots cannot be identical")
    return data, files


def require_candidate(path: Path, data: Path, files: Path) -> Path:
    """Accept only a regular MpCmdRun.exe in native Defender layout.

    Non-reparse ancestry is checked before signing/hash custody checks in the
    caller. The OS-owned roots are NOT configurable by customer or CLI input.
    """
    try:
        if not isinstance(path, Path) or not path.is_absolute() or ".." in path.parts:
            raise InstallHold("Defender candidate path is not canonical")
        if path.name.casefold() != "mpcmdrun.exe":
            raise InstallHold("Unexpected scanner executable")
        platform = data / "Microsoft" / "Windows Defender" / "Platform"
        legacy = files / "Windows Defender" / "MpCmdRun.exe"
        # Version labels are checked by the existing numeric engine discovery.
        modern = (path.parent.parent == platform and
                  VERSION.fullmatch(path.parent.name) is not None)
        if path != legacy and not modern:
            raise InstallHold("Scanner is outside native Defender installation")
        _no_reparse(path)
        if not stat.S_ISREG(path.stat().st_mode):
            raise InstallHold("Defender scanner is not an ordinary file")
        if not _root(data) or not _root(files):
            raise InstallHold("Defender roots are not trusted")
        return path
    except InstallHold:
        raise
    except (OSError, ValueError, RuntimeError):
        raise InstallHold("Defender candidate path could not be validated") from None
