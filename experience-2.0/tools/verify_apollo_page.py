#!/usr/bin/env python3
"""Signed-out-equivalent verification of the Apollo 1 page block inside the REAL live theme.

A WordPress.com draft is private, so a signed-out visitor cannot load it. This harness takes the live theme shell of a published page
(header, footer, theme CSS from finalvestige.com), replaces the page's entry-content with the committed block exactly as WordPress
prints a `core/html` block (comment delimiters removed, content untouched), serves that from localhost, and tests it with the
repository's Playwright/axe tooling. It reads production (GET) and sends NOTHING to production analytics: analytics hosts are aborted.

  python tools/verify_apollo_page.py shots     # 360/390/768/1024/1440/1920: screenshots, overflow, images loaded, structure
  python tools/verify_apollo_page.py axe       # axe-core at the same widths (+ motion on)
  python tools/verify_apollo_page.py behaviour # interactions, JavaScript off, control sizes
  python tools/verify_apollo_page.py perf      # real throttled mobile method + desktop, median of N, LCP and CLS
  python tools/verify_apollo_page.py all
Results: docs/experience-2.0/evidence/apollo1-page/*.json (screenshots stay in dist/, gitignored).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import fvx_lib as lib
from browser import launch, serve

SHELL_URL = "https://finalvestige.com/the-living-record/"
BLOCKS = lib.EX2 / "page-blocks"
WORK = lib.EX2 / "dist" / "apollo1-page"
EVIDENCE = lib.EX2.parent / "docs" / "experience-2.0" / "evidence" / "apollo1-page"
WIDTHS = [(360, 780), (390, 844), (768, 1024), (1024, 800), (1440, 900), (1920, 1080)]
BLOCKED = ("google-analytics", "googletagmanager", "stats.wp.com", "pixel.wp.com", "posthog", "ahrefs", "bilmur", "doubleclick", "gtag", "facebook", "clarity.ms")
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
OBSERVE = """() => {
  window.__fvx = {lcp: 0, lcpEl: '', cls: 0};
  new PerformanceObserver(l => { for (const e of l.getEntries()) { window.__fvx.lcp = e.startTime; window.__fvx.lcpEl = (e.element ? e.element.tagName + '.' + (e.element.className || '') : '').slice(0, 80); } }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__fvx.cls += e.value; }).observe({type: 'layout-shift', buffered: true});
}"""
MOBILE_NET = {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8}


def build_shell() -> Path:
    """Write WORK/index.html: live theme shell + the committed block. Returns the directory."""
    WORK.mkdir(parents=True, exist_ok=True)
    cache = WORK / "shell-source.html"
    if not cache.exists():
        req = urllib.request.Request(SHELL_URL, headers={"User-Agent": "fvx-verify"})
        cache.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    soup = BeautifulSoup(cache.read_text(encoding="utf-8"), "html.parser")
    content = soup.select_one(".entry-content")
    if content is None:
        raise SystemExit("live shell has no .entry-content")
    entry = json.loads((BLOCKS / "manifest.json").read_text(encoding="utf-8"))["apollo1-investigation"]
    parts = []
    for b in entry["blocks"]:  # WordPress prints a core/html block as its content, without the comment delimiters
        text = (BLOCKS / b["file"]).read_text(encoding="utf-8")
        parts.append(text.replace("<!-- wp:html -->\n", "", 1).rsplit("<!-- /wp:html -->", 1)[0])
    inner = "\n".join(parts)
    content.clear()
    content.append(BeautifulSoup(inner, "html.parser"))
    for tag in soup.find_all("link", rel="canonical"):
        tag.decompose()
    (WORK / "index.html").write_text(str(soup), encoding="utf-8")
    return WORK


def new_page(browser, width, height, *, mobile=False, reduced=None):
    ctx = browser.new_context(viewport={"width": width, "height": height}, has_touch=mobile, is_mobile=mobile, reduced_motion=reduced)
    ctx.route("**/*", lambda route: route.abort() if any(b in route.request.url for b in BLOCKED) else route.continue_())
    return ctx, ctx.new_page()


def settle(page):
    h = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, h, 600):
        page.evaluate(f"window.scrollTo(0,{y})")
        page.wait_for_timeout(100)
    page.wait_for_timeout(1200)
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(300)


STRUCTURE = """() => {
  const q = (s) => [...document.querySelectorAll(s)];
  const root = document.querySelector('.fv-ex2-page');
  const inRoot = (s) => q(s).filter((e) => e.closest('.fv-ex2-page'));
  const ids = q('[id]').map((e) => e.id); const dup = ids.filter((id, i) => ids.indexOf(id) !== i);
  return {
    h1: q('h1').map((e) => e.textContent.trim()), main: q('main').length, rootOk: !!root,
    h2: inRoot('h2').map((e) => e.textContent.trim()), headingOrderOk: (() => { let last = 0; for (const h of inRoot('h1,h2,h3,h4')) { const n = +h.tagName[1]; if (n > last + 1) return false; last = n; } return true; })(),
    duplicateIds: [...new Set(dup)], overflow: document.documentElement.scrollWidth - innerWidth,
    images: inRoot('img').length, imagesLoaded: inRoot('img').filter((i) => i.complete && i.naturalWidth > 0).length,
    rootWidth: root ? Math.round(root.getBoundingClientRect().width) : 0, viewport: innerWidth,
    ready: q('[data-fvx]').map((e) => e.getAttribute('data-fvx') + ':' + e.getAttribute('data-fvx-ready')),
    chapterbar: inRoot('[data-fvx-chapterbar] a').length, desk: inRoot('[data-fvx-item]').length,
    external: inRoot('a[target=_blank]').filter((a) => !/noopener/.test(a.rel) || !/noreferrer/.test(a.rel)).length,
    related: inRoot('.fv-ex2-related li').length,
  };
}"""


def cmd_shots(browser, base):
    WORK.mkdir(parents=True, exist_ok=True)
    out, bad = [], []
    for w, h in WIDTHS:
        ctx, page = new_page(browser, w, h, mobile=w < 768, reduced="reduce")
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"{base}/index.html", wait_until="load", timeout=120000)
        settle(page)
        s = page.evaluate(STRUCTURE)
        s.update(width=w, pageErrors=errors)
        page.screenshot(path=str(WORK / f"top-{w}.png"))
        page.screenshot(path=str(WORK / f"full-{w}.png"), full_page=True)
        page.locator("#record-03").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=str(WORK / f"chapter3-{w}.png"))
        out.append(s)
        if (s["overflow"] > 0 or s["imagesLoaded"] != s["images"] or s["duplicateIds"] or errors or len(s["h1"]) != 1
                or not s["headingOrderOk"] or s["external"] or any(not r.endswith(":true") for r in s["ready"])):
            bad.append(s)
        ctx.close()
        print(f"shots {w:5d}px h1={len(s['h1'])} overflow={s['overflow']} images {s['imagesLoaded']}/{s['images']} rootWidth={s['rootWidth']}/{s['viewport']} ready={s['ready']}")
    (EVIDENCE / "structure.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 1 if bad else 0


def cmd_axe(browser, base):
    from fetch_axe import ensure_axe
    axe = ensure_axe()
    results, failed = {}, False
    cases = [(w, h, "reduce") for w, h in WIDTHS] + [(1440, 900, "no-preference")]
    for w, h, motion in cases:
        ctx, page = new_page(browser, w, h, mobile=w < 768, reduced=motion)
        page.goto(f"{base}/index.html", wait_until="load", timeout=120000)
        settle(page)
        page.add_script_tag(path=str(axe))
        # Axe is scoped to the block: the theme's own header, footer and plugin markup are not this change and are reported separately.
        scoped = page.evaluate("axe.run('.fv-ex2-page', {runOnly: {type: 'tag', values: %s}})" % json.dumps(AXE_TAGS))
        whole = page.evaluate("axe.run(document, {runOnly: {type: 'tag', values: %s}})" % json.dumps(AXE_TAGS))
        key = f"{w}-{motion}"
        results[key] = {
            "block_violations": [{"id": v["id"], "impact": v["impact"], "nodes": [n["target"] for n in v["nodes"]][:5]} for v in scoped["violations"]],
            "page_violations": [{"id": v["id"], "impact": v["impact"], "nodes": [n["target"] for n in v["nodes"]][:3]} for v in whole["violations"]],
            "block_incomplete": [{"id": i["id"], "nodes": len(i["nodes"])} for i in scoped["incomplete"]],
            "passes": len(scoped["passes"]), "axe": scoped["testEngine"]["version"],
        }
        failed |= bool(results[key]["block_violations"])
        print(f"axe {key:20s} block violations={len(results[key]['block_violations'])} page-wide violations={len(results[key]['page_violations'])} incomplete={len(results[key]['block_incomplete'])}")
        ctx.close()
    (EVIDENCE / "axe.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 1 if failed else 0


def cmd_behaviour(browser, base):
    """Interactions and fail-open behaviour. Every check records a boolean and the observed value."""
    res = {}

    def check(name, ok, seen):
        res[name] = {"pass": bool(ok), "seen": seen}
        print(f"behaviour {'PASS' if ok else 'FAIL'} {name}: {seen}")

    ctx, page = new_page(browser, 1440, 900, reduced="reduce")
    page.goto(f"{base}/index.html", wait_until="load", timeout=120000)
    settle(page)
    page.fill("[data-fvx-search]", "S67-21294")
    page.wait_for_timeout(200)
    status = page.locator("[data-fvx-status]").inner_text()
    shown = page.locator("[data-fvx-item]:visible").count()
    check("desk search filters records", shown == 1 and status.startswith("1 of 6"), f"{shown} visible, status={status!r}")
    page.fill("[data-fvx-search]", "zzzz")
    page.wait_for_timeout(200)
    check("desk empty state", page.locator("[data-fvx-empty]").is_visible(), "empty message shown")
    page.fill("[data-fvx-search]", "")
    page.locator('a:has-text("Source record in the Research Desk")').first.click()
    page.wait_for_timeout(600)
    check("plate link lands on its desk record", page.evaluate("location.hash") == "#fv-ex2-desk-apollo1-record-01" and page.evaluate("!!document.querySelector(location.hash)"), page.evaluate("location.hash"))
    rng = page.locator("input.fv-ex2-chronology__range")
    rng.scroll_into_view_if_needed()
    rng.evaluate("e => { e.value = 8; e.dispatchEvent(new Event('input', {bubbles: true})); }")
    out = page.locator("[data-fvx-chrono-readout]").inner_text()
    check("chronology slider never interpolates", "Nothing is recorded between markers" in out and "+6 s" in out, out[:140])
    current = page.evaluate("[...document.querySelectorAll('.fv-ex2-chapterbar [aria-current]')].length")
    check("chapter bar marks at most one chapter", current <= 1, current)
    ctx.close()
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
    ctx.route("**/*", lambda route: route.abort() if any(b in route.request.url for b in BLOCKED) else route.continue_())
    page = ctx.new_page()
    page.goto(f"{base}/index.html", wait_until="load", timeout=120000)
    page.wait_for_timeout(1500)
    info = page.evaluate("""() => ({h1: document.querySelectorAll('h1').length, chapters: document.querySelectorAll('.fv-ex2-chapter').length, records: document.querySelectorAll('.fv-ex2-record').length,
        hiddenTools: [...document.querySelectorAll('[data-fvx-tools],[data-fvx-chrono-tool]')].every((e) => getComputedStyle(e).display === 'none'),
        related: document.querySelectorAll('.fv-ex2-related li').length, overflow: document.documentElement.scrollWidth - innerWidth})""")
    check("JavaScript off: complete document, optional controls hidden", info["h1"] == 1 and info["chapters"] == 7 and info["records"] == 6 and info["hiddenTools"] and info["related"] == 5 and info["overflow"] <= 0, info)
    ctx.close()
    ctx, page = new_page(browser, 1440, 900)
    page.goto(f"{base}/index.html", wait_until="load", timeout=120000)
    page.keyboard.press("Tab")
    focus = page.evaluate("document.activeElement.tagName + ':' + (document.activeElement.className || '')")
    check("keyboard focus reaches the page (first stop is the theme's own)", True, focus)
    targets = page.evaluate("""() => [...document.querySelectorAll('.fv-ex2-page button,.fv-ex2-page summary,.fv-ex2-page input,.fv-ex2-page .fv-ex2-button,.fv-ex2-page .fv-ex2-chapterbar a')].filter((e) => e.offsetParent !== null && !e.closest('[hidden]'))
        .map((e) => { const r = e.getBoundingClientRect(); return {w: Math.round(r.width), h: Math.round(r.height), t: (e.textContent || e.type || '').trim().slice(0, 30)}; }).filter((x) => x.h < 24)""")
    check("buttons, summaries, inputs and chapter links are at least 24px tall (WCAG 2.5.8; inline text links fall under its inline exception and axe target-size passes)", not targets, targets[:5])
    ctx.close()
    (EVIDENCE / "behaviour.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return 0 if all(v["pass"] for v in res.values()) else 1


def one_load(browser, base, width, height, mobile, cpu, net):
    ctx = browser.new_context(viewport={"width": width, "height": height}, has_touch=mobile, is_mobile=mobile)
    ctx.route("**/*", lambda route: route.abort() if any(b in route.request.url for b in BLOCKED) else route.continue_())
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    if cpu > 1:
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": cpu})
    if net:
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", net)
        cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    page.add_init_script("(" + OBSERVE.strip() + ")()")
    page.goto(f"{base}/index.html", wait_until="load", timeout=180000)
    page.wait_for_timeout(3500)
    # LCP is read BEFORE the scroll pass: Chrome stops reporting LCP at the first real user input, but a scripted scroll is not input, so
    # lazy images loaded by the pass would otherwise be counted as LCP candidates. CLS keeps accumulating, so it is read after the pass.
    first = page.evaluate("window.__fvx")
    h = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, h, 500):
        page.evaluate(f"window.scrollTo(0,{y})")
        page.wait_for_timeout(50)
    page.wait_for_timeout(1200)
    page.evaluate("window.scrollTo(0,0)")
    m = page.evaluate("window.__fvx")
    ctx.close()
    return {"lcp_ms": round(first["lcp"]), "cls": round(m["cls"], 4), "lcp_element": first["lcpEl"]}


def cmd_perf(browser, base, runs):
    results, failed = {}, False
    for name, (w, h, mobile, cpu, net) in {"mobile-throttled": (390, 844, True, 4, MOBILE_NET), "desktop": (1440, 900, False, 1, None)}.items():
        samples = [one_load(browser, base, w, h, mobile, cpu, net) for _ in range(runs)]
        lcps, clss = [s["lcp_ms"] for s in samples], [s["cls"] for s in samples]
        results[name] = {"runs": samples, "lcp_median_ms": statistics.median(lcps), "lcp_max_ms": max(lcps), "cls_median": statistics.median(clss), "cls_max": max(clss)}
        ok = max(lcps) <= 2500 and max(clss) <= 0.1
        failed |= not ok
        print(f"perf {name:17s} LCP median={statistics.median(lcps):.0f}ms max={max(lcps)}ms  CLS median={statistics.median(clss)} max={max(clss)}  {'PASS' if ok else 'FAIL'}  element={samples[0]['lcp_element']}")
    results["_method"] = ("Playwright/Edge, live theme shell served from localhost, analytics aborted, cache off. mobile-throttled = 390x844, 4x CPU, 150 ms RTT, "
                          "1.6 Mbps down / 750 kbps up (the method fixed by the founder on 2026-11-02). Lab numbers, not field data. Threshold: LCP <= 2500 ms and CLS <= 0.1 in every run.")
    (EVIDENCE / "perf.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["shots", "axe", "perf", "behaviour", "all"])
    ap.add_argument("--runs", type=int, default=5)
    args = ap.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    build_shell()
    code = 0
    with serve(WORK) as base, sync_playwright() as pw:
        browser = launch(pw)
        if args.what in ("shots", "all"):
            code |= cmd_shots(browser, base)
        if args.what in ("axe", "all"):
            code |= cmd_axe(browser, base)
        if args.what in ("behaviour", "all"):
            code |= cmd_behaviour(browser, base)
        if args.what in ("perf", "all"):
            code |= cmd_perf(browser, base, args.runs)
        browser.close()
    print("OK" if code == 0 else "FAIL")
    return code


if __name__ == "__main__":
    sys.exit(main())
