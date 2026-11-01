"""Resolve Windows PowerShell from the native Windows System32 directory.

Never search PATH or the working directory for a security preflight interpreter.
This *only* prevents process-name/path hijacking; it is not AV clearance,
Authenticode validation, or permission to release a desktop application.
"""
from __future__ import annotations

import ctypes
import os
import stat
import sys
from pathlib import Path


class PowerShellHold(ValueError):
    """The native Windows PowerShell executable cannot be trusted by location."""


def _native_system_directory() -> Path:
    """Call the OS API directly; ignore SystemRoot, windir, and search PATH."""
    if os.name != "nt" or sys.maxsize <= 2**32:
        raise PowerShellHold("Native 64-bit Windows is required")
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        getter = kernel32.GetSystemDirectoryW
        getter.argtypes = [ctypes.c_wchar_p, ctypes.c_uint]
        getter.restype = ctypes.c_uint
        buffer = ctypes.create_unicode_buffer(32768)
        count = getter(buffer, len(buffer))
        if not 0 < count < len(buffer) or len(buffer.value) != count:
            raise PowerShellHold("Native System32 discovery failed")
        return Path(buffer.value)
    except PowerShellHold:
        raise
    except (AttributeError, OSError, TypeError, ValueError, OverflowError):
        raise PowerShellHold("Native System32 discovery failed") from None


def _validate_system_powershell(system_directory: Path) -> Path:
    """Pure path guard; exposed for synthetic tests, not a caller override."""
    try:
        if (not isinstance(system_directory, Path)
                or not system_directory.is_absolute()
                or system_directory.name.casefold() != "system32"):
            raise PowerShellHold("Native System32 path is invalid")
        parent = system_directory / "WindowsPowerShell"
        version = parent / "v1.0"
        binary = version / "powershell.exe"
        for item in (system_directory, parent, version, binary):
            if item.is_symlink():
                raise PowerShellHold("Reparse-linked interpreter path is prohibited")
            is_junction = getattr(item, "is_junction", None)
            if is_junction is not None and is_junction():
                raise PowerShellHold("Junction interpreter path is prohibited")
        mode = binary.stat().st_mode
        if not stat.S_ISREG(mode):
            raise PowerShellHold("System PowerShell is not a regular file")
        with binary.open("rb") as executable:
            if executable.read(2) != b"MZ":
                raise PowerShellHold("System PowerShell is not a Windows PE image")
        return binary
    except PowerShellHold:
        raise
    except (AttributeError, OSError, TypeError, ValueError):
        raise PowerShellHold("Native PowerShell interpreter unavailable") from None


def require_system_powershell() -> Path:
    """Resolve an absolute OS-owned interpreter path without environment input."""
    return _validate_system_powershell(_native_system_directory())
