#!/usr/bin/env python3
"""Measure what the browser actually transfers/decodes for the three archival images (CDP Network).

  python measure_images.py --url http://127.0.0.1:9400/ --out <dir>
Records per viewport (mobile 390@DPR3, tablet 768@2, desktop 1440@1, wide 1920@1): chosen currentSrc,
naturalWidth/Height, rendered CSS size, decode status, HTTP status, content-type and
transferred bytes (encodedDataLength) plus decoded body sha256 of each chosen file.
"""
import argparse, hashlib, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

CASES = {"apollo": "s67-19766", "franklin": "Franklinexpeditionnote", "malbone": "nypl-5003296"}
VPS = [("mobile-390@3x", 390, 844, 3), ("tablet-768@2x", 768, 1024, 2), ("desktop-1440@1x", 1440, 900, 1), ("wide-1920@1x", 1920, 1080, 1)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url", default="http://127.0.0.1:9400/"); ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    R = {}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        for name, w, h, dpr in VPS:
            ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr)
            pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg); cdp.send("Network.enable")
            reqs = {}
            cdp.on("Network.responseReceived", lambda e: reqs.setdefault(e["requestId"], {}).update(url=e["response"]["url"], status=e["response"]["status"], mime=e["response"]["mimeType"], type=e.get("type")))
            cdp.on("Network.loadingFinished", lambda e: reqs.setdefault(e["requestId"], {}).update(bytes=e["encodedDataLength"]))
            pg.goto(a.url, wait_until="load")
            for sel in ["[data-fv-records]"]:
                pg.locator(sel).scroll_into_view_if_needed()
            # exercise each case so the chosen image for every case is requested
            for c in CASES:
                pg.locator(f'[data-fv-case-button="{c}"]').scroll_into_view_if_needed(); pg.click(f'[data-fv-case-button="{c}"]'); pg.wait_for_timeout(900)
            pg.wait_for_timeout(1500)
            imgs = pg.evaluate("""()=>[...document.querySelectorAll('.fv-hf img')].map(i=>({src:i.currentSrc,alt:(i.alt||'').slice(0,90),nw:i.naturalWidth,nh:i.naturalHeight,cw:Math.round(i.getBoundingClientRect().width),ch:Math.round(i.getBoundingClientRect().height),complete:i.complete,loading:i.loading,fetchpriority:i.getAttribute('fetchpriority'),visible:i.getBoundingClientRect().width>0}))""")
            rows = []
            for i in imgs:
                key = next((k for k, s in CASES.items() if s in i["src"]), None)
                if not key: continue
                m = next((v for v in reqs.values() if v.get("url") == i["src"]), {})
                i.update(case=key, http=m.get("status"), mime=m.get("mime"), transfer_bytes=m.get("bytes"))
                rows.append(i)
            R[name] = rows
            ctx.close()
        b.close()
    # decoded body hashes of the chosen candidates
    import urllib.request, ssl
    seen = {}
    for rows in R.values():
        for r in rows:
            if r["src"] in seen: continue
            try:
                d = urllib.request.urlopen(urllib.request.Request(r["src"], headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
                seen[r["src"]] = {"sha256": hashlib.sha256(d).hexdigest(), "decoded_bytes": len(d), "magic": d[:12].hex()}
            except Exception as e:
                seen[r["src"]] = {"error": str(e)[:100]}
    R["_bodies"] = seen
    (a.out / "image_measurements.json").write_text(json.dumps(R, indent=2), encoding="utf-8")
    for name, rows in R.items():
        if name.startswith("_"): continue
        for r in rows: print(name, r["case"], r["nw"], "x", r["nh"], "css", r["cw"], "x", r["ch"], "http", r["http"], r["mime"], "xfer", r["transfer_bytes"], "visible", r["visible"], r["src"][-70:])


if __name__ == "__main__":
    main()
