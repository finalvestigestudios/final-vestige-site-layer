#!/usr/bin/env python3
"""Build the exact deterministic Site Layer package accepted by FVDB v0.3.1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "release-manifest.json"
REPOSITORY = "finalvestigestudios/final-vestige-site-layer"
BRANCH = "production"
ZIP_ROOT = "final-vestige-site-layer"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

PACKAGE_FILES = (
    "final-vestige-site-layer.php",
    "payloads/case-search-wp-block-v1.txt",
    "payloads/detail-lens-wp-block-v1.txt",
    "payloads/evidence-map-wp-block-v1.txt",
    "payloads/scale-board-wp-block-r4.txt",
    "payloads/signal-finder-wp-block-v1.txt",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_manifest(commit: str) -> bytes:
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise SystemExit("commit must be an exact 40-character lowercase SHA-1")

    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    files = []
    for rel in PACKAGE_FILES:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"missing package file: {rel}")
        data = path.read_bytes()
        files.append({"path": rel, "sha256": sha256(data), "bytes": len(data)})

    manifest = dict(source)
    manifest["repository"] = REPOSITORY
    manifest["branch"] = BRANCH
    manifest["commit"] = commit
    manifest["files"] = files

    return (
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")


def write_entry(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    zf.writestr(
        info,
        data,
        compress_type=zipfile.ZIP_STORED,
    )


def build(commit: str, output: Path) -> tuple[str, int]:
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_bytes = build_manifest(commit)

    entries: dict[str, bytes] = {
        f"{ZIP_ROOT}/{rel}": (ROOT / rel).read_bytes()
        for rel in PACKAGE_FILES
    }
    entries[f"{ZIP_ROOT}/release-manifest.json"] = manifest_bytes

    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_STORED
    ) as zf:
        for name in sorted(entries):
            write_entry(zf, name, entries[name])

    package = output.read_bytes()
    return sha256(package), len(package)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("commit")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    digest, size = build(args.commit.lower(), args.output)
    print(f"package={args.output}")
    print(f"sha256={digest}")
    print(f"bytes={size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
