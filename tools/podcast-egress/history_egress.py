#!/usr/bin/env python3
"""Deterministic ElevenLabs History egress for already-generated narration.

This bridge never calls synthesis endpoints. It lists Flow-origin History items,
matches each locked canonical stem by normalized text, downloads only existing
History audio, selects the exact approved take by measured duration when duplicate
text candidates exist, and emits one ZIP + machine-readable receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

HISTORY_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
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
    if not name.lower().endswith(".mp3"):
        raise EgressError(f"POD-001 History egress expects MP3 output: {name!r}")


def normalize_spoken_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text).casefold()
    tokens = re.findall(r"[^\W_]+", text, flags=re.UNICODE)
    return " ".join(tokens)


def validate_manifest(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise EgressError("manifest root must be an object")
    stems = data.get("stems")
    if not isinstance(stems, list) or not stems:
        raise EgressError("manifest stems must be a non-empty list")
    expected_count = data.get("expected_count")
    if expected_count is not None and expected_count != len(stems):
        raise EgressError(f"expected_count={expected_count} but found {len(stems)} stems")

    required_top = ["episode_id", "canonical_script_sha256", "voice_id", "model_id"]
    for key in required_top:
        if not isinstance(data.get(key), str) or not data[key]:
            raise EgressError(f"manifest missing {key}")

    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for i, stem in enumerate(stems, start=1):
        if not isinstance(stem, dict):
            raise EgressError(f"stem #{i} must be an object")
        stem_id = stem.get("stem_id")
        filename = stem.get("filename")
        text_hash = stem.get("normalized_text_sha256")
        if not isinstance(stem_id, str) or not STEM_ID_RE.fullmatch(stem_id):
            raise EgressError(f"invalid stem_id at #{i}: {stem_id!r}")
        if stem_id in seen_ids:
            raise EgressError(f"duplicate stem_id: {stem_id}")
        seen_ids.add(stem_id)
        if not isinstance(filename, str):
            raise EgressError(f"missing filename for {stem_id}")
        validate_filename(filename)
        if filename in seen_files:
            raise EgressError(f"duplicate filename: {filename}")
        seen_files.add(filename)
        if not isinstance(text_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", text_hash):
            raise EgressError(f"missing/invalid normalized_text_sha256 for {stem_id}")
        dur = stem.get("expected_duration_seconds")
        if dur is not None and (not isinstance(dur, (int, float)) or dur <= 0):
            raise EgressError(f"invalid expected duration for {stem_id}")
    return data


def api_request(url: str, api_key: str, accept: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "xi-api-key": api_key,
            "Accept": accept,
            "User-Agent": "FinalVestige-Podcast-Egress/2.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        raise EgressError(f"ElevenLabs API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise EgressError(f"ElevenLabs API request failed: {exc.reason}") from exc


def list_history(manifest: dict[str, Any], api_key: str, api_base: str) -> list[dict[str, Any]]:
    params = {
        "page_size": "1000",
        "source": manifest.get("history_source", "Flows"),
        "voice_id": manifest["voice_id"],
        "model_id": manifest["model_id"],
    }
    if manifest.get("history_date_after_unix") is not None:
        params["date_after_unix"] = str(int(manifest["history_date_after_unix"]))
    if manifest.get("history_date_before_unix") is not None:
        params["date_before_unix"] = str(int(manifest["history_date_before_unix"]))
    url = f"{api_base}/v1/history?" + urllib.parse.urlencode(params)
    try:
        payload = json.loads(api_request(url, api_key, "application/json"))
    except json.JSONDecodeError as exc:
        raise EgressError("History endpoint returned invalid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("history"), list):
        raise EgressError("History endpoint returned unexpected schema")
    if payload.get("has_more"):
        raise EgressError("History result is paginated; widen bridge pagination support before egress")
    items = [x for x in payload["history"] if isinstance(x, dict)]
    for item in items:
        normalized = normalize_spoken_text(item.get("text", ""))
        item["_normalized_text_sha256"] = hashlib.sha256(normalized.encode("utf-8")).hexdigest() if normalized else None
    return items


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


def download_history_audio(api_base: str, history_id: str, api_key: str, destination: Path) -> tuple[int, float, str]:
    if not HISTORY_ID_RE.fullmatch(history_id):
        raise EgressError(f"invalid History item ID: {history_id!r}")
    audio = api_request(
        f"{api_base}/v1/history/{urllib.parse.quote(history_id, safe='')}/audio",
        api_key,
        "audio/mpeg",
        timeout=120,
    )
    if len(audio) < 4096:
        raise EgressError(f"History audio {history_id} is implausibly small ({len(audio)} bytes)")
    destination.write_bytes(audio)
    duration = probe_duration(destination)
    digest = hashlib.sha256(audio).hexdigest()
    return len(audio), duration, digest


def choose_candidate(
    stem: dict[str, Any],
    matches: list[dict[str, Any]],
    api_base: str,
    api_key: str,
    temp_dir: Path,
    tolerance: float,
    ambiguity_margin: float,
) -> tuple[dict[str, Any], Path, int, float, str, list[dict[str, Any]]]:
    stem_id = stem["stem_id"]
    expected = stem.get("expected_duration_seconds")
    if not matches:
        raise EgressError(f"{stem_id}: no History item matches locked canonical text")

    measured: list[tuple[dict[str, Any], Path, int, float, str]] = []
    for n, item in enumerate(matches, start=1):
        history_id = item.get("history_item_id")
        if not isinstance(history_id, str):
            raise EgressError(f"{stem_id}: matching History row lacks history_item_id")
        candidate_path = temp_dir / f"{stem_id}-candidate-{n:02d}.mp3"
        byte_count, duration, digest = download_history_audio(api_base, history_id, api_key, candidate_path)
        measured.append((item, candidate_path, byte_count, duration, digest))

    if expected is None:
        if len(measured) != 1:
            detail = [f"{x[0].get('history_item_id')}:{x[3]:.3f}s" for x in measured]
            raise EgressError(f"{stem_id}: {len(measured)} lexical matches and no locked duration; ambiguous {detail}")
        selected = measured[0]
    else:
        ranked = sorted(measured, key=lambda x: abs(x[3] - float(expected)))
        best = ranked[0]
        best_delta = abs(best[3] - float(expected))
        if best_delta > tolerance:
            detail = [f"{x[0].get('history_item_id')}:{x[3]:.3f}s" for x in ranked[:5]]
            raise EgressError(
                f"{stem_id}: nearest History take is {best_delta:.3f}s from locked duration {expected:.3f}s; {detail}"
            )
        if len(ranked) > 1:
            second_delta = abs(ranked[1][3] - float(expected))
            if second_delta - best_delta < ambiguity_margin:
                detail = [f"{x[0].get('history_item_id')}:{x[3]:.3f}s" for x in ranked[:5]]
                raise EgressError(f"{stem_id}: duration match is ambiguous; {detail}")
        selected = best

    candidates_receipt = [
        {
            "history_item_id": x[0].get("history_item_id"),
            "date_unix": x[0].get("date_unix"),
            "duration_seconds": round(x[3], 3),
            "sha256": x[4],
            "selected": x is selected,
        }
        for x in measured
    ]
    return (*selected, candidates_receipt)


def run(manifest_path: Path, out_dir: Path, zip_path: Path, receipt_path: Path, api_key: str) -> None:
    manifest = validate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
    api_base = os.environ.get("ELEVENLABS_API_BASE", "https://api.elevenlabs.io").rstrip("/")
    if not api_base.startswith("https://"):
        raise EgressError("ELEVENLABS_API_BASE must use https")

    history = list_history(manifest, api_key, api_base)
    print(f"History candidate window: {len(history)} items", flush=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    tolerance = float(manifest.get("duration_tolerance_seconds", 0.80))
    ambiguity_margin = float(manifest.get("duration_ambiguity_margin_seconds", 0.20))
    receipts: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="fv-pod001-history-") as tmp:
        tmp_dir = Path(tmp)
        for stem in manifest["stems"]:
            stem_id = stem["stem_id"]
            text_hash = stem["normalized_text_sha256"]
            matches = [x for x in history if x.get("_normalized_text_sha256") == text_hash]
            item, source_path, byte_count, duration, digest, candidates = choose_candidate(
                stem, matches, api_base, api_key, tmp_dir, tolerance, ambiguity_margin
            )
            target = out_dir / stem["filename"]
            shutil.copyfile(source_path, target)
            history_id = item.get("history_item_id")
            receipts.append(
                {
                    "stem_id": stem_id,
                    "filename": stem["filename"],
                    "history_item_id": history_id,
                    "legacy_generation_id": stem.get("legacy_generation_id"),
                    "source_session_id": stem.get("source_session_id"),
                    "retake": bool(stem.get("retake", False)),
                    "bytes": byte_count,
                    "sha256": digest,
                    "duration_seconds": round(duration, 3),
                    "locked_duration_seconds": stem.get("expected_duration_seconds"),
                    "lexical_match_count": len(matches),
                    "candidate_measurements": candidates,
                }
            )
            print(
                f"verified {stem_id}: history={history_id} lexical_matches={len(matches)} "
                f"bytes={byte_count} duration={duration:.3f}s",
                flush=True,
            )

    expected_count = int(manifest.get("expected_count", len(receipts)))
    if len(receipts) != expected_count:
        raise EgressError(f"expected {expected_count} selected stems, got {len(receipts)}")
    names = [x["filename"] for x in receipts]
    if len(set(names)) != expected_count:
        raise EgressError("selected output filenames are not unique")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for entry in receipts:
            zf.write(out_dir / entry["filename"], arcname=entry["filename"])

    receipt = {
        "schema_version": "2.0",
        "episode_id": manifest["episode_id"],
        "canonical_script_sha256": manifest["canonical_script_sha256"],
        "elevenlabs_flow_id": manifest.get("elevenlabs_flow_id"),
        "voice_id": manifest["voice_id"],
        "model_id": manifest["model_id"],
        "history_source": manifest.get("history_source", "Flows"),
        "history_candidate_count": len(history),
        "retrieved_at_unix": int(time.time()),
        "selected_stem_count": len(receipts),
        "zip_filename": zip_path.name,
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256_file(zip_path),
        "stems": receipts,
        "security": {
            "api_key_logged": False,
            "signed_content_urls_persisted": False,
            "synthesis_endpoint_called": False,
            "provider_mutation_performed": False,
        },
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"complete: {len(receipts)} selected stems -> {zip_path.name} sha256={receipt['zip_sha256']}", flush=True)


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
