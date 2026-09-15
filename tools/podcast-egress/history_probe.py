#!/usr/bin/env python3
"""Read-only ElevenLabs History API capability probe for POD-001.

Prints only non-secret identity metadata and text hashes/previews. It never calls
synthesis or mutation endpoints and never prints signed media URLs or API keys.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request


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
        # Sep 13 2026 00:00:00 UTC through Sep 15 2026 23:59:59 UTC.
        "date_after_unix": "1789257600",
        "date_before_unix": "1789516799",
    }
    url = "https://api.elevenlabs.io/v1/history?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "xi-api-key": key,
            "Accept": "application/json",
            "User-Agent": "FinalVestige-Podcast-Egress/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        print(f"HTTP_ERROR {exc.code}: {body}")
        return 1
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        return 1

    items = payload.get("history", []) if isinstance(payload, dict) else []
    print(f"HISTORY_OK count={len(items)} has_more={payload.get('has_more') if isinstance(payload, dict) else None}")
    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        text = item.get("text") if isinstance(item.get("text"), str) else ""
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
        preview = " ".join(text.split())[:72]
        safe = {
            "n": i,
            "history_item_id": item.get("history_item_id"),
            "request_id": item.get("request_id"),
            "date_unix": item.get("date_unix"),
            "voice_id": item.get("voice_id"),
            "model_id": item.get("model_id"),
            "source": item.get("source"),
            "content_type": item.get("content_type"),
            "text_sha256": text_hash,
            "text_preview": preview,
        }
        print(json.dumps(safe, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
