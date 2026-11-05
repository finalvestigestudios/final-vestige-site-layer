#!/usr/bin/env python3
"""Offline fail-closed archival image parity check. No network, writes, or CMS access.

Requires existing lawful local copies; an apparent match is only a *review lead*,
never a rights clearance, provenance proof, performance measurement or release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from PIL import Image, ImageChops, ImageOps, UnidentifiedImageError

SCHEMA = "fv-offline-visual-identity-gate-v1"
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_PIXELS = 70_000_000
MAX_WIDTH = 960
URL_PATTERN = re.compile(r"^https://[^\s?#]+(?:[?#][^\s]*)?$", re.I)
KEY_PATTERN = re.compile(r"^[1-9]\d*:[0-9]+$")
ACCEPTED_FORMATS = {"JPEG", "PNG", "WEBP"}
# Synthetic and resized-file regression tests establish that these reject grossly
# different photographs. They do NOT establish archival identity or pixel equality.
MAX_DHASH_DISTANCE = 9
MAX_GREY_MAE = 14.0


def _reject(reason: str) -> ValueError:
    return ValueError(reason)


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith(("/", "\\")):
        raise _reject("invalid relative local path")
    if "://" in relative or "\\" in relative:
        raise _reject("URL or backslash path forbidden")
    parts = Path(relative).parts
    if any(x in ("..", ".") for x in parts) or len(parts) == 0:
        raise _reject("traversal/empty path forbidden")
    p = root
    for component in parts:
        p = p / component
        if p.is_symlink():
            raise _reject("symlink in source path forbidden")
    if not p.is_file():
        raise _reject("local file not found")
    actual = p.resolve(strict=True)
    if not actual.is_relative_to(root):
        raise _reject("path escapes root")
    if actual.stat().st_size > MAX_FILE_BYTES:
        raise _reject("file too large")
    return actual


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path: Path):
    try:
        with Image.open(path) as raw:
            if raw.format not in ACCEPTED_FORMATS or getattr(raw, "n_frames", 1) != 1:
                raise _reject("unsupported or animated media")
            if raw.width * raw.height > MAX_PIXELS or min(raw.size) < 24:
                raise _reject("invalid or excessive intrinsic geometry")
            # EXIF orientation can change the visual orientation after decode.
            image = ImageOps.exif_transpose(raw)
            image.load()
            return image.convert("RGBA"), raw.format
    except (Image.DecompressionBombError, Image.DecompressionBombWarning, UnidentifiedImageError, OSError) as e:
        raise _reject("image decode failed or exceeded size limits") from e


def dhash(image: Image.Image) -> int:
    small = image.convert("RGB").convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    px = list(small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata())
    out = 0
    for y in range(8):
        for x in range(8):
            out = (out << 1) | int(px[y * 9 + x] > px[y * 9 + x + 1])
    return out


def greyscale_mae(a: Image.Image, b: Image.Image) -> float:
    # Diff after matching both to a canonical small canvas, not a pixel-identity check.
    x = a.convert("RGB").convert("L").resize((128, 128), Image.Resampling.LANCZOS)
    y = b.convert("RGB").convert("L").resize((128, 128), Image.Resampling.LANCZOS)
    hist = ImageChops.difference(x, y).histogram()
    return sum(v * n for v, n in enumerate(hist)) / (128 * 128)


def alpha_mae(a: Image.Image, b: Image.Image) -> float:
    x = a.getchannel("A").resize((64, 64), Image.Resampling.LANCZOS)
    y = b.getchannel("A").resize((64, 64), Image.Resampling.LANCZOS)
    hist = ImageChops.difference(x, y).histogram()
    return sum(v * n for v, n in enumerate(hist)) / (64 * 64)


def analyze(manifest: dict, root: Path) -> dict:
    """Compare two already-existing lawful local files. Always release-HOLD."""
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise _reject("wrong manifest schema")
    for k in ("image_key", "original_source_url", "candidate_catalog_url", "source_local_path", "candidate_local_path"):
        if not isinstance(manifest.get(k), str) or not manifest[k]:
            raise _reject("missing manifest field: " + k)
    if not KEY_PATTERN.fullmatch(manifest["image_key"]):
        raise _reject("image key invalid")
    if not URL_PATTERN.fullmatch(manifest["original_source_url"]) or not URL_PATTERN.fullmatch(manifest["candidate_catalog_url"]):
        raise _reject("HTTPS source/catalog URL required")
    if manifest.get("lawful_local_copies_attested") is not True:
        raise _reject("lawful copies must be expressly attested")
    if manifest.get("item_specific_rights_review") != "PASS":
        raise _reject("item-specific rights review must PASS for local processing")
    if manifest.get("source_relationship") not in ("same_catalog_item", "proposed_same_photo"):
        raise _reject("different-scene/subject alternatives cannot use identity gate")
    if manifest["source_local_path"] == manifest["candidate_local_path"]:
        raise _reject("source and derivative paths cannot be the same")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise _reject("root must be directory")
    src = safe_path(root, manifest["source_local_path"])
    out = safe_path(root, manifest["candidate_local_path"])
    src_image, src_fmt = _load(src)
    candidate, cand_fmt = _load(out)
    sw, sh = src_image.size
    cw, ch = candidate.size
    # Integer rounding at most 1 pixel to preserve framing and prevent stretching.
    expected_height = round(sh * cw / sw)
    geometry_pass = cw <= MAX_WIDTH and cw <= sw and ch <= sh and abs(ch - expected_height) <= 1
    hd = (dhash(src_image) ^ dhash(candidate)).bit_count()
    ma = greyscale_mae(src_image, candidate)
    aa = alpha_mae(src_image, candidate)
    visual_pass = geometry_pass and hd <= MAX_DHASH_DISTANCE and ma <= MAX_GREY_MAE and aa <= 1.0
    result = {
        "schema": SCHEMA,
        "image_key": manifest["image_key"],
        "original_source_url": manifest["original_source_url"],
        "candidate_catalog_url": manifest["candidate_catalog_url"],
        "source_relationship": manifest["source_relationship"],
        "source_sha256": _sha(src),
        "candidate_sha256": _sha(out),
        "source_dimensions": [sw, sh],
        "candidate_dimensions": [cw, ch],
        "source_format": src_fmt,
        "candidate_format": cand_fmt,
        "max_allowed_width": MAX_WIDTH,
        "geometry_pass": geometry_pass,
        "dhash_hamming_64": hd,
        "greyscale_mae_0_255": round(ma, 3),
        "alpha_mae_0_255": round(aa, 3),
        "comparison_result": "VISUAL_SIMILARITY_REVIEW" if visual_pass else "VISUAL_PARITY_FAILED",
        "exact_archival_identity_proven": False,
        "rights_to_publish_proven": False,
        "browser_image_status": None,
        "actual_network_transfer_bytes": None,
        "sitewide_savings_percent": None,
        "word_press_prod_write_authorized": False,
        "candidate_republication_authorized": False,
    }
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True, help="A JSON manifest for already-held local files")
    ap.add_argument("--root", required=True, help="Directory containing already lawful local copies")
    args = ap.parse_args(argv)
    try:
        root = Path(args.root)
        if root.is_symlink():
            raise _reject("symlink root forbidden")
        with Path(args.manifest).open("r", encoding="utf-8") as f:
            m = json.load(f)
        result = analyze(m, root)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"schema": SCHEMA, "comparison_result": "INPUT_REJECTED", "reason": str(e), "publication_authorized": False}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["comparison_result"] == "VISUAL_SIMILARITY_REVIEW" else 1


if __name__ == "__main__":
    sys.exit(main())
