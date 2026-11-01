#!/usr/bin/env python3
"""Measure text contrast over the hero photograph, which axe-core reports as 'incomplete' (it cannot sample images).

For every text element in the hero, the text is made transparent, the pixels behind it are screenshotted (REAL NASA image,
network required), and the WCAG ratio is computed against the 99th-percentile lightest background pixel (worst case for
light text). Thresholds: 4.5:1, or 3:1 for large text (>= 24 px, or >= 18.66 px bold).
"""
from __future__ import annotations

import io
import json
import sys

from playwright.sync_api import sync_playwright

import fvx_lib as lib
from browser import launch, serve

SELECTORS = ".fv-ex2-hero .fv-ex2-label, .fv-ex2-hero__title, .fv-ex2-hero__dek, .fv-ex2-hero__meta dt, .fv-ex2-hero__meta dd, .fv-ex2-hero__credit"


def lum(rgb) -> float:
    lin = [(c / 255) / 12.92 if c / 255 <= 0.03928 else (((c / 255) + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def main() -> int:
    from PIL import Image
    rows, failures = [], []
    with serve(lib.EX2 / "dist") as base, sync_playwright() as pw:
        browser = launch(pw)
        for w, h in [(360, 780), (390, 844), (768, 1024), (1440, 900), (1920, 1080)]:
            page = browser.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce")
            page.goto(f"{base}/apollo-1/index.html", wait_until="load")
            page.wait_for_function("document.querySelector('.fv-ex2-hero__media img').complete && document.querySelector('.fv-ex2-hero__media img').naturalWidth > 0")
            page.wait_for_timeout(600)
            info = page.evaluate("""(sel) => [...document.querySelectorAll(sel)].map(e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
                return {text: e.textContent.trim().slice(0, 28), x: r.x, y: r.y + scrollY, w: r.width, h: r.height, color: cs.color, size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight)}; })""", SELECTORS)
            page.add_style_tag(content=".fv-ex2-hero__inner *{color:transparent!important;border-color:transparent!important}.fv-ex2-hero__actions{visibility:hidden}.fv-ex2-masthead{visibility:hidden}")
            page.wait_for_timeout(200)
            for item in info:
                if item["w"] < 2 or item["h"] < 2:
                    continue
                shot = page.screenshot(clip={"x": max(0, item["x"]), "y": item["y"], "width": min(item["w"], w - max(0, item["x"])), "height": item["h"]}, full_page=True)
                img = Image.open(io.BytesIO(shot)).convert("RGB")
                pixels = img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()
                lums = sorted(lum(px) for px in pixels)
                bg = lums[int(len(lums) * 0.99) - 1]
                m = [int(v) for v in item["color"].replace("rgba(", "").replace("rgb(", "").replace(")", "").split(",")[:3]]
                ratio = (lum(m) + 0.05) / (bg + 0.05)
                large = item["size"] >= 24 or (item["size"] >= 18.66 and item["weight"] >= 700)
                need = 3.0 if large else 4.5
                ok = ratio >= need
                rows.append({"width": w, "text": item["text"], "ratio": round(ratio, 2), "need": need, "ok": ok})
                if not ok:
                    failures.append(f"{w}px '{item['text']}': {ratio:.2f}:1 < {need}:1")
            page.close()
        browser.close()
    (lib.EX2 / "dist" / "hero-contrast.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    worst = min(rows, key=lambda r: r["ratio"] - r["need"])
    if failures:
        print(f"FAIL: {len(failures)} hero text region(s) below threshold", *failures, sep="\n  ")
        return 1
    print(f"OK: {len(rows)} hero text regions measured over the real photograph; tightest margin {worst['ratio']}:1 (needs {worst['need']}:1) at {worst['width']}px '{worst['text']}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
