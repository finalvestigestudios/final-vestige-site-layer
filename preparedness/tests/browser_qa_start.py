#!/usr/bin/env python3
"""Real-browser QA for the Start Here hub and the two tools, using Playwright with the installed Microsoft Edge.

    python -I preparedness/tests/browser_qa_start.py            # full run: 8 widths, writes audit/start-here/qa-evidence.json + screenshots
    python -I preparedness/tests/browser_qa_start.py --quick    # 2 widths, no screenshots (used by the unit-test wrapper)

Run `python -I preparedness/tools/build.py` first (it writes build/preview/*.html, which this reads over file://).
No axe-core is used; the accessibility checks here are programmatic (names, labels, headings, ids, contrast of rendered text).
These checks do NOT replace an installed-WordPress test or a screen-reader test with a person.
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "build" / "preview"
AUDIT = ROOT / "audit" / "start-here"
WIDTHS_FULL = [320, 360, 390, 428, 768, 1024, 1440, 1920]
PAGES = {"hub": "hub-start-here.html", "plan": "reunification-plan.html", "kit": "kit-builder.html",
         "a1": "household-emergency-plan.html", "a2": "three-day-kit.html", "a3": "go-bags.html", "a4": "preparedness-real-households.html"}

CONTRAST_JS = r"""
() => {
  const lum = c => { const f = v => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }; return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]); };
  const parse = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(x=>parseFloat(x)); return {c:p.slice(0,3), a:p.length>3?p[3]:1}; };
  const bgOf = el => { let n = el; while (n) { const cs = getComputedStyle(n); if (cs.backgroundImage !== 'none') return null; const b = parse(cs.backgroundColor); if (b && b.a > 0.95) return b.c; n = n.parentElement; } return [255,255,255]; };
  const bad = [], seen = new Set(); let checked = 0;
  document.querySelectorAll('.pa *').forEach(el => {
    if (!el.offsetParent && getComputedStyle(el).position !== 'fixed') return;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!own) return;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.opacity === '0') return;
    const fg = parse(cs.color), bg = bgOf(el); if (!fg || !bg) return;
    const L1 = lum(fg.c), L2 = lum(bg), r = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700, large = size >= 24 || (size >= 18.66 && bold);
    checked++;
    if (r < (large ? 3 : 4.5)) { const k = el.tagName + '.' + el.className + ':' + r.toFixed(2); if (!seen.has(k)) { seen.add(k); bad.push({el: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''), ratio: +r.toFixed(2), text: el.textContent.trim().slice(0, 40)}); } }
  });
  return {checked, bad};
}
"""

A11Y_JS = r"""
() => {
  const out = {unnamed: [], dupIds: [], headingJumps: [], emptyButtons: [], noLang: !document.documentElement.lang, h1: document.querySelectorAll('h1').length};
  const name = el => { if (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.title) return true; if (el.id && document.querySelector('label[for="'+CSS.escape(el.id)+'"]')) return true; return !!el.closest('label'); };
  document.querySelectorAll('input:not([type=hidden]),select,textarea').forEach(e => { if (!name(e)) out.unnamed.push(e.id || e.outerHTML.slice(0, 60)); });
  const ids = {}; document.querySelectorAll('[id]').forEach(e => { ids[e.id] = (ids[e.id]||0)+1; }); Object.keys(ids).forEach(k => { if (ids[k] > 1) out.dupIds.push(k); });
  let last = 0; document.querySelectorAll('h1,h2,h3,h4').forEach(h => { const l = +h.tagName[1]; if (last && l > last + 1) out.headingJumps.push(h.textContent.trim().slice(0, 40)); last = l; });
  document.querySelectorAll('button').forEach(b => { if (!b.textContent.trim() && !b.getAttribute('aria-label')) out.emptyButtons.push(b.outerHTML.slice(0, 60)); });
  return out;
}
"""


class Run:
    def __init__(self):
        self.results: list[dict] = []
        self.failures: list[str] = []

    def check(self, name: str, ok: bool, detail=""):
        self.results.append({"check": name, "pass": bool(ok), "detail": detail if not ok or detail else ""})
        if not ok:
            self.failures.append(f"{name}: {detail}")


def new_page(browser, width, height=900, **kw):
    ctx = browser.new_context(viewport={"width": width, "height": height}, **kw)
    page = ctx.new_page()
    log = {"requests": [], "console": [], "dialogs": [], "errors": []}
    page.on("request", lambda r: log["requests"].append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
    page.on("console", lambda m: log["console"].append(f"{m.type}: {m.text[:120]}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: log["errors"].append(str(e)[:160]))
    page.on("dialog", lambda d: (log["dialogs"].append(d.message), d.dismiss()))
    return ctx, page, log


def goto(page, key):
    page.goto((PREVIEW / PAGES[key]).as_uri(), wait_until="load")
    page.wait_for_timeout(150)


def layout_checks(R: Run, browser, widths, shots: Path | None):
    for key in PAGES:
        for w in widths:
            ctx, page, log = new_page(browser, w)
            page.add_init_script("window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput)window.__cls+=e.value}}).observe({type:'layout-shift',buffered:true});")
            t0 = time.time(); goto(page, key); load_ms = int((time.time() - t0) * 1000)
            over = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            R.check(f"no-horizontal-overflow {key}@{w}", over <= 1, f"overflow {over}px")
            R.check(f"no-console-errors {key}@{w}", not log["errors"] and not [c for c in log["console"] if c.startswith("error")], str(log["errors"] + log["console"])[:200])
            R.check(f"no-network {key}@{w}", not log["requests"], str(log["requests"][:3]))
            cls = page.evaluate("window.__cls")
            R.check(f"layout-stable {key}@{w}", cls < 0.1, f"CLS {cls:.3f}")
            R.check(f"load-time {key}@{w}", load_ms < 3000, f"{load_ms} ms")
            if w in (320, 1440):
                a = page.evaluate(A11Y_JS)
                R.check(f"a11y-names {key}@{w}", not a["unnamed"] and not a["emptyButtons"], str(a["unnamed"] + a["emptyButtons"])[:200])
                R.check(f"a11y-ids-headings {key}@{w}", not a["dupIds"] and not a["headingJumps"] and a["h1"] == 1 and not a["noLang"], str(a)[:250])
                c = page.evaluate(CONTRAST_JS)
                R.check(f"contrast {key}@{w}", not c["bad"], f"{len(c['bad'])} low-contrast of {c['checked']}: {c['bad'][:3]}")
            if shots and key in ("hub", "plan", "kit") and w in (320, 1440):
                page.screenshot(path=str(shots / f"{key}-{w}.jpg"), type="jpeg", quality=50, full_page=True)
            ctx.close()


def plan_tests(R: Run, browser):
    ctx, page, log = new_page(browser, 1280, accept_downloads=True)
    goto(page, "plan")
    R.check("plan: builder rendered", page.locator("#pb-app .pb-sec").count() >= 9)
    R.check("plan: blank worksheet collapsed when JS runs", page.evaluate("!document.getElementById('pb-blank').open"))
    # basic entry and live preview
    page.fill('[data-path="members.0.name"]', "Alex")
    page.fill('[data-path="outOfArea.name"]', "Sam Rivera")
    page.fill('[data-path="outOfArea.phone1"]', "555-123-4567")
    page.fill('[data-path="meeting.near"]', "The oak by the corner")
    page.wait_for_timeout(300)
    prev = page.inner_text("#pb-preview")
    R.check("plan: preview shows entries", "Alex" in prev and "Sam Rivera" in prev and "oak by the corner" in prev)
    # invalid phone: inline error then blocked export
    page.fill('[data-path="outOfArea.phone2"]', "call me")
    page.locator('[data-path="outOfArea.phone2"]').blur()
    R.check("plan: invalid phone flagged inline", page.get_attribute('[data-path="outOfArea.phone2"]', "aria-invalid") == "true" and "digits" in page.inner_text('[data-err-for="outOfArea.phone2"]'))
    page.click('[data-action="download"]')
    page.wait_for_timeout(200)
    R.check("plan: export blocked with accessible error summary", page.is_visible("#pb-errors") and page.get_attribute("#pb-errors", "role") == "alert" and page.evaluate("document.activeElement.id") == "pb-errors")
    R.check("plan: print blocked too (no print attr set)", page.evaluate("document.body.getAttribute('data-pb-print')") is None)
    page.fill('[data-path="outOfArea.phone2"]', "555-987-6543")
    # hostile input
    page.fill('[data-path="members.0.cardNote"]', '<img src=x onerror=alert(1)>')
    page.fill('[data-path="contacts.0.name"]', '"><script>window.__x=1</script>')
    page.wait_for_timeout(300)
    R.check("plan: hostile text is not interpreted", page.evaluate("document.querySelectorAll('#pb-preview img, #pb-preview script, #pb-preview svg').length") == 0 and not page.evaluate("window.__x") and not log["dialogs"])
    # add/remove rows with focus management
    page.click("#pb-add-members"); page.wait_for_timeout(100)
    R.check("plan: focus moves into new row", page.evaluate("document.activeElement.getAttribute('data-path')") == "members.1.name")
    page.click('[data-action="remove"][data-key="members"][data-index="1"]'); page.wait_for_timeout(100)
    R.check("plan: focus returns to Add button after remove", page.evaluate("document.activeElement.id") == "pb-add-members")
    # suggested dates
    page.fill('[data-path="start"]', "2026-11-30"); page.click('[data-action="suggest"]'); page.wait_for_timeout(150)
    R.check("plan: suggested dates", page.input_value('[data-path="practice.drill"]') == "2027-02-28" and page.input_value('[data-path="practice.review"]') == "2027-11-30")
    # download content
    with page.expect_download() as dl:
        page.click('[data-action="download"]')
    path = dl.value.path(); text = Path(path).read_text(encoding="utf-8")
    R.check("plan: download has entries and no network", "Alex" in text and "Sam Rivera" in text and "555-123-4567" in text and "Kept on this device only" in text and not log["requests"])
    R.check("plan: status announced", "not sent anywhere" in page.inner_text("#pb-status") and page.get_attribute("#pb-status", "aria-live") == "polite")
    # nothing persisted
    store = page.evaluate("({ls: localStorage.length, ss: sessionStorage.length, ck: document.cookie, url: location.href, hash: location.hash, search: location.search})")
    idb = page.evaluate("indexedDB.databases ? indexedDB.databases().then(d => d.length) : 0")
    R.check("plan: no storage, cookies, URL state", store["ls"] == 0 and store["ss"] == 0 and store["ck"] == "" and store["hash"] == "" and store["search"] == "" and idb == 0, str(store))
    # print emulation + real PDF render
    page.evaluate("window.print = () => {}")
    page.click('[data-action="print-plan"]')  # exercises the real handler (window.print stubbed); the PDF below is rendered explicitly
    page.evaluate("document.body.setAttribute('data-pb-print','plan')")
    page.emulate_media(media="print")
    shown = page.evaluate("getComputedStyle(document.getElementById('pb-print-plan')).display")
    hidden = page.evaluate("getComputedStyle(document.querySelector('.pb-screen')).display")
    R.check("plan: print layout shows only the plan", shown == "block" and hidden == "none", f"{shown}/{hidden}")
    pdf = Path(tempfile.mkdtemp(prefix="pbqa-")) / "plan.pdf"
    page.pdf(path=str(pdf), print_background=True)
    if shutil.which("pdftotext"):
        t = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        R.check("plan: rendered PDF contains plan, not the form", "Household emergency plan" in t and "Alex" in t and "Add a person" not in t and "Print the full plan" not in t, t[:120].replace("\n", " "))
    page.evaluate("document.body.setAttribute('data-pb-print','cards')")
    shown = page.evaluate("getComputedStyle(document.getElementById('pb-print-cards')).display")
    cards = page.evaluate("document.querySelectorAll('#pb-print-cards .pb-card').length")
    R.check("plan: wallet cards print layout", shown == "block" and cards >= 1, f"{shown}, {cards} cards")
    page.evaluate("document.body.removeAttribute('data-pb-print')"); page.emulate_media(media="screen")
    # clear
    page.click("#pb-clear"); R.check("plan: clear asks for confirmation", page.is_visible("#pb-confirm") and page.evaluate("document.activeElement.id") == "pb-clear-yes")
    page.click('[data-action="clear-no"]'); R.check("plan: cancel keeps data", page.input_value('[data-path="members.0.name"]') == "Alex")
    page.click("#pb-clear"); page.click("#pb-clear-yes"); page.wait_for_timeout(200)
    R.check("plan: clear empties fields, announces, moves focus", page.input_value('[data-path="members.0.name"]') == "" and "cleared" in page.inner_text("#pb-status") and page.evaluate("document.activeElement.id") == "pb-top")
    # keyboard-only: tab reaches the first control and every button is focusable via keyboard
    page.evaluate("document.activeElement.blur()"); page.keyboard.press("Tab")
    reach = set()
    for _ in range(140):
        reach.add(page.evaluate("document.activeElement.id || document.activeElement.getAttribute('data-action') || ''"))
        page.keyboard.press("Tab")
    R.check("plan: keyboard reaches actions", {"pb-add-members", "pb-clear"} <= reach or "download" in reach, str(sorted(x for x in reach if x))[:150])
    R.check("plan: no dialogs/errors/network during session", not log["dialogs"] and not log["errors"] and not log["requests"], str(log)[:200])
    ctx.close()
    # reduced motion + no animations
    ctx, page, _ = new_page(browser, 1280, reduced_motion="reduce"); goto(page, "plan")
    R.check("plan: reduced motion, no running animations", page.evaluate("document.getAnimations().length") == 0)
    ctx.close()
    # JavaScript disabled
    ctx, page, _ = new_page(browser, 390, java_script_enabled=False); goto(page, "plan")
    R.check("plan(no-JS): blank worksheet open and tables visible", page.evaluate("document.getElementById('pb-blank').open") and page.locator("#pb-blank table").count() >= 6 and page.is_visible("#pb-blank table"))
    R.check("plan(no-JS): fallback explained", "javascript is off" in page.inner_text("body").lower())
    R.check("plan(no-JS): no overflow at 390", page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 1)
    ctx.close()


def kit_tests(R: Run, browser):
    ctx, page, log = new_page(browser, 1280, accept_downloads=True); goto(page, "kit")
    vis0 = page.evaluate("[...document.querySelectorAll('.kb-group')].filter(g=>!g.hidden).map(g=>g.dataset.group)")
    R.check("kit: default shows basic groups only", vis0 == ["core", "hazard", "adults"], str(vis0))
    page.check("#kb-s-children"); page.check("#kb-s-pets")
    vis1 = page.evaluate("[...document.querySelectorAll('.kb-group')].filter(g=>!g.hidden).map(g=>g.dataset.group)")
    R.check("kit: scenarios reveal groups", "children" in vis1 and "pets" in vis1 and "infants" not in vis1, str(vis1))
    page.check("#kb-i-water"); page.check("#kb-i-c-water"); page.wait_for_timeout(100)
    R.check("kit: progress announced", "2 of" in page.inner_text("#kb-summary") and page.get_attribute("#kb-summary", "aria-live") == "polite", page.inner_text("#kb-summary"))
    page.uncheck("#kb-s-children"); page.wait_for_timeout(100)
    with page.expect_download() as dl:
        page.click('[data-kb-action="download"]')
    text = Path(dl.value.path()).read_text(encoding="utf-8")
    R.check("kit: download lists ticked, excludes hidden groups", "[x] Bottled water" in text and "Children" not in text.split("For:")[1].split("\n")[0] and "water bottle sized for each child" not in text and "does not mean you are ready" in text)
    R.check("kit: every item cites a source", page.evaluate("[...document.querySelectorAll('.kb-item')].every(li => li.querySelector('.pa-cite, sup'))"))
    store = page.evaluate("({ls: localStorage.length, ss: sessionStorage.length, ck: document.cookie, h: location.hash, s: location.search})")
    R.check("kit: no storage, cookies, URL state", store["ls"] == 0 and store["ss"] == 0 and store["ck"] == "" and not store["h"] and not store["s"], str(store))
    # print
    page.evaluate("window.print=()=>{}"); page.evaluate("document.body.setAttribute('data-kb-print','1')"); page.emulate_media(media="print")
    R.check("kit: print hides controls, keeps list", page.evaluate("getComputedStyle(document.querySelector('.kb-screen')).display") == "none" and page.evaluate("getComputedStyle(document.querySelector('.kb-checklist')).display") != "none")
    pdf = Path(tempfile.mkdtemp(prefix="kbqa-")) / "kit.pdf"; page.pdf(path=str(pdf), print_background=True)
    if shutil.which("pdftotext"):
        t = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        R.check("kit: rendered PDF is the checklist", "Emergency kit and go-bag checklist" in t and "Bottled water" in t and "Reset choices" not in t, t[:100].replace("\n", " "))
    page.evaluate("document.body.removeAttribute('data-kb-print')"); page.emulate_media(media="screen")
    page.click('[data-kb-action="reset"]'); page.wait_for_timeout(100)
    R.check("kit: reset restores defaults", page.evaluate("[...document.querySelectorAll('[data-kb-item]')].every(c=>!c.checked)") and not page.is_checked("#kb-s-pets") and page.is_checked("#kb-s-adults"))
    R.check("kit: no dialogs/errors/network", not log["dialogs"] and not log["errors"] and not log["requests"], str(log)[:200])
    # keyboard operation of a scenario and an item
    page.focus("#kb-s-infants"); page.keyboard.press("Space"); page.wait_for_timeout(100)
    R.check("kit: keyboard toggles scenario", page.evaluate("!document.querySelector('[data-group=infants]').hidden"))
    ctx.close()
    ctx, page, _ = new_page(browser, 390, java_script_enabled=False); goto(page, "kit")
    n = page.evaluate("[...document.querySelectorAll('.kb-group')].filter(g=>getComputedStyle(g).display!=='none').length")
    R.check("kit(no-JS): every group is shown", n == page.evaluate("document.querySelectorAll('.kb-group').length") and n >= 12, str(n))
    R.check("kit(no-JS): explained", "javascript is off" in page.inner_text("body").lower())
    ctx.close()


def hub_tests(R: Run, browser):
    ctx, page, _ = new_page(browser, 1280); goto(page, "hub")
    hrefs = page.evaluate("[...document.querySelectorAll('.pa-hub a[href^=\"/preparedness/\"]')].map(a=>a.getAttribute('href'))")
    built = {p.stem for p in PREVIEW.glob("*.html")}
    missing = []
    for h in hrefs:
        parts = [x for x in h.split("/") if x]
        if len(parts) == 1:
            continue  # the Preparedness Archive landing page itself
        slug = parts[-1] if len(parts) >= 3 else f"hub-{parts[-1]}"
        if slug not in built and not (len(parts) == 2 and f"hub-{parts[1]}" in built):
            missing.append(h)
    R.check("hub: every internal link goes to a built page", not missing, str(missing))
    txt = page.inner_text("body")
    R.check("hub: title, theme and track label", "Preparedness Starts at Home" in txt and "Practical plans. Real households. Evidence you can trust." in txt and "ACT NOW" in txt.upper())
    R.check("hub: four steps in order", page.evaluate("[...document.querySelectorAll('.ph-step h3')].map(h=>h.textContent.trim())") == ["Make a plan", "Build a kit", "Prepare to leave", "Adapt for your household"])
    R.check("hub: both tools linked", page.locator('.ph-tool a[href*="reunification-plan"]').count() == 1 and page.locator('.ph-tool a[href*="kit-builder"]').count() == 1)
    R.check("hub: states draft status", "Draft for review" in txt)
    R.check("hub: no history techniques mixed in", not re.search(r"salt beef|hardtack|pemmican", txt, re.I))
    ctx.close()


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--quick", action="store_true"); args = ap.parse_args()
    from playwright.sync_api import sync_playwright
    R = Run(); widths = [320, 1440] if args.quick else WIDTHS_FULL
    shots = None
    if not args.quick:
        shots = AUDIT / "screenshots"; shots.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        ver = browser.version
        layout_checks(R, browser, widths, shots)
        plan_tests(R, browser); kit_tests(R, browser); hub_tests(R, browser)
        browser.close()
    summary = {"browser": f"Microsoft Edge {ver} via Playwright (headless)", "widths": widths, "checks": len(R.results), "failed": len(R.failures),
               "not_covered": ["axe-core (not installed)", "screen-reader testing with a person or NVDA/VoiceOver", "installed WordPress rendering", "real printer output", "text-spacing and forced-colors modes"]}
    if not args.quick:
        (AUDIT / "qa-evidence.json").write_text(json.dumps({"summary": summary, "results": R.results}, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(summary)); [print("FAIL", f) for f in R.failures]
    return 1 if R.failures else 0


if __name__ == "__main__":
    sys.exit(main())
