"""Smoke-test the *installed Windows console EXE*, not just Python modules.

Usage: python desktop-software/fileproof/smoke_installed.py path/to/FileProofCLI.exe
No network, credentials, sensitive files, or third-party libraries required.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(binary: Path, expected: int, *arguments: str) -> str:
    result = subprocess.run([str(binary), *arguments], capture_output=True,
                            text=True, encoding="utf-8", errors="replace",
                            timeout=90, check=False)
    if result.returncode != expected:
        raise AssertionError(
            f"Expected exit {expected}, got {result.returncode} for {arguments[:1]}; "
            f"stdout={result.stdout[-500:]!r}; stderr={result.stderr[-500:]!r}"
        )
    return result.stdout


def smoke(binary: Path) -> None:
    binary = binary.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="fileproof-smoke-") as directory:
        temp = Path(directory)
        root = temp / "source"
        root.mkdir()
        tracked = root / "données.txt"
        tracked.write_text("original\n", encoding="utf-8")
        secret = temp / "passphrase.txt"
        secret.write_text("this-is-a-temporary-test-passphrase\n", encoding="utf-8")
        wrong = temp / "wrong.txt"
        wrong.write_text("a-different-test-passphrase\n", encoding="utf-8")
        manifest = temp / "manifest.json"

        run(binary, 0, "create", str(root), str(manifest),
            "--passphrase-file", str(secret))
        run(binary, 2, "create", str(root), str(manifest),
            "--passphrase-file", str(secret))
        original_manifest = manifest.read_bytes()

        result = run(binary, 0, "verify", str(root), str(manifest),
                     "--passphrase-file", str(secret))
        if "Manifest authentication: VERIFIED" not in result or "données.txt" not in result:
            raise AssertionError("Valid authenticated manifest was not verified.")
        run(binary, 2, "verify", str(root), str(manifest), "--passphrase-file", str(wrong))
        run(binary, 2, "verify", str(root), str(manifest))

        tracked.write_text("modified\n", encoding="utf-8")
        difference = run(binary, 1, "verify", str(root), str(manifest),
                         "--passphrase-file", str(secret))
        if "CHANGED" not in difference:
            raise AssertionError("Changed file was not reported.")
        tracked.write_text("original\n", encoding="utf-8")

        altered = json.loads(manifest.read_text(encoding="utf-8"))
        altered["files"][0]["sha256"] = "0" * 64
        manifest.write_text(json.dumps(altered), encoding="utf-8")
        run(binary, 2, "verify", str(root), str(manifest),
            "--passphrase-file", str(secret))
        manifest.write_bytes(original_manifest)

        stripped = json.loads(manifest.read_text(encoding="utf-8"))
        stripped.pop("authentication")
        manifest.write_text(json.dumps(stripped), encoding="utf-8")
        run(binary, 2, "verify", str(root), str(manifest),
            "--passphrase-file", str(secret))

        unsigned = temp / "unsigned.json"
        run(binary, 0, "create", str(root), str(unsigned))
        result = run(binary, 0, "verify", str(root), str(unsigned))
        if "authentication: NONE" not in result:
            raise AssertionError("Unsigned manifest must be visibly identified.")
        run(binary, 2, "verify", str(root), str(unsigned),
            "--passphrase-file", str(secret))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: smoke_installed.py FileProofCLI.exe", file=sys.stderr)
        raise SystemExit(2)
    smoke(Path(sys.argv[1]))
    print("PASS: installed FileProofCLI.exe authenticated-manifest smoke tests")
