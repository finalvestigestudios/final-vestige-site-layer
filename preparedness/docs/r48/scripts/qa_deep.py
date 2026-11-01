import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright
sys.path.insert(0, r"C:\Users\brhod\OneDrive\Desktop\Projects\_wt-r47-lf\preparedness\tools")
import build

PREV = Path(r"C:\Users\brhod\OneDrive\Desktop\Projects\_wt-r47-lf\preparedness\build\preview")
OUT = Path("qa_out"); SH = OUT / "shots"; SH.mkdir(parents=True, exist_ok=True)
AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"
PAGES = sorted(p.stem for p in PREV.glob("*.html"))
lib = build.Library()
ROUTES = {"/preparedness/": "landing"}
for p in PAGES:
    if p.startswith("hub-"): ROUTES[f"/preparedness/{p[4:]}/"] = p
for s in lib.articles: ROUTES[lib.url_path(s)] = s
R = {}
t0 = time.time()
def url(n): return (PREV / f"{n}.html").as_uri()

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")

    # 1 internal links ---------------------------------------------------------
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page()
    internal = {}; unresolved = {}
    for n in PAGES:
        pg.goto(url(n))
        for h in pg.evaluate("() => [...document.querySelectorAll('a[href^=\"/\"]')].map(a => a.getAttribute('href'))"):
            path = h.split("#")[0]
            internal.setdefault(h, set()).add(n)
            if path not in ROUTES: unresolved.setdefault(path, set()).add(n)
    R["internal_links"] = {"distinct": len(internal), "archive_unresolved": {k: sorted(v) for k, v in unresolved.items()}}
    ctx.close(); print("links", round(time.time()-t0), flush=True); json.dump(R, open(OUT / "deep.json", "w"), indent=1)

    # 2 keyboard ---------------------------------------------------------------
    kb = {}
    for n in PAGES:
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); pg.goto(url(n))
        stops = []
        for i in range(10):
            pg.keyboard.press("Tab")
            stops.append(pg.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null; const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
              return {tag: e.tagName, text: (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 40), outline: cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0, shadow: cs.boxShadow !== 'none', visible: r.width > 0 && r.height > 0}; }"""))
        first = stops[0]
        pg.keyboard.press("Shift+Tab"); pg.keyboard.press("Shift+Tab")
        # activate skip link
        pg.goto(url(n)); pg.keyboard.press("Tab"); pg.keyboard.press("Enter"); hashv = pg.evaluate("location.hash")
        kb[n] = {"first": first, "stops_with_no_visible_focus": [s for s in stops if s and not (s["outline"] or s["shadow"])], "nulls": sum(1 for s in stops if s is None), "skip_hash": hashv}
        ctx.close()
    R["keyboard"] = kb; print("keyboard", round(time.time()-t0), flush=True); json.dump(R, open(OUT / "deep.json", "w"), indent=1)

    # 3 JS disabled ------------------------------------------------------------
    nojs = {}
    for n in PAGES:
        c1 = b.new_context(viewport={"width": 1280, "height": 900}); c2 = b.new_context(viewport={"width": 1280, "height": 900}, java_script_enabled=False)
        a = c1.new_page(); a.goto(url(n)); la = a.evaluate("document.querySelector('.pa').innerText.length")
        z = c2.new_page(); z.goto(url(n)); lz = z.evaluate("document.querySelector('.pa').innerText.length")
        extra = {}
        if n == "landing": extra["cards_visible_nojs"] = z.evaluate("[...document.querySelectorAll('.pa-card')].filter(c => c.offsetParent !== null).length"); extra["cards_total"] = z.evaluate("document.querySelectorAll('.pa-card').length")
        if n == "water-planner": extra["results_text_nojs"] = z.evaluate("document.getElementById('wp-out').innerText.length"); extra["noscript"] = z.evaluate("!!document.querySelector('noscript')")
        nojs[n] = {"js_len": la, "nojs_len": lz, "same_content": abs(la - lz) < 40, **extra}
        c1.close(); c2.close()
    R["no_js"] = nojs; print("nojs", round(time.time()-t0), flush=True); json.dump(R, open(OUT / "deep.json", "w"), indent=1)

    # 4 print ------------------------------------------------------------------
    pr = {}
    for n in PAGES:
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); pg.goto(url(n)); pg.emulate_media(media="print")
        info = pg.evaluate("""() => { const pa = document.querySelector('.pa'); const toc = document.querySelector('.pa-toc'); const f = document.querySelector('.pa-filter'); const bar = document.querySelector('.pa-printbar');
          return {bg: getComputedStyle(pa).backgroundColor, tocHidden: toc ? getComputedStyle(toc).display === 'none' : null, filterHidden: f ? getComputedStyle(f).display === 'none' : null, barHidden: bar ? getComputedStyle(bar).display === 'none' : null, toolHidden: document.querySelector('.pa-tool') ? getComputedStyle(document.querySelector('.pa-tool')).display === 'none' : null}; }""")
        pdf = pg.pdf(format="Letter", print_background=False); doc = fitz.open(stream=pdf, filetype="pdf")
        txt = " ".join(pg_.get_text() for pg_ in doc)
        info.update(pdf_pages=doc.page_count, pdf_has_text=len(txt) > 500, shows_sources=("Sources and verification" in txt) if n not in ("landing",) and not n.startswith("hub-") else None, shows_draft=("Draft" in txt))
        pr[n] = info; ctx.close()
    R["print"] = pr; print("print", round(time.time()-t0), flush=True); json.dump(R, open(OUT / "deep.json", "w"), indent=1)

    # 5 reduced motion ---------------------------------------------------------
    ctx = b.new_context(reduced_motion="reduce"); pg = ctx.new_page(); pg.goto(url("landing"))
    R["reduced_motion"] = pg.evaluate("() => ({card: getComputedStyle(document.querySelector('.pa-card')).transitionDuration, link: getComputedStyle(document.querySelector('.pa a')).transitionDuration})")
    ctx.close()
    ctx = b.new_context(); pg = ctx.new_page(); pg.goto(url("landing"))
    R["normal_motion"] = pg.evaluate("() => ({card: getComputedStyle(document.querySelector('.pa-card')).transitionDuration})"); ctx.close()

    # 6 axe ---------------------------------------------------------------------
    ax = {}
    for n in PAGES:
        for w in (390, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); pg.goto(url(n)); pg.add_script_tag(url=AXE)
            v = pg.evaluate("""async () => { const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}}); return {violations: r.violations.map(x => [x.id, x.impact, x.nodes.length]), incomplete: r.incomplete.map(x => x.id)}; }""")
            ax[f"{n}@{w}"] = v; ctx.close()
    R["axe"] = ax; print("axe", round(time.time()-t0), flush=True); json.dump(R, open(OUT / "deep.json", "w"), indent=1)

    # 7 planner UI edge cases ---------------------------------------------------
    ctx = b.new_context(viewport={"width": 390, "height": 900}); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url("water-planner")); cases = []
    def setv(vals, hot=False):
        for k in ("wp-people", "wp-days", "wp-stored", "wp-filled", "wp-pets", "wp-petgal", "wp-extra"):
            try: pg.fill("#" + k, vals.get(k, ""))
            except Exception as e: cases.append({"case": "input rejected by browser", "field": k, "value": vals.get(k), "err": str(e)[:60]})
        pg.set_checked("#wp-hot", hot)
        return pg.inner_text("#wp-out")
    for label, vals, hot in [("empty", {}, False), ("zero people", {"wp-people": "0", "wp-days": "3"}, False), ("negative", {"wp-people": "-4", "wp-days": "-3", "wp-stored": "-9"}, False),
                             ("huge", {"wp-people": "999999", "wp-days": "999999"}, False), ("decimals", {"wp-people": "2.7", "wp-days": "3.2"}, False),
                             ("1 person 1 day", {"wp-people": "1", "wp-days": "1"}, False), ("stored exceeds need", {"wp-people": "2", "wp-days": "3", "wp-stored": "50"}, False),
                             ("hot + pet + extra", {"wp-people": "4", "wp-days": "14", "wp-pets": "2", "wp-petgal": "0.5", "wp-extra": "1"}, True),
                             ("bad date", {"wp-people": "1", "wp-days": "3", "wp-filled": "2026-02-30"}, False), ("pet without amount", {"wp-people": "2", "wp-days": "3", "wp-pets": "3"}, False)]:
        out = setv(vals, hot)
        nums = re.findall(r"-?\d[\d,]*\.?\d*", out)
        cases.append({"case": label, "has_NaN": "NaN" in out or "undefined" in out or "Infinity" in out, "has_negative": bool(re.search(r"(?<![\d\w])-\d", out)), "total_line": next((l for l in out.splitlines() if l.startswith("Total to plan for")), "")[:60], "still": next((l for l in out.splitlines() if l.startswith("Still to store")), "")[:50]})
    R["planner"] = {"cases": cases, "js_errors": errs, "region_role": pg.get_attribute("#wp-out", "role"), "aria_live": pg.get_attribute("#wp-out", "aria-live")}
    ctx.close(); print("planner", round(time.time()-t0), flush=True)

    # 8 screenshots ---------------------------------------------------------------
    for n, w, full in [("landing", 1440, False), ("landing", 390, False), ("hub-water", 1440, False), ("hub-lost-ways", 390, False), ("making-water-safer", 1440, False), ("making-water-safer", 390, False),
                       ("medication-and-devices", 390, False), ("salt-beef-salt-pork-age-of-sail", 1440, False), ("water-planner", 1440, False), ("water-planner", 390, False), ("outage-heat-cold-generators", 390, False), ("pressure-canning-low-acid", 1440, False)]:
        ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); pg.goto(url(n)); pg.screenshot(path=str(SH / f"{n}-{w}.png"), full_page=full); ctx.close()
    b.close()

# 9 site-level (non-archive) links ----------------------------------------------
site = {}
for h in sorted({k.split("#")[0] for k in internal if k.split("#")[0] not in ROUTES}):
    try:
        req = urllib.request.Request("https://finalvestige.com" + h, headers={"User-Agent": "FinalVestigePreparednessQA/1.0 (read-only link check)"}, method="GET")
        with urllib.request.urlopen(req, timeout=25) as r: site[h] = r.status
    except urllib.error.HTTPError as e: site[h] = e.code
    except Exception as e: site[h] = f"{type(e).__name__}"
R["site_links_live_status"] = site
json.dump(R, open(OUT / "deep.json", "w"), indent=1)
print("deep pass complete", round(time.time() - t0), "s")
