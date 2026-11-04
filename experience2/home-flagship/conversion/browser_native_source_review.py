#!/usr/bin/env python3
"""Offline full-source seven-chapter observer-exit Chromium review.

Unlike the earlier standalone snippet, this reads the ACTUAL checked-out
index.html + six CSS source files, while explicitly BLOCKING all network.
It is NOT saved WordPress/Assembler, axe, Jetpack, a live signup or field CWV.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HOME = HERE.parent
CSS = ("flagship.css", "chronicle.css", "chronicle-lens.css",
       "inquiry.css", "observer-lab.css", "reading-trail.css")
FOCUS = "https://finalvestige.com/focus/"
WIDTHS = (320, 390, 768, 1440, 1920)


def source_html():
    raw = (HOME / "index.html").read_text(encoding="utf-8")
    for name in CSS:
        tag = '<link rel="stylesheet" href="./' + name + '">'
        if raw.count(tag) != 1:
            raise ValueError("Unexpected source stylesheet reference " + name)
        style = (HOME / name).read_text(encoding="utf-8")
        if "</style" in style.lower():
            raise ValueError("Unsafe stylesheet close tag in " + name)
        raw = raw.replace(tag, '<style data-fv-offline-css="' + name + '">' +
                          style + '</style>', 1)
    # These scripts require hosted context; keep full static meaning and
    # explicitly omit enhancement *from offline diagnostic copy only*.
    raw, number = re.subn(
        r'<script src="\\./[^"]+\\.js" defer></script>', "", raw)
    if number != 4:
        raise ValueError("Expected 4 enhancements; source changed")
    if raw.count('data-fv-destination="focus"') != 1:
        raise ValueError("Native source conversion marker absent/duplicated")
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(HERE / "native-browser-evidence"))
    args = parser.parse_args()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    html = source_html()
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, executable_path="/usr/bin/chromium",
            args=["--no-sandbox"])
        for width in WIDTHS:
            page = browser.new_page(
                viewport={"width": width, "height": 900},
                java_script_enabled=False, reduced_motion="reduce")
            # No production calls, media, marketing, tracking or merchant opens.
            page.route("**/*", lambda route: route.abort())
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.set_content(html, wait_until="domcontentloaded")
            exit_box = page.locator('[data-fv-observer-exit]')
            cta = page.locator('a[data-fv-destination="focus"]')
            assert exit_box.count() == cta.count() == 1
            cta.scroll_into_view_if_needed()
            box = cta.bounding_box()
            observed = page.evaluate("""() => ({
              scrollWidth:document.documentElement.scrollWidth,
              viewport:window.innerWidth,
              chapterLinks:document.querySelectorAll('.fv-hf__chapter-nav a').length,
              evidenceLinks:document.querySelectorAll('.fv-hf__observer-context a').length,
              focusLinks:document.querySelectorAll('a[href="https://finalvestige.com/focus/"]').length
            })""")
            assert observed["scrollWidth"] <= observed["viewport"] + 1, (width, observed)
            assert box and box["width"] >= 44 and box["height"] >= 44, (width, box)
            assert cta.get_attribute("href") == FOCUS
            assert observed["chapterLinks"] == 7
            assert observed["evidenceLinks"] >= 2
            assert not errors
            cta.focus()
            page.keyboard.press("Tab")
            next_link = page.evaluate(
                "document.activeElement?.getAttribute('href')")
            assert next_link == (
                "https://finalvestige.com/free-resources/"
                "puysegurs-animal-magnetism-files/"), (width, next_link)
            # Ensure disclosure remains readable after the no-JS reveal.
            details = page.locator("#fv-hf-observer-answer")
            details.locator("summary").click()
            assert details.get_attribute("open") is not None
            file = output / f"observer-native-{width}.png"
            exit_box.screenshot(path=str(file), animations="disabled")
            results.append({"width": width, "cta_px": {
                "width": round(box["width"], 1),
                "height": round(box["height"], 1)},
                "horizontal_overflow": False, "source_links": observed["evidenceLinks"],
                "keyboard_next_historical_link": True,
                "details_no_js": True, "screenshot": file.name})
            page.close()
        browser.close()
    receipt = {
        "scope": "REAL SOURCE HTML + SIX CSS; OFFLINE NO-JS ONLY",
        "wordpress": "NOT_TESTED", "assembler": "NOT_TESTED",
        "axe": "NOT_RUN", "lighthouse": "NOT_RUN",
        "physical_zoom": "NOT_RUN", "media": "BLOCKED_BY_DESIGN",
        "signups": "NOT_TESTED", "paid_orders": "UNKNOWN",
        "widths": results, "release": "HOLD"}
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
