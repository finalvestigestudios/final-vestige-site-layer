"""Fail-closed Windows process-job custody for the internal source-test runner.

Not a sandbox: a subprocess can race job assignment during Popen, and privileged
or deliberately detached work is outside this guarantee. No release authorization.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os


class JobCustodyError(OSError):
    """Fixed message only: never include process arguments or private paths."""


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    )]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimits), ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _WindowsKernel:
    """Small Win32 API adapter; mockable without executing Windows binaries."""

    def __init__(self):
        if os.name != "nt":
            raise JobCustodyError("Windows job custody unavailable")
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.create = kernel.CreateJobObjectW
        self.create.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p)
        self.create.restype = ctypes.c_void_p
        self.set_information = kernel.SetInformationJobObject
        self.set_information.argtypes = (ctypes.c_void_p, wintypes.INT, ctypes.c_void_p, wintypes.DWORD)
        self.set_information.restype = wintypes.BOOL
        self.assign = kernel.AssignProcessToJobObject
        self.assign.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
        self.assign.restype = wintypes.BOOL
        self.terminate = kernel.TerminateJobObject
        self.terminate.argtypes = (ctypes.c_void_p, wintypes.UINT)
        self.terminate.restype = wintypes.BOOL
        self.close = kernel.CloseHandle
        self.close.argtypes = (ctypes.c_void_p,)
        self.close.restype = wintypes.BOOL

    def enable_kill_on_close(self, job: int) -> bool:
        info = _ExtendedLimits()
        info.BasicLimitInformation.LimitFlags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        return bool(self.set_information(job, 9, ctypes.byref(info), ctypes.sizeof(info)))


class WindowsJob:
    """Own a Windows Job Object until its process tree is terminated and reaped.

    Injection of ``api`` is exclusively for deterministic cross-platform unit
    tests. Production code uses the actual Win32 API. Assignment is deliberately
    fail-closed; nested-job policy can prevent it.
    """

    def __init__(self, proc: object, *, api: object | None = None):
        self._api = api if api is not None else _WindowsKernel()
        self._job = self._api.create(None, None)
        if not self._job:
            raise JobCustodyError("Windows job custody unavailable")
        try:
            if not self._api.enable_kill_on_close(self._job):
                raise JobCustodyError("Windows job custody unavailable")
            handle = getattr(proc, "_handle", None)
            if handle is None or not self._api.assign(self._job, handle):
                raise JobCustodyError("Windows job custody unavailable")
        except Exception:
            self.close()
            raise JobCustodyError("Windows job custody unavailable") from None

    def terminate(self) -> None:
        if self._job and not self._api.terminate(self._job, 1):
            raise JobCustodyError("Windows job custody unavailable")

    def close(self) -> None:
        if self._job:
            job, self._job = self._job, None
            if not self._api.close(job):
                raise JobCustodyError("Windows job custody unavailable")
