import json, sys
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright
PREV = Path(r"C:\Users\brhod\OneDrive\Desktop\Projects\_wt-r47-lf\preparedness\build\preview")
AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"
pages = sorted(p.stem for p in PREV.glob("*.html"))
arts = [p for p in pages if not p.startswith("hub-") and p not in ("landing", "water-planner")]
R = {"axe": {}, "overflow": [], "wide_toc_open": {}, "narrow_toc_closed": {}, "nojs_narrow_toc_closed": {}, "nojs_wide_toc_closed": {}, "print": {}, "kbd": {}, "errors": []}
u = lambda n: (PREV / f"{n}.html").as_uri()
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    for n in pages:
        for w in (390, 768, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(u(n))
            if pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"): R["overflow"].append(f"{n}@{w}")
            if errs: R["errors"].append((n, w, errs))
            if n in arts:
                st = pg.evaluate("() => { const d = document.querySelector('.pa-toc details'); return d ? d.open : null; }")
                (R["wide_toc_open"] if w == 1440 else R["narrow_toc_closed"]).setdefault(n, {})[w] = st
            if w in (390, 1440):
                pg.add_script_tag(url=AXE)
                v = pg.evaluate("""async () => { const r = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}}); return r.violations.map(x => [x.id, x.impact, x.nodes.length]); }""")
                R["axe"][f"{n}@{w}"] = v
            ctx.close()
    for n in arts:
        for w, key in ((390, "nojs_narrow_toc_closed"), (1440, "nojs_wide_toc_closed")):
            ctx = b.new_context(viewport={"width": w, "height": 900}, java_script_enabled=False); pg = ctx.new_page(); pg.goto(u(n))
            R[key][n] = pg.evaluate("() => { const d = document.querySelector('.pa-toc details'); return d ? !d.open : null; }"); ctx.close()
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); pg.goto(u(n)); pg.emulate_media(media="print")
        info = pg.evaluate("() => ({toc: getComputedStyle(document.querySelector('.pa-toc')).display, head: getComputedStyle(document.querySelector('.pa-printbar--head')).display, end: getComputedStyle(document.querySelector('.pa-printbar--end')).display})")
        txt = " ".join(x.get_text() for x in fitz.open(stream=pg.pdf(format="Letter"), filetype="pdf"))
        info["pdf_has_act_and_sources"] = ("Sources and verification" in txt); R["print"][n] = info; ctx.close()
    # keyboard on a narrow article: summary reachable, toggles with Enter, links reachable after open
    ctx = b.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); pg.goto(u("making-water-safer"))
    seq = []
    for i in range(5):
        pg.keyboard.press("Tab"); seq.append(pg.evaluate("() => { const e = document.activeElement; return (e.tagName + ':' + (e.innerText||'').trim().slice(0,30)); }"))
    R["kbd"]["tab_order_first5"] = seq
    pg.focus(".pa-toc summary"); before = pg.evaluate("document.querySelector('.pa-toc details').open"); pg.keyboard.press("Enter"); after = pg.evaluate("document.querySelector('.pa-toc details').open")
    R["kbd"]["enter_toggles"] = [before, after]
    ow = pg.evaluate("() => { const s = document.querySelector('.pa-toc summary'); const cs = getComputedStyle(s); return {outline: cs.outlineStyle, h: s.getBoundingClientRect().height}; }"); R["kbd"]["summary_focus_outline_and_height"] = ow
    pg.screenshot(path=str(Path(sys.argv[1]) / "f1-after-making-water-safer-390-toc-open.png")); ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); pg.goto(u("making-water-safer")); pg.screenshot(path=str(Path(sys.argv[1]) / "f1-after-making-water-safer-390.png")); ctx.close()
    ctx = b.new_context(viewport={"width": 390, "height": 844}); pg = ctx.new_page(); pg.goto(u("medication-and-devices")); pg.screenshot(path=str(Path(sys.argv[1]) / "f1-after-medication-and-devices-390.png")); ctx.close()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); pg = ctx.new_page(); pg.goto(u("making-water-safer")); pg.screenshot(path=str(Path(sys.argv[1]) / "f1-after-making-water-safer-1440.png")); ctx.close()
    b.close()
viol = {k: v for k, v in R["axe"].items() if v}
print("axe runs", len(R["axe"]), "with violations", len(viol), viol if viol else "")
print("overflow:", R["overflow"]); print("js errors:", R["errors"])
print("wide toc open (JS on):", sum(1 for v in R["wide_toc_open"].values() if v.get(1440) is True), "/", len(R["wide_toc_open"]))
print("narrow toc closed 390/768 (JS on):", sum(1 for v in R["narrow_toc_closed"].values() if v.get(390) is False), sum(1 for v in R["narrow_toc_closed"].values() if v.get(768) is False), "/", len(R["narrow_toc_closed"]), "(768 container may be <900)")
print("no-JS narrow closed:", sum(1 for v in R["nojs_narrow_toc_closed"].values() if v), "/", len(arts), "| no-JS wide closed (accepted degradation):", sum(1 for v in R["nojs_wide_toc_closed"].values() if v))
print("print: toc hidden", sum(1 for v in R["print"].values() if v["toc"] == "none"), "head btn hidden", sum(1 for v in R["print"].values() if v["head"] == "none"), "end btn hidden", sum(1 for v in R["print"].values() if v["end"] == "none"), "sources in pdf", sum(1 for v in R["print"].values() if v["pdf_has_act_and_sources"]), "/", len(arts))
print("kbd:", R["kbd"])
json.dump(R, open(sys.argv[1] + "/f1_regress.json", "w"), indent=1, default=str)
