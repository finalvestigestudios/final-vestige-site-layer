#!/usr/bin/env python3
"""Verify every image and record URL in data/apollo1.json against the live hosts.

Checks: HTTP 200, an image content type, decoded dimensions equal the declared ones, and each NASA record page still
resolves. Needs the network. Failure to reach a host is a FAILURE, never a pass.
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.error
import urllib.request

import fvx_lib as lib

UA = {"User-Agent": "FinalVestige-media-verify/0.1 (read-only)"}


def fetch(url: str, attempts: int = 3) -> tuple[int, str, bytes]:
    for n in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and n < attempts:
                time.sleep(min(int(exc.headers.get("Retry-After", "10") or 10), 60))
                continue
            return exc.code, "", b""
        except Exception as exc:  # noqa: BLE001
            if n == attempts:
                return 0, str(exc), b""
            time.sleep(3)
    return 0, "", b""


def main() -> int:
    from PIL import Image
    data = lib.load_apollo1()
    failures, rows = [], []
    for rec in data["records"]:
        img = rec["image"]
        targets = [(img["src"], img["width"], img["height"])]
        for v in img["variants"]:
            targets.append((v["url"], v["w"], round(v["w"] * img["height"] / img["width"])))
        for url, w, h in targets:
            status, ctype, body = fetch(url)
            ok = status == 200 and ctype.startswith("image/")
            dims = None
            if ok:
                dims = Image.open(io.BytesIO(body)).size
                tol = 1 if url == img["src"] else 2
                ok = abs(dims[0] - w) <= tol and abs(dims[1] - h) <= tol
            rows.append({"url": url, "status": status, "type": ctype, "declared": [w, h], "actual": list(dims) if dims else None, "ok": ok})
            if not ok:
                failures.append(f"{url}: status={status} type={ctype} declared={w}x{h} actual={dims}")
        status, _, _ = fetch(img["record_url"])
        rows.append({"url": img["record_url"], "status": status, "ok": status == 200})
        if status != 200:
            failures.append(f"record page {img['record_url']} returned {status}")
        # The image library API is the authority on whether an asset id exists. The Final Vestige-hosted copy
        # (S67-19766) is a known exception recorded in its identity_note.
        if "images-assets.nasa.gov" in img["src"]:
            st, _, body = fetch("https://images-api.nasa.gov/search?nasa_id=" + img["nasa_id"])
            items = json.loads(body)["collection"]["items"] if st == 200 and body else []
            ok = bool(items) and items[0]["data"][0]["nasa_id"] == img["nasa_id"]
            rows.append({"api_nasa_id": img["nasa_id"], "status": st, "ok": ok})
            if not ok:
                failures.append(f"NASA Image API has no asset {img['nasa_id']} (status {st})")
    status, _, _ = fetch(data["primary_report"]["url"])
    rows.append({"url": data["primary_report"]["url"], "status": status, "ok": status == 200})
    if status != 200:
        failures.append(f"Board report page returned {status}")
    out = lib.EX2 / "dist" / "media-results.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    if failures:
        print(f"FAIL: {len(failures)} problem(s)", *failures, sep="\n  ")
        return 1
    print(f"OK: {len(rows)} URLs verified (images decoded at declared dimensions; record pages and Board report resolve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
