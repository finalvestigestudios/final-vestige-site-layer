#!/usr/bin/env python3
"""Read-only guest browser admission for LIVE Final Vestige opt-in paths.
No credentials, email entry, form submission, CMS writes, or performance claims.
A local fixture can be used only for harness QA; it can NEVER pass hosted release.
"""
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

ROUTES = ("/", "/focus/", "/dispatch/")
WIDTHS = (320, 360, 390, 768, 1440, 1920)

async def examine(page, path, width, js, motion, out):
    url = out["origin"] + path
    blocked_writes = []
    async def fence(route):
        method = route.request.method.upper()
        if method not in ("GET", "HEAD", "OPTIONS"):
            blocked_writes.append({"method": method, "resource_type": route.request.resource_type})
            await route.abort()
        else:
            await route.continue_()
    await page.route("**/*", fence)
    entry = {"path": path, "width": width, "javascript": js, "reduced_motion": motion,
             "http_status": None, "browser_form_visible": False, "email_fields_visible": 0,
             "fallback_self_links": 0, "horizontal_overflow": None, "screen": None,
             "blocked_nonread_requests": [], "status": "BLOCKED"}
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=14000)
        await page.wait_for_timeout(900 if js else 150)
        if urlparse(page.url).netloc != urlparse(out["origin"]).netloc:
            raise RuntimeError("CROSS_ORIGIN_REDIRECT")
        entry["http_status"] = response.status if response else None
        if entry["http_status"] != 200:
            raise RuntimeError("NON_200_HTTP_RESPONSE")
        entry["fallback_self_links"] = await page.locator(
            '.wp-block-jetpack-subscriptions a[href*="post_type=page"]').count()
        visible = 0
        for frame in page.frames:
            try:
                locator = frame.locator('.wp-block-jetpack-subscriptions input[type="email"]')
                for idx in range(min(await locator.count(), 10)):
                    if await locator.nth(idx).is_visible(): visible += 1
            except Exception:
                pass
        entry["email_fields_visible"] = visible
        entry["browser_form_visible"] = visible > 0
        entry["horizontal_overflow"] = await page.evaluate(
            "document.documentElement.scrollWidth > window.innerWidth + 2")
        entry["focus_links"] = await page.locator('a[href="/focus/"], a[href="https://finalvestige.com/focus/"]').count()
        if path == "/":
            entry["chapter_links"] = await page.locator('nav.fv-hf__chapter-nav a[href^="#"]').count()
            entry["margin_records"] = await page.locator('.fv-margin-strip__item').count()
        if path == "/focus/":
            entry["gift_hidden"] = await page.locator("#fvf-gift").evaluate(
                "(el) => el.hidden") if await page.locator("#fvf-gift").count() else None
        name = ("home" if path == "/" else path.strip("/")) + "_" + str(width) + ("_nojs" if not js else "") + ("_reduced" if motion else "") + ".png"
        await page.screenshot(path=str(Path(out["screenshots"]) / name), full_page=False)
        entry["screen"] = name
        if path == "/" and (entry.get("chapter_links") != 7 or entry.get("margin_records") != 72):
            raise RuntimeError("HOMEPAGE_SEVEN_CHAPTER_OR_MARGINS_DRIFT")
        if entry["horizontal_overflow"]:
            raise RuntimeError("HORIZONTAL_OVERFLOW")
        if js and not entry["browser_form_visible"]:
            raise RuntimeError("NO_VISIBLE_EMAIL_INPUT_IN_GUEST_BROWSER")
        entry["status"] = "OBSERVED_IN_BROWSER"
    except Exception as e:
        entry["reason"] = str(e)[:250]
    entry["blocked_nonread_requests"] = blocked_writes
    return entry

async def run(args):
    origin = "http://127.0.0.1:8765" if args.offline_fixture else "https://finalvestige.com"
    root = Path(args.out).resolve()
    root.mkdir(parents=True, exist_ok=True)
    shots = root / "screenshots"
    shots.mkdir(exist_ok=True)
    report = {"origin": origin, "mode": "OFFLINE_FIXTURE_NOT_RELEASE_EVIDENCE" if args.offline_fixture else "LIVE_READ_ONLY_BROWSER",
              "captured_utc": datetime.now(timezone.utc).isoformat(), "screenshots": str(shots),
              "results": [], "axe_wcag22aa": "UNVERIFIED", "field_cwv": "UNMEASURED",
              "forms_submitted": 0, "subscriptions_created": 0, "paid_orders_verified": 0}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=args.chromium,
                                          args=["--no-sandbox"])
        try:
            for width in WIDTHS:
                for path in ROUTES:
                    context = await browser.new_context(viewport={"width": width, "height": 900},
                                      reduced_motion="reduce" if width == 390 else "no-preference")
                    page = await context.new_page()
                    report["results"].append(await examine(page,path,width,True,width == 390,report | {"origin":origin}))
                    await context.close()
            # No JavaScript accessibility of meaning; do not assert Jetpack works without JS.
            context = await browser.new_context(viewport={"width":390,"height":900},java_script_enabled=False,reduced_motion="reduce")
            page = await context.new_page()
            for path in ROUTES:
                report["results"].append(await examine(page,path,390,False,True,report | {"origin":origin}))
            await context.close()
        finally:
            await browser.close()
    report["browser_observed"] = sum(r["status"]=="OBSERVED_IN_BROWSER" for r in report["results"])
    report["blocked"] = sum(r["status"]!="OBSERVED_IN_BROWSER" for r in report["results"])
    report["release_decision"] = "HOLD"  # Requires true hosted JS, axe, CWV and independent QD.
    (root / "read_only_guest_receipt.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"mode":report["mode"],"tested":len(report["results"]),"browser_observed":report["browser_observed"],"blocked":report["blocked"],"release_decision":"HOLD"},indent=2))
    return 2 if report["blocked"] else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="ex2_guest_optin_receipt")
    parser.add_argument("--chromium", default=os.getenv("FV_CHROMIUM","/usr/bin/chromium"))
    parser.add_argument("--offline-fixture", action="store_true", help="tests ONLY localhost:8765, never provides hosted acceptance")
    args=parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))
