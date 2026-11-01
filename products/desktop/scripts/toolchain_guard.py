"""Offline custody of Python, PyInstaller and packaging dependencies for six EXEs.

This is a change-detection gate, not signed supply-chain provenance, malware
clearance, Windows executable verification, QD approval, or a release permit.
Never stores absolute paths, customer inputs, environment variables or secrets.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys

DESKTOP = Path(__file__).resolve().parents[1]
ROOT = DESKTOP.parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from report_evidence import prepare_report_path, publish_report

SCHEMA = "fvs-windows-toolchain-custody-v1"
REQUIRED = ("pyinstaller", "pyinstaller-hooks-contrib", "altgraph", "cryptography")
OPTIONAL = ("cffi", "packaging", "pefile", "pywin32-ctypes")
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_DIST_FILES = 4096
MAX_DIST_BYTES = 512 * 1024 * 1024
MAX_MANIFEST_BYTES = 16 * 1024
ERROR = "REJECTED: Windows packaging toolchain custody could not be verified"


def _identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _same_path_descriptor_identity(path_info: os.stat_result,
                                   descriptor_info: os.stat_result,
                                   *, windows: bool | None = None,
                                   executable_path: bool = False) -> bool:
    """Guard two OS stat views; never loosen before/after same-view custody.

    Windows 3.12 path-vs-descriptor ctime can disagree (R101). Hosted R104
    additionally proved only st_mode disagreed for a *synthetic .exe* runtime,
    while dev, inode, link count, size, mtime and ctime agreed. Windows marks
    executable permission from pathname suffix; a descriptor need not do so.
    Accept only those executable permission-bit differences for a regular
    .exe file, never for manifests, Python modules or other file types.
    """
    if windows is None:
        windows = os.name == "nt"
    path_identity = _identity(path_info)
    descriptor_identity = _identity(descriptor_info)
    if not windows:
        return path_identity == descriptor_identity
    if not executable_path:
        return path_identity[:-1] == descriptor_identity[:-1]
    if not (stat.S_ISREG(path_info.st_mode) and
            stat.S_ISREG(descriptor_info.st_mode)):
        return False
    execute_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    if (path_info.st_mode ^ descriptor_info.st_mode) & ~execute_bits:
        return False
    # Only ctime and path-extension executable flags may differ cross-view.
    # All other stat identity values are still compared exactly.
    return all(path_identity[index] == descriptor_identity[index]
               for index in (0, 1, 3, 4, 5))


def _file_record(path: Path) -> tuple[str, tuple[int, ...], int]:
    """Hash descriptor-checked bytes, rejecting links, swaps, and oversized data."""
    fd = None
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or before.st_size > MAX_FILE_BYTES):
            raise ValueError("Unsafe toolchain file")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                     | getattr(os, "O_BINARY", 0))
        opened = os.fstat(fd)
        # Only a Windows .exe pathname may expose extension-derived execute
        # bits that the opened descriptor does not. Never relax other files.
        executable_path = os.name == "nt" and path.suffix.lower() == ".exe"
        if not _same_path_descriptor_identity(
                before, opened, executable_path=executable_path):
            raise ValueError("Toolchain file replaced")
        digest = hashlib.sha256()
        length = 0
        while True:
            chunk = os.read(fd, 64 * 1024)
            if not chunk:
                break
            length += len(chunk)
            if length > MAX_FILE_BYTES:
                raise ValueError("Oversized toolchain file")
            digest.update(chunk)
        finished = os.fstat(fd)
        after = path.lstat()
        if (length != before.st_size
                or _identity(finished) != _identity(opened)
                or _identity(after) != _identity(before)
                or not _same_path_descriptor_identity(
                    after, finished, executable_path=executable_path)):
            raise ValueError("Toolchain file modified")
        return digest.hexdigest(), _identity(before), length
    except (OSError, RuntimeError):
        raise ValueError("Unsafe toolchain file") from None
    finally:
        if fd is not None:
            os.close(fd)


def _distribution_record(name: str, root: Path, lookup) -> dict:
    try:
        dist = lookup(name)
    except metadata.PackageNotFoundError:
        if name in REQUIRED:
            raise ValueError("Missing required packaging distribution") from None
        return {"name": name, "status": "absent"}
    version = dist.version
    entries = dist.files
    if not isinstance(version, str) or not version or len(version) > 128 or entries is None:
        raise ValueError("Distribution has no bounded installed inventory")
    selected = []
    for entry in entries:
        relative = str(entry).replace("\\", "/")
        parts = relative.split("/")
        # Installer-generated console scripts outside site-packages are not
        # imported by `python -I -m PyInstaller`; exclude them explicitly.
        if any(p in ("", ".", "..") for p in parts) or PurePosixPath(relative).is_absolute():
            continue
        selected.append((relative, entry))
    selected.sort(key=lambda item: item[0])
    if (not selected or len(selected) > MAX_DIST_FILES or
            len({name for name, _ in selected}) != len(selected)):
        raise ValueError("Incomplete or ambiguous installed package inventory")
    digest = hashlib.sha256()
    total = 0
    for relative, entry in selected:
        path = Path(dist.locate_file(entry))
        # Installed packages must not reside inside the untrusted checkout.
        # This guards against a repo-local fake PyInstaller module.
        if path.resolve(strict=True).is_relative_to(root):
            raise ValueError("Packaging distribution inside checkout")
        file_hash, identity, size = _file_record(path)
        total += size
        if total > MAX_DIST_BYTES:
            raise ValueError("Packaging distribution exceeds inventory bound")
        record = json.dumps([relative, file_hash, list(identity)],
                            separators=(",", ":"), ensure_ascii=True)
        digest.update(record.encode("utf-8") + b"\n")
    return {"name": name, "status": "installed", "version": version,
            "file_count": len(selected), "bytes": total,
            "inventory_sha256": digest.hexdigest()}


def snapshot(root: Path, *, lookup=None, runtime: Path | None = None) -> dict:
    root = Path(root).resolve(strict=True)
    runtime = Path(sys.executable if runtime is None else runtime)
    if runtime.resolve(strict=True).is_relative_to(root):
        raise ValueError("Python interpreter inside checkout")
    python_hash, identity, _ = _file_record(runtime)
    lookup = metadata.distribution if lookup is None else lookup
    packages = [_distribution_record(name, root, lookup)
                for name in (*REQUIRED, *OPTIONAL)]
    return {"schema": SCHEMA,
            "scope": "PROCESS_LOCAL_TOOLCHAIN_ONLY_NOT_EXECUTABLE_OR_QD_PROOF",
            "released": False, "qd_approved": False,
            "windows_executables_verified": False,
            "premium_download_authorized": False,
            "runtime": {"implementation": sys.implementation.name,
                        "version": list(sys.version_info[:3]),
                        "sha256": python_hash, "identity": list(identity)},
            "distributions": packages}


def capture(root: Path, destination: Path, **kwargs) -> None:
    root = Path(root).resolve(strict=True)
    destination = prepare_report_path(destination, root)
    state = snapshot(root, **kwargs)
    if snapshot(root, **kwargs) != state:
        raise ValueError("Toolchain changed before custody publication")
    publish_report(destination, state)
    if snapshot(root, **kwargs) != state:
        raise ValueError("Toolchain changed during custody publication")


def _read_manifest(root: Path, path: Path) -> dict:
    root = Path(root).resolve(strict=True)
    path = Path(path)
    parent = path.parent.resolve(strict=True)
    if parent == root or root in parent.parents or not parent.is_dir():
        raise ValueError("Toolchain manifest must be outside checkout")
    safe_path = parent / path.name
    before = safe_path.lstat()
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            or before.st_size > MAX_MANIFEST_BYTES):
        raise ValueError("Unsafe toolchain manifest")
    fd = None
    try:
        fd = os.open(safe_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        opened = os.fstat(fd)
        if not _same_path_descriptor_identity(before, opened):
            raise ValueError("Toolchain manifest replaced")
        data = bytearray()
        while len(data) <= MAX_MANIFEST_BYTES:
            part = os.read(fd, min(4096, MAX_MANIFEST_BYTES + 1 - len(data)))
            if not part:
                break
            data.extend(part)
        finished = os.fstat(fd)
        after = safe_path.lstat()
        if (len(data) != before.st_size or len(data) > MAX_MANIFEST_BYTES
                or _identity(finished) != _identity(opened)
                or _identity(after) != _identity(before)
                or not _same_path_descriptor_identity(after, finished)):
            raise ValueError("Toolchain manifest modified")
    finally:
        if fd is not None:
            os.close(fd)

    def unique_keys(pairs):
        result = {}
        for name, value in pairs:
            if name in result:
                raise ValueError("Duplicate manifest field")
            result[name] = value
        return result

    loaded = json.loads(data.decode("utf-8"), object_pairs_hook=unique_keys)
    if (type(loaded) is not dict or loaded.get("schema") != SCHEMA
            or set(loaded) != {"schema", "scope", "released", "qd_approved",
                               "windows_executables_verified", "premium_download_authorized",
                               "runtime", "distributions"}
            or any(loaded.get(key) is not False for key in
                   ("released", "qd_approved", "windows_executables_verified",
                    "premium_download_authorized"))):
        raise ValueError("Invalid toolchain manifest")
    return loaded


def check(root: Path, destination: Path, **kwargs) -> None:
    before = _read_manifest(root, destination)
    if snapshot(root, **kwargs) != before:
        raise ValueError("Packaging interpreter or installed dependencies changed")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "check"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.action == "capture":
            capture(args.root, args.manifest)
        else:
            check(args.root, args.manifest)
    except (OSError, ValueError, RuntimeError, TypeError, UnicodeError,
            json.JSONDecodeError):
        print(ERROR, file=sys.stderr)
        return 1
    print("PASS: Python and installed packaging inputs unchanged; NOT EXE/QD/release proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
