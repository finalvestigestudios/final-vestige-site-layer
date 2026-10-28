"""FileProof — offline SHA-256 folder manifest creator and verifier.

No network access, no file modification. Requires Python 3.11+.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from inventory_diff import inventory_additions
from manifest_auth import (authenticate_manifest, verify_authentication,
                           load_manifest, save_new_manifest, read_passphrase_file)

VERSION = "0.2.0"
SCHEMA = "finalvestige.fileproof.v1"
CHUNK = 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect(root: Path, exclude: Path | None = None) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select a folder, not a file.")
    files = []
    errors = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        # Do not follow symlinked folders outside the selected tree.
        dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if path.is_symlink() or (exclude is not None and path.resolve() == exclude.resolve()):
                continue
            relative = path.relative_to(root).as_posix()
            try:
                before = path.stat()
                digest = sha256(path)
                after = path.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise OSError("File changed while hashing")
                files.append({"path": relative, "bytes": after.st_size, "sha256": digest})
            except (OSError, PermissionError) as exc:
                errors.append({"path": relative, "error": str(exc)})
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "errors": errors,
    }


def create_manifest(root: Path, destination: Path,
                    passphrase: str | None = None) -> dict:
    # Do not follow existing symlinks at the output path.
    destination = Path(os.path.abspath(destination))
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Refusing to overwrite an existing manifest.")
    manifest = collect(root, exclude=destination)
    if passphrase is not None:
        manifest = authenticate_manifest(manifest, passphrase)
    save_new_manifest(destination, manifest)
    return manifest


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("Unsafe path in manifest.")
    p = PurePosixPath(relative)
    if p.is_absolute() or ".." in p.parts or "." in p.parts or ":" in p.parts[0]:
        raise ValueError("Unsafe path in manifest.")
    result = root.joinpath(*p.parts)
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError("Manifest path escapes selected folder.")
    return result


def verify_manifest(root: Path, manifest_file: Path,
                    passphrase: str | None = None) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select a folder to verify.")
    manifest_file = manifest_file.resolve(strict=True)
    manifest = load_manifest(manifest_file)
    authenticated = verify_authentication(manifest, passphrase)
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("Not a supported FileProof manifest.")
    expected = manifest.get("files")
    original_errors = manifest.get("errors", [])
    if not isinstance(expected, list) or not isinstance(original_errors, list):
        raise ValueError("Invalid manifest entries or scan error records.")
    results = []
    seen = set()
    expected_paths = set()
    for item in expected:
        if not isinstance(item, dict):
            raise ValueError("Invalid manifest entry.")
        expected_hash = item.get("sha256")
        expected_size = item.get("bytes")
        if (not isinstance(expected_hash, str)
                or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
                or not isinstance(expected_size, int)
                or isinstance(expected_size, bool)
                or expected_size < 0):
            raise ValueError("Invalid file size or checksum in manifest.")
        relative = item.get("path")
        path = safe_path(root, relative)
        key = relative.casefold() if os.name == "nt" else relative
        if key in seen:
            raise ValueError("Duplicate path in manifest.")
        seen.add(key)
        expected_paths.add(relative)
        if path.is_symlink():
            status = "CHANGED"
        elif not path.is_file():
            status = "MISSING"
        else:
            try:
                before = path.stat()
                digest = sha256(path)
                after = path.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    status = "UNSTABLE"
                else:
                    status = "OK" if (after.st_size == expected_size and digest == expected_hash) else "CHANGED"
            except OSError:
                status = "UNREADABLE"
        results.append({"path": relative, "status": status})
    additions, traversal_errors = inventory_additions(root, expected_paths, manifest_file)
    return {
        "total": len(results),
        "authenticated": authenticated,
        "ok": sum(item["status"] == "OK" for item in results),
        "added": sum(item["status"] == "ADDED" for item in additions),
        "untracked_links": sum(item["status"] == "UNTRACKED_LINK" for item in additions),
        "results": results + additions,
        "scan_errors": original_errors + traversal_errors,
    }


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk()
    app.title(f"FileProof {VERSION} · Final Vestige Studios")
    app.geometry("760x520")
    app.minsize(620, 420)
    root_var = tk.StringVar()
    status_var = tk.StringVar(value="Choose a folder to create or verify a file integrity manifest.")
    frame = ttk.Frame(app, padding=22)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="FileProof", font=("Segoe UI", 24, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Verify what changed. Keep the files where they are.").pack(anchor="w", pady=(0, 20))
    ttk.Label(frame, text="Folder").pack(anchor="w")
    line = ttk.Frame(frame)
    line.pack(fill="x", pady=(4, 18))
    ttk.Entry(line, textvariable=root_var).pack(side="left", fill="x", expand=True)
    ttk.Button(line, text="Browse…", command=lambda: root_var.set(filedialog.askdirectory() or root_var.get())).pack(side="left", padx=(8, 0))
    output = tk.Text(frame, wrap="none", height=14, state="disabled")
    output.pack(fill="both", expand=True, pady=(12, 8))
    ttk.Label(frame, textvariable=status_var).pack(anchor="w")

    def show(text: str) -> None:
        output.config(state="normal")
        output.delete("1.0", "end")
        output.insert("1.0", text)
        output.config(state="disabled")

    def run_create() -> None:
        if not root_var.get():
            messagebox.showwarning("Select a folder", "Choose the folder to inspect.")
            return
        filename = filedialog.asksaveasfilename(title="Save manifest", defaultextension=".json",
                                                 filetypes=[("FileProof manifest", "*.json")])
        if not filename:
            return
        try:
            result = create_manifest(Path(root_var.get()), Path(filename))
            status_var.set(f"Manifest created: {len(result['files'])} files; {len(result['errors'])} unreadable.")
            show(json.dumps({"saved_to": filename, "files": len(result["files"]), "errors": result["errors"]}, indent=2))
        except Exception as exc:
            messagebox.showerror("Could not create manifest", str(exc))

    def run_verify() -> None:
        if not root_var.get():
            messagebox.showwarning("Select a folder", "Choose the folder to verify.")
            return
        filename = filedialog.askopenfilename(title="Open manifest", filetypes=[("FileProof manifest", "*.json")])
        if not filename:
            return
        try:
            result = verify_manifest(Path(root_var.get()), Path(filename))
            status_var.set(f"Verified {result['ok']} of {result['total']} recorded files; {result['added']} added; {result['untracked_links']} untracked links; {len(result['scan_errors'])} scan errors.")
            show("\n".join(f"{x['status']:10} {x['path']}" for x in result["results"]) or "No files in manifest.")
        except Exception as exc:
            messagebox.showerror("Could not verify manifest", str(exc))

    buttons = ttk.Frame(frame)
    buttons.pack(fill="x", before=output)
    ttk.Button(buttons, text="Create manifest", command=run_create).pack(side="left")
    ttk.Button(buttons, text="Verify manifest", command=run_verify).pack(side="left", padx=10)
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline folder integrity manifests")
    commands = parser.add_subparsers(dest="command")
    create = commands.add_parser("create")
    create.add_argument("folder")
    create.add_argument("manifest")
    verify = commands.add_parser("verify")
    verify.add_argument("folder")
    verify.add_argument("manifest")
    args = parser.parse_args()
    if args.command is None:
        gui()
        return 0
    try:
        if args.command == "create":
            result = create_manifest(Path(args.folder), Path(args.manifest))
            print(f"Recorded {len(result['files'])} files; errors: {len(result['errors'])}")
            return 2 if result["errors"] else 0
        result = verify_manifest(Path(args.folder), Path(args.manifest))
        for entry in result["results"]:
            print(f"{entry['status']:10} {entry['path']}")
        print(f"{result['ok']}/{result['total']} unchanged; {result['added']} added; {result['untracked_links']} untracked links; {len(result['scan_errors'])} scan errors")
        return 0 if (result["ok"] == result["total"] and result["added"] == 0
                     and result["untracked_links"] == 0 and not result["scan_errors"]) else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
