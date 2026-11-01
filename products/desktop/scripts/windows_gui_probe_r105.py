"""Native Windows GUI pre-release observation for the six local-first desktop EXEs.

This is NOT a screen-reader or keyboard acceptance test, a premium-license
activation, a malware scan, a release permit, or a replacement for the R9 gate.
It never selects customer files or invokes Generate/Review. Executables are
verified with the existing R9 PE/checksum gate before AND after observation.
Only the four free app windows may open. The two premium apps must instead
display their signed-authority-not-configured lock dialog, not the main editor.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from release_gate import verify as verify_candidate, GateFailure
from report_evidence import prepare_report_path, publish_report

WINDOWS = (
    ("LedgerDiffLite.exe", "Final Vestige Labs — LedgerDiff Lite", "main"),
    ("InvoiceTwinScout.exe", "Final Vestige Labs — Invoice Twin Scout", "main"),
    ("SpendMapLite.exe", "Final Vestige Labs — SpendMap Lite", "main"),
    ("PolicyDeltaDesk.exe", "Final Vestige Labs — Policy Delta Desk", "main"),
    ("GrantAuditStudioPro.exe", "Premium preview locked", "locked"),
    ("ProcureGuardStudioPro.exe", "Premium preview locked", "locked"),
)
FORBIDDEN_PREMIUM = (
    "Final Vestige Labs — GrantAudit Studio Pro — development preview",
    "Final Vestige Labs — ProcureGuard Studio Pro — development preview",
)
ERROR = "BLOCKED: native Windows GUI/pre-release entitlement observation failed"
MAX_SECONDS = 45


class GUIBlocked(ValueError):
    pass


def _descends(pid: int, root: int, parents: dict[int, int]) -> bool:
    """Match only a launched PyInstaller process or its children, not others."""
    seen: set[int] = set()
    for _ in range(64):
        if pid == root:
            return True
        if pid <= 0 or pid in seen:
            return False
        seen.add(pid)
        pid = parents.get(pid, 0)
    return False


def _admit(windows: list[tuple[int, int, str]], baseline: set[int],
           parents: dict[int, int], root: int, expected: str,
           kind: str) -> bool:
    """Never accept a pre-existing or unrelated window with a matching title."""
    owned = [(handle, title) for handle, pid, title in windows
             if handle not in baseline and _descends(pid, root, parents)]
    if kind == "locked" and any(title in FORBIDDEN_PREMIUM for _, title in owned):
        raise GUIBlocked("Premium application exposed its main window")
    return any(title == expected for _, title in owned)


def _windows_snapshot() -> tuple[dict[int, int], list[tuple[int, int, str]]]:
    """Read only process ancestry, HWND and visible window captions in memory.

    No process names, paths or unrelated captions are ever written to output.
    The fixed-size Win32 declarations support GitHub's native Windows x64.
    """
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    user = ctypes.WinDLL("user32", use_last_error=True)

    class ProcessEntry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", wintypes.LONG), ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    kernel.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(ProcessEntry))
    kernel.Process32FirstW.restype = wintypes.BOOL
    kernel.Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(ProcessEntry))
    kernel.Process32NextW.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL

    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)  # TH32CS_SNAPPROCESS
    if snapshot in (None, 0, ctypes.c_void_p(-1).value):
        raise GUIBlocked("Windows process snapshot unavailable")
    parents: dict[int, int] = {}
    try:
        entry = ProcessEntry()
        entry.dwSize = ctypes.sizeof(ProcessEntry)
        ok = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        if not ok:
            raise GUIBlocked("Windows process enumeration unavailable")
        while ok:
            parents[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
            ok = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)

    CALLBACK = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user.EnumWindows.argtypes = (CALLBACK, wintypes.LPARAM)
    user.EnumWindows.restype = wintypes.BOOL
    user.IsWindowVisible.argtypes = (wintypes.HWND,)
    user.IsWindowVisible.restype = wintypes.BOOL
    user.GetWindowTextLengthW.argtypes = (wintypes.HWND,)
    user.GetWindowTextLengthW.restype = ctypes.c_int
    user.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
    user.GetWindowTextW.restype = ctypes.c_int
    user.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
    user.GetWindowThreadProcessId.restype = wintypes.DWORD
    windows: list[tuple[int, int, str]] = []

    def collect(hwnd, _):
        if not user.IsWindowVisible(hwnd):
            return True
        length = user.GetWindowTextLengthW(hwnd)
        if not 0 < length < 180:
            return True
        title_buffer = ctypes.create_unicode_buffer(length + 1)
        if user.GetWindowTextW(hwnd, title_buffer, length + 1) != length:
            return True
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        windows.append((int(hwnd), int(owner.value), title_buffer.value))
        return True

    callback = CALLBACK(collect)
    if not user.EnumWindows(callback, 0):
        raise GUIBlocked("Windows GUI enumeration unavailable")
    return parents, windows


def _terminate_tree(process: subprocess.Popen) -> None:
    """Never kill a process we did not start; remove one-file bootloader child."""
    if os.name != "nt":
        raise GUIBlocked("Native Windows process cleanup unavailable")
    try:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        process.kill()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _observe_one(root: Path, name: str, expected: str,
                 kind: str, seconds: int) -> dict:
    _, before = _windows_snapshot()
    baseline = {hwnd for hwnd, _, _ in before}
    process = subprocess.Popen([str((root / name).resolve(strict=True))],
                               cwd=str(root.resolve(strict=True)),
                               stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    found = False
    try:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            parents, visible = _windows_snapshot()
            if _admit(visible, baseline, parents, process.pid, expected, kind):
                # Check again for a mistakenly exposed premium main editor.
                time.sleep(0.25)
                parents, visible = _windows_snapshot()
                if kind == "locked":
                    _admit(visible, baseline, parents, process.pid, expected, kind)
                found = True
                break
            if process.poll() is not None:
                raise GUIBlocked("Candidate exited before a verified GUI surface appeared")
            time.sleep(0.25)
    finally:
        _terminate_tree(process)
    if not found:
        raise GUIBlocked("Expected native Windows surface not observed")
    return {"executable": name, "surface": "main_window" if kind == "main"
            else "premium_lock_dialog", "status": "PASS"}


def probe(root: Path, *, seconds: int = MAX_SECONDS) -> dict:
    """Verify genuine PE-candidate custody and each spawned window/lock surface."""
    if os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        raise GUIBlocked("A native Windows x64 GUI runner is required")
    if not 5 <= seconds <= 120:
        raise GUIBlocked("Unapproved GUI observation timeout")
    before = verify_candidate(root, smoke=False)
    if [a["name"] for a in before["artifacts"]] != [a[0] for a in WINDOWS]:
        raise GUIBlocked("Unexpected six-product candidate inventory")
    observed = []
    for name, title, kind in WINDOWS:
        observed.append(_observe_one(root, name, title, kind, seconds))
    after = verify_candidate(root, smoke=False)
    if (before["checksums_sha256"] != after["checksums_sha256"] or
            [(a["name"], a["sha256"]) for a in before["artifacts"]] !=
            [(a["name"], a["sha256"]) for a in after["artifacts"]]):
        raise GUIBlocked("Candidate bytes changed during GUI checks")
    return {"schema": "fvs-native-gui-r105", "kind": "WINDOWS_GUI_OBSERVATION_ONLY",
            "released": False, "qd_approved": False,
            "premium_entitlement_verified": False,
            "screen_reader_verified": False, "keyboard_verified": False,
            "windows_native_gui_observed": True, "surfaces": observed,
            "candidate_checksums_sha256": before["checksums_sha256"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--seconds", type=int, default=MAX_SECONDS)
    args = parser.parse_args(argv)
    try:
        if args.report:
            output = prepare_report_path(args.report, args.dist)
        else:
            output = None
        result = probe(args.dist, seconds=args.seconds)
        if output is not None:
            publish_report(output, result)
    except (GUIBlocked, GateFailure, OSError, ValueError, RuntimeError,
            subprocess.SubprocessError):
        print(ERROR, file=sys.stderr)
        return 1
    print("PASS: four native free-app windows and two premium locked dialogs; "
          "NOT keyboard/WCAG/AV/QD/release approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
