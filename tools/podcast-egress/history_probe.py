#!/usr/bin/env python3
"""Read-only ElevenLabs History API capability probe for POD-001.

Prints only non-secret identity metadata and verifies one known POD-001 history
audio item can be downloaded. It never calls synthesis/mutation endpoints and
never prints signed media URLs or API keys.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.elevenlabs.io"
S01_HISTORY_ID = "8rkYdrWhkE70ERacgBI3"


def request(url: str, key: str, accept: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "xi-api-key": key,
            "Accept": accept,
            "User-Agent": "FinalVestige-Podcast-Egress/1.0",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        print("ERROR: ELEVENLABS_API_KEY missing")
        return 2

    params = {
        "page_size": "1000",
        "source": "Flows",
        "voice_id": "G39kes5C0SCb5IRyUk73",
        "model_id": "eleven_multilingual_v2",
        "date_after_unix": "1789257600",
        "date_before_unix": "1789516799",
    }
    url = f"{API}/v1/history?" + urllib.parse.urlencode(params)
    try:
        payload = json.loads(request(url, key, "application/json"))
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        print(f"HISTORY_HTTP_ERROR {exc.code}: {body}")
        return 1
    except Exception as exc:
        print(f"HISTORY_ERROR: {type(exc).__name__}: {exc}")
        return 1

    items = payload.get("history", []) if isinstance(payload, dict) else []
    print(f"HISTORY_OK count={len(items)} has_more={payload.get('has_more') if isinstance(payload, dict) else None}")

    # Verify the known S01 candidate is present and its text identity is correct.
    item = next((x for x in items if x.get("history_item_id") == S01_HISTORY_ID), None)
    if not item:
        print("ERROR: known S01 History item missing")
        return 1
    preview = " ".join(str(item.get("text", "")).split())[:96]
    print(f"S01_HISTORY_PRESENT id={S01_HISTORY_ID} preview={preview!r}")

    # Test the standard History audio endpoint on the current plan/key.
    try:
        audio = request(f"{API}/v1/history/{S01_HISTORY_ID}/audio", key, "audio/mpeg")
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        print(f"AUDIO_HTTP_ERROR {exc.code}: {body}")
        return 1
    if len(audio) < 1024:
        print(f"ERROR: S01 audio response unexpectedly small ({len(audio)} bytes)")
        return 1

    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        f.write(audio)
        f.flush()
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", f.name],
            text=True,
            capture_output=True,
            check=True,
        )
        duration = float(proc.stdout.strip())
    digest = hashlib.sha256(audio).hexdigest()
    print(f"S01_AUDIO_OK bytes={len(audio)} duration={duration:.3f}s sha256={digest}")
    if abs(duration - 36.46) > 0.75:
        print("ERROR: S01 duration does not match locked selected-source evidence")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
