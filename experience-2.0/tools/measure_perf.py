#!/usr/bin/env python3
"""Lab performance measurement (NOT field data). Reports LCP, CLS and an interaction-latency proxy per page.

Profiles: `desktop` (no throttling) and `mobile` (390x844, 4x CPU slowdown, ~Slow-4G network via CDP).
Images are the REAL NASA files, so results depend on the network. A lab number is not a Core Web Vitals field result.
Exit code is non-zero if any page misses LCP <= 2.5 s or CLS <= 0.1 in the profile it is asserted for (--assert-profile).
"""
from __future__ import annotations

import argparse
import json
import sys

from playwright.sync_api import sync_playwright

import fvx_lib as lib
from browser import launch, serve

OBSERVE = """
() => {
  window.__fvx = {lcp: 0, cls: 0, longTasks: 0, events: []};
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__fvx.lcp = e.startTime; }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__fvx.cls += e.value; }).observe({type: 'layout-shift', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__fvx.events.push(e.duration); }).observe({type: 'event', durationThreshold: 16, buffered: true});
  new PerformanceObserver(l => { window.__fvx.longTasks += l.getEntries().length; }).observe({type: 'longtask', buffered: true});
}
"""

PROFILES = {
    "desktop": {"viewport": {"width": 1440, "height": 900}, "cpu": 1, "net": None, "mobile": False},
    "mobile": {"viewport": {"width": 390, "height": 844}, "cpu": 4, "net": {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8}, "mobile": True},
}


def measure(browser, url: str, profile: dict, interact: bool) -> dict:
    ctx = browser.new_context(viewport=profile["viewport"], has_touch=profile["mobile"], is_mobile=profile["mobile"])
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    if profile["cpu"] > 1:
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": profile["cpu"]})
    if profile["net"]:
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", profile["net"])
    page.add_init_script("(" + OBSERVE.strip() + ")()")
    page.goto(url, wait_until="load", timeout=120000)
    page.wait_for_timeout(2500)
    if interact:
        h = page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, h, 600):
            page.evaluate(f"window.scrollTo(0,{y})")
            page.wait_for_timeout(60)
        page.evaluate("window.scrollTo(0,0)")
        btn = page.locator("[data-fvx-open-source]").first
        if btn.count():
            btn.scroll_into_view_if_needed()
            btn.click()
            page.wait_for_timeout(300)
            page.keyboard.press("Escape")
        page.wait_for_timeout(800)
    m = page.evaluate("window.__fvx")
    ctx.close()
    return {"lcp_ms": round(m["lcp"]), "cls": round(m["cls"], 4), "long_tasks": m["longTasks"], "max_event_ms": round(max(m["events"], default=0)), "events_over_16ms": len(m["events"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-profile", default="desktop", choices=list(PROFILES))
    args = ap.parse_args()
    results: dict = {}
    failed = []
    with serve(lib.EX2 / "dist") as base, sync_playwright() as pw:
        browser = launch(pw)
        for name, path in {"flagship": "apollo-1/index.html", "desk": "research-desk/index.html", "atlas": "atlas/index.html"}.items():
            for pname, profile in PROFILES.items():
                r = measure(browser, f"{base}/{path}", profile, interact=(name == "flagship"))
                results[f"{name}/{pname}"] = r
                print(f"{name:9s} {pname:8s} LCP={r['lcp_ms']}ms CLS={r['cls']} longtasks={r['long_tasks']} slowest-event={r['max_event_ms']}ms")
                if pname == args.assert_profile and (r["lcp_ms"] > 2500 or r["cls"] > 0.1 or r["max_event_ms"] > 200):
                    failed.append(f"{name}/{pname}: {r}")
        browser.close()
    results["_note"] = "Lab measurement against live NASA images; not field data. mobile = 4x CPU + ~Slow-4G."
    (lib.EX2 / "dist" / "perf-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    if failed:
        print("FAIL: thresholds missed in the asserted profile", *failed, sep="\n  ")
        return 1
    print(f"OK: {args.assert_profile} profile within LCP<=2500ms, CLS<=0.1, event<=200ms (lab only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
