#!/usr/bin/env python3
"""Deterministic ElevenLabs Flow-generation binary egress.

Fetches exact, already-generated ElevenLabs Flow TTS generations by immutable
`generation_id`, downloads their current signed media URLs, validates the files,
and emits a ZIP + receipt. It never calls a synthesis endpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

GENERATION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
STEM_ID_RE = re.compile(r"^[A-Z0-9_-]{1,32}$")


class EgressError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_filename(name: str) -> None:
    if not name or Path(name).name != name or name in {".", ".."}:
        raise EgressError(f"unsafe filename: {name!r}")
    if not name.lower().endswith((".mp3", ".wav", ".m4a", ".flac")):
        raise EgressError(f"unsupported audio filename: {name!r}")


def validate_manifest(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise EgressError("manifest root must be an object")
    stems = data.get("stems")
    if not isinstance(stems, list) or not stems:
        raise EgressError("manifest stems must be a non-empty list")
    expected_count = data.get("expected_count")
    if expected_count is not None and expected_count != len(stems):
        raise EgressError(f"expected_count={expected_count} but found {len(stems)} stems")

    seen_stems: set[str] = set()
    seen_files: set[str] = set()
    seen_generations: set[str] = set()
    for i, stem in enumerate(stems, start=1):
        if not isinstance(stem, dict):
            raise EgressError(f"stem #{i} must be an object")
        stem_id = stem.get("stem_id")
        filename = stem.get("filename")
        generation_id = stem.get("generation_id")
        if not isinstance(stem_id, str) or not STEM_ID_RE.fullmatch(stem_id):
            raise EgressError(f"invalid stem_id at #{i}: {stem_id!r}")
        if not isinstance(filename, str):
            raise EgressError(f"missing filename for {stem_id}")
        validate_filename(filename)
        if not isinstance(generation_id, str) or not GENERATION_ID_RE.fullmatch(generation_id):
            raise EgressError(f"invalid generation_id for {stem_id}")
        if stem_id in seen_stems:
            raise EgressError(f"duplicate stem_id: {stem_id}")
        if filename in seen_files:
            raise EgressError(f"duplicate filename: {filename}")
        if generation_id in seen_generations:
            raise EgressError(f"duplicate generation_id: {generation_id}")
        seen_stems.add(stem_id)
        seen_files.add(filename)
        seen_generations.add(generation_id)

        dur = stem.get("expected_duration_seconds")
        if dur is not None and (not isinstance(dur, (int, float)) or dur <= 0):
            raise EgressError(f"invalid expected duration for {stem_id}")

    return data


def is_safe_https_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)


def request_json(url: str, api_key: str, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "xi-api-key": api_key,
            "Accept": "application/json",
            "User-Agent": "FinalVestige-Podcast-Egress/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read(1024).decode("utf-8", errors="replace")
        raise EgressError(f"ElevenLabs generation lookup failed HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise EgressError(f"ElevenLabs generation lookup failed: {exc.reason}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EgressError("ElevenLabs generation lookup returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise EgressError("ElevenLabs generation lookup returned non-object JSON")
    return value


def parse_completed_generation(payload: dict[str, Any], expected_generation_id: str) -> tuple[str, str]:
    if payload.get("id") != expected_generation_id:
        raise EgressError(
            f"generation identity mismatch: expected {expected_generation_id}, got {payload.get('id')!r}"
        )
    if payload.get("status") != "completed":
        raise EgressError(f"generation {expected_generation_id} is not completed: {payload.get('status')!r}")
    mime = payload.get("content_mime_type")
    if not isinstance(mime, str) or not mime.startswith("audio/"):
        raise EgressError(f"generation {expected_generation_id} did not return audio content: {mime!r}")
    content_url = payload.get("content_url")
    if not isinstance(content_url, str) or not is_safe_https_url(content_url):
        raise EgressError(f"generation {expected_generation_id} returned an unsafe/missing content URL")
    return content_url, mime


def download_binary(url: str, destination: Path, timeout: int = 120) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "FinalVestige-Podcast-Egress/1.0"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, destination.open("wb") as out:
            total = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                total += len(chunk)
    except urllib.error.HTTPError as exc:
        destination.unlink(missing_ok=True)
        raise EgressError(f"signed media download failed HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        destination.unlink(missing_ok=True)
        raise EgressError(f"signed media download failed: {exc.reason}") from exc
    if total < 4096:
        destination.unlink(missing_ok=True)
        raise EgressError(f"downloaded media is implausibly small ({total} bytes)")
    return total


def probe_duration(path: Path) -> float:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise EgressError("ffprobe is required for duration verification")
    proc = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise EgressError(f"ffprobe failed for {path.name}: {proc.stderr.strip()}")
    try:
        return float(proc.stdout.strip())
    except ValueError as exc:
        raise EgressError(f"ffprobe returned invalid duration for {path.name}") from exc


def run(manifest_path: Path, out_dir: Path, zip_path: Path, receipt_path: Path, api_key: str) -> None:
    manifest = validate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
    api_base = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io").rstrip("/")
    if not is_safe_https_url(api_base):
        raise EgressError("ELEVENLABS_API_BASE must be a safe https URL")

    out_dir.mkdir(parents=True, exist_ok=True)
    receipt_entries: list[dict[str, Any]] = []
    tolerance = float(manifest.get("duration_tolerance_seconds", 1.25))

    for stem in manifest["stems"]:
        stem_id = stem["stem_id"]
        generation_id = stem["generation_id"]
        filename = stem["filename"]
        lookup_url = f"{api_base}/v1/flows/text-to-speech/{urllib.parse.quote(generation_id, safe='')}"
        payload = request_json(lookup_url, api_key)
        content_url, mime = parse_completed_generation(payload, generation_id)

        target = out_dir / filename
        byte_count = download_binary(content_url, target)
        duration = probe_duration(target)
        expected_duration = stem.get("expected_duration_seconds")
        if expected_duration is not None and abs(duration - float(expected_duration)) > tolerance:
            target.unlink(missing_ok=True)
            raise EgressError(
                f"{stem_id} duration mismatch: expected ~{expected_duration:.2f}s, observed {duration:.2f}s"
            )

        receipt_entries.append(
            {
                "stem_id": stem_id,
                "filename": filename,
                "generation_id": generation_id,
                "source_session_id": stem.get("source_session_id"),
                "retake": bool(stem.get("retake", False)),
                "mime_type": mime,
                "bytes": byte_count,
                "sha256": sha256_file(target),
                "duration_seconds": round(duration, 3),
            }
        )
        print(f"verified {stem_id}: {filename} {byte_count} bytes {duration:.2f}s", flush=True)

    if len(receipt_entries) != int(manifest.get("expected_count", len(receipt_entries))):
        raise EgressError("not all expected stems were retrieved")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for entry in receipt_entries:
            zf.write(out_dir / entry["filename"], arcname=entry["filename"])

    receipt = {
        "schema_version": "1.0",
        "episode_id": manifest.get("episode_id"),
        "canonical_script_sha256": manifest.get("canonical_script_sha256"),
        "elevenlabs_flow_id": manifest.get("elevenlabs_flow_id"),
        "voice_id": manifest.get("voice_id"),
        "model_id": manifest.get("model_id"),
        "retrieved_at_unix": int(time.time()),
        "selected_stem_count": len(receipt_entries),
        "zip_filename": zip_path.name,
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256_file(zip_path),
        "stems": receipt_entries,
        "security": {
            "api_key_logged": False,
            "signed_content_urls_persisted": False,
            "synthesis_endpoint_called": False,
        },
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"complete: {len(receipt_entries)} stems -> {zip_path} sha256={receipt['zip_sha256']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--zip", dest="zip_path", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY is not set", file=sys.stderr)
        return 2
    try:
        run(args.manifest, args.out_dir, args.zip_path, args.receipt, api_key)
    except (EgressError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
