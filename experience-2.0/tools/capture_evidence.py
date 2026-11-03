#!/usr/bin/env python3
"""Capture real-browser screenshots at 360, 390, 768, 1024, 1440 and 1920 px using the REAL NASA images (network).

Output: experience-2.0/dist/evidence/ (gitignored: screenshots are generated evidence, not source). A manifest records, per
capture, whether every image actually loaded, so a blocked-media environment is visible instead of silently pretty.
"""
from __future__ import annotations

import json
import sys

from playwright.sync_api import sync_playwright

import fvx_lib as lib
from browser import launch, serve

WIDTHS = [(360, 780), (390, 844), (768, 1024), (1024, 800), (1440, 900), (1920, 1080)]
PAGES = {"flagship": "apollo-1/index.html", "research-desk": "research-desk/index.html", "atlas": "atlas/index.html", "design-system": "design-system/index.html"}


def main() -> int:
    out = lib.EX2 / "dist" / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    with serve(lib.EX2 / "dist") as base, sync_playwright() as pw:
        browser = launch(pw)
        for name, path in PAGES.items():
            for w, h in WIDTHS:
                page = browser.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce")
                page.goto(f"{base}/{path}", wait_until="load")
                height = page.evaluate("document.documentElement.scrollHeight")
                for y in range(0, height, 600):  # trigger lazy images
                    page.evaluate(f"window.scrollTo(0,{y})")
                    page.wait_for_timeout(120)
                page.wait_for_timeout(1500)
                page.evaluate("window.scrollTo(0,0)")
                stats = page.evaluate("({images: document.images.length, loaded: [...document.images].filter(i => i.complete && i.naturalWidth > 0).length, overflow: document.documentElement.scrollWidth - innerWidth})")
                page.screenshot(path=str(out / f"{name}-{w}-top.png"))
                if name in ("flagship", "research-desk", "design-system"):
                    page.screenshot(path=str(out / f"{name}-{w}-full.png"), full_page=True)
                if name == "flagship":
                    page.evaluate("document.getElementById('record-03').scrollIntoView()")
                    page.wait_for_timeout(400)
                    page.screenshot(path=str(out / f"{name}-{w}-chapter3.png"))
                    opener = page.locator('[data-fvx-open-source="record-04"]')
                    opener.scroll_into_view_if_needed()
                    opener.click()
                    page.wait_for_timeout(700)
                    page.screenshot(path=str(out / f"{name}-{w}-drawer.png"))
                manifest.append({"page": name, "width": w, **stats})
                page.close()
        browser.close()
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    bad = [m for m in manifest if m["loaded"] != m["images"] or m["overflow"] > 0]
    for m in manifest:
        print(f"{m['page']:14s} {m['width']:5d}px images {m['loaded']}/{m['images']} overflow={m['overflow']}")
    if bad:
        print("FAIL: some captures had unloaded images or overflow", file=sys.stderr)
        return 1
    print(f"OK: {len(manifest)} captures, all images loaded, no overflow -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
