#!/usr/bin/env python3
"""Local-only archive-byte witness. NOT a rights clearance or source authenticity opinion."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

IMAGES = (
    ("apollo.webp", 78346, 1041, 810, "image/webp",
     "https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp"),
    ("franklin.jpg", 466043, 960, 1526, "image/jpeg",
     "https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg"),
    ("nypl.jpg", 5553669, 5667, 3831, "image/jpeg",
     "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg"),
)


def inspect(path: Path):
    code = (
        "$x=@getimagesize($argv[1]);"
        "if(!$x){fwrite(STDERR,'invalid image');exit(2);}"
        "echo json_encode(array('width'=>$x[0],'height'=>$x[1],"
        "'mime'=>$x['mime']??''));"
    )
    result = subprocess.run(
        ["php", "-r", code, str(path)],
        check=True, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def build(media_dir: Path):
    images = {}
    for name, expected_bytes, width, height, mime, source_url in IMAGES:
        path = media_dir / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"{name}: missing file or symlink")
        size = path.stat().st_size
        if size != expected_bytes:
            raise ValueError(f"{name}: expected {expected_bytes} bytes; got {size}")
        measured = inspect(path)
        if measured != {"width": width, "height": height, "mime": mime}:
            raise ValueError(f"{name}: dimensions or MIME differ from original media metadata")
        images[name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": expected_bytes,
            "source_url": source_url,
        }
    return {
        "purpose": "isolated-staging-media-review",
        "images": images,
        "warning": (
            "Local byte fingerprints only. Confirm source identity against "
            "the original archival record and clear reproduction rights separately."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--media-dir", required=True, type=Path,
                   help="Directory of three independently checked downloaded originals")
    p.add_argument("--output", required=True, type=Path,
                   help="New manifest path; existing files are never overwritten")
    args = p.parse_args()
    if args.output.exists():
        p.error("Refusing to overwrite existing trusted image manifest")
    manifest = build(args.media_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf8") as stream:
        json.dump(manifest, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"manifest": str(args.output), "images": list(manifest["images"]),
                      "status": "BYTES_FINGERPRINTED_RIGHTS_NOT_CLEARED"}))


if __name__ == "__main__":
    main()
