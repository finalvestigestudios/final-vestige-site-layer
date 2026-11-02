"""Rendered QA of the integrated release candidate's private preview pages (local files, Edge via Playwright).

Run against a build made from the QA-simulated custody copy (see simulate_custody_update.py):
  python qa_candidate.py PREVIEW_DIR REPO_PREPAREDNESS_DIR OUT_DIR
Measures only; asserts nothing about safety or accuracy. Not the live Assembler theme, not a screen reader, not Lighthouse.
"""
import json, re, sys, time
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

PREV, PREP, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PREP / "tools"))
import build  # noqa: E402

AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"
PAGES = sorted(p.stem for p in PREV.glob("*.html"))
WIDTHS = [320, 360, 390, 640, 768, 1024, 1440, 1920]  # 640 = 200% zoom of 1280; 320 = 400% zoom of 1280
lib = build.Library(root=PREP)
ROUTES = {"/preparedness/": "landing"}
for n in PAGES:
    if n.startswith("hub-"):
        ROUTES[f"/preparedness/{n[4:]}/"] = n
for s in lib.articles:
    ROUTES[lib.url_path(s)] = s
u = lambda n: (PREV / f"{n}.html").as_uri()
R = {"pages": PAGES, "widths": WIDTHS, "layout": {}, "axe": {}, "keyboard": {}, "nojs": {}, "print": {}, "links": {}, "motion": {}, "dom": {}}
t0 = time.time()

DOM = """() => { const pa = document.querySelector('.pa'); const o = {};
 o.h1 = document.querySelectorAll('h1').length;
 const hs = [...document.querySelectorAll('.pa h1,.pa h2,.pa h3,.pa h4')].map(h => +h.tagName[1]); let j = 0; for (let i = 1; i < hs.length; i++) if (hs[i] > hs[i-1] + 1) j++; o.headingJumps = j;
 const ids = [...document.querySelectorAll('[id]')].map(e => e.id); o.dupIds = ids.filter((x, i) => ids.indexOf(x) !== i).length;
 o.imgNoAlt = [...document.querySelectorAll('img')].filter(i => !i.getAttribute('alt')).length; o.imgs = document.querySelectorAll('img').length;
 o.tables = [...document.querySelectorAll('table')].map(t => !!t.querySelector('caption') && !!t.closest('.pa-tablewrap') && t.closest('.pa-tablewrap').getAttribute('tabindex') === '0');
 const cites = [...document.querySelectorAll('a[href^="#src-"]')]; o.brokenCites = cites.filter(a => !document.getElementById(a.getAttribute('href').slice(1))).length;
 const srcs = [...document.querySelectorAll('li[id^="src-"]')].map(l => l.id); o.unreferencedSources = srcs.filter(id => !cites.some(a => a.getAttribute('href') === '#' + id)).length;
 o.extNoRel = [...document.querySelectorAll('a[href^="http"]')].filter(a => !/noopener/.test(a.rel)).length;
 const hashes = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href')).filter(h => h.length > 1); o.brokenHashes = hashes.filter(h => !document.getElementById(h.slice(1))).length;
 o.jsonld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { JSON.parse(s.textContent); return true; } catch (e) { return false; } });
 o.draftMarker = /Draft: not public/.test(pa ? pa.innerText : ''); o.internal = [...document.querySelectorAll('a[href^="/"]')].map(a => a.getAttribute('href'));
 o.noscript = !!document.querySelector('noscript'); o.dom = document.querySelectorAll('*').length; return o; }"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    for n in PAGES:
        lay = {}
        for w in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:100])); pg.on("console", lambda m: errs.append(m.text[:100]) if m.type == "error" else None)
            pg.goto(u(n))
            lay[w] = {"overflow_px": pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"), "errors": errs[:2]}
            if w == 1440:
                R["dom"][n] = pg.evaluate(DOM)
            ctx.close()
        R["layout"][n] = lay
    print("layout", round(time.time() - t0), flush=True)
    AX = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
    for n in PAGES:
        for w in (390, 1024, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); pg.goto(u(n)); pg.add_script_tag(url=AXE)
            R["axe"][f"{n}@{w}"] = pg.evaluate("async (t) => { const r = await axe.run(document, {runOnly: {type: 'tag', values: t}}); return {v: r.violations.map(x => [x.id, x.impact, x.nodes.length]), inc: r.incomplete.map(x => x.id)}; }", AX)
            ctx.close()
    print("axe", round(time.time() - t0), flush=True)
    for n in PAGES:
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); pg.goto(u(n)); stops = []
        for _ in range(10):
            pg.keyboard.press("Tab")
            stops.append(pg.evaluate("() => { const e = document.activeElement; if (!e || e === document.body) return null; const cs = getComputedStyle(e); return {t: e.tagName, ok: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== 'none'}; }"))
        pg.goto(u(n)); pg.keyboard.press("Tab"); pg.keyboard.press("Enter")
        R["keyboard"][n] = {"first_is_skip": bool(stops[0]) and stops[0]["t"] == "A", "no_visible_focus": sum(1 for s in stops if s and not s["ok"]), "skip_hash": pg.evaluate("location.hash")}
        ctx.close()
        c1 = b.new_context(viewport={"width": 1280, "height": 900}); c2 = b.new_context(viewport={"width": 1280, "height": 900}, java_script_enabled=False)
        a, z = c1.new_page(), c2.new_page(); a.goto(u(n)); z.goto(u(n))
        la, lz = a.evaluate("document.querySelector('.pa').innerText.length"), z.evaluate("document.querySelector('.pa').innerText.length")
        R["nojs"][n] = {"js": la, "nojs": lz, "same": abs(la - lz) < 40}
        c1.close(); c2.close()
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page(); pg.goto(u(n)); pg.emulate_media(media="print")
        info = pg.evaluate("() => ({bg: getComputedStyle(document.querySelector('.pa')).backgroundColor, toc: document.querySelector('.pa-toc') ? getComputedStyle(document.querySelector('.pa-toc')).display : null})")
        txt = " ".join(x.get_text() for x in fitz.open(stream=pg.pdf(format="Letter"), filetype="pdf")); doc = fitz.open(stream=pg.pdf(format="Letter"), filetype="pdf")
        info.update(pages=doc.page_count, has_sources=("Sources and verification" in txt) if not n.startswith("hub-") and n != "landing" else None); R["print"][n] = info; ctx.close()
    print("keyboard/nojs/print", round(time.time() - t0), flush=True)
    ctx = b.new_context(reduced_motion="reduce"); pg = ctx.new_page(); pg.goto(u("landing"))
    R["motion"] = {"reduce": pg.evaluate("getComputedStyle(document.querySelector('.pa-card')).transitionDuration")}; ctx.close()
    ctx = b.new_context(); pg = ctx.new_page(); pg.goto(u("landing")); R["motion"]["normal"] = pg.evaluate("getComputedStyle(document.querySelector('.pa-card')).transitionDuration"); ctx.close()
    # action box position on phones (QA-F1 regression)
    pos = {}
    for n in PAGES:
        if n.startswith("hub-") or n == "landing":
            continue
        for w, h in ((390, 844), (360, 740)):
            ctx = b.new_context(viewport={"width": w, "height": h}); pg = ctx.new_page(); pg.goto(u(n))
            pos.setdefault(f"{w}x{h}", {})[n] = pg.evaluate("() => { const e = document.querySelector('.pa-act'); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null; }"); ctx.close()
    R["action_box_top"] = pos
    b.close()
# links
unres = {}
for n, d in R["dom"].items():
    for h in d["internal"]:
        path = h.split("#")[0]
        if path.startswith("/preparedness") and path not in ROUTES:
            unres.setdefault(path, set()).add(n)
R["links"] = {"archive_unresolved": {k: sorted(v) for k, v in unres.items()}, "distinct_internal": len({h.split("#")[0] for d in R["dom"].values() for h in d["internal"]})}
for d in R["dom"].values():
    d.pop("internal", None)
(OUT / "RC-QA-RESULTS.json").write_text(json.dumps(R, indent=1), encoding="utf-8", newline="\n")
import statistics
lay_bad = [(n, w, v["overflow_px"]) for n, ws in R["layout"].items() for w, v in ws.items() if v["overflow_px"] > 0]
err = [(n, w) for n, ws in R["layout"].items() for w, v in ws.items() if v["errors"]]
axv = {k: v["v"] for k, v in R["axe"].items() if v["v"]}
print("PAGES", len(PAGES), "| overflow combos:", len(lay_bad), lay_bad[:6], "| console errors:", len(err))
print("axe runs", len(R["axe"]), "violations:", len(axv), list(axv.items())[:4])
print("h1!=1:", [n for n, d in R["dom"].items() if d["h1"] != 1], "| heading jumps:", sum(d["headingJumps"] for d in R["dom"].values()), "| dup ids:", sum(d["dupIds"] for d in R["dom"].values()), "| broken cites:", sum(d["brokenCites"] for d in R["dom"].values()), "| unreferenced sources:", sum(d["unreferencedSources"] for d in R["dom"].values()), "| broken hashes:", sum(d["brokenHashes"] for d in R["dom"].values()))
print("tables not wrapped/captioned:", sum(1 for d in R["dom"].values() for t in d["tables"] if not t), "of", sum(len(d["tables"]) for d in R["dom"].values()), "| ext links w/o noopener:", sum(d["extNoRel"] for d in R["dom"].values()), "| jsonld bad:", sum(1 for d in R["dom"].values() for j in d["jsonld"] if not j))
print("keyboard: skip-first", sum(1 for k in R["keyboard"].values() if k["first_is_skip"]), "/", len(PAGES), "| stops w/o focus:", sum(k["no_visible_focus"] for k in R["keyboard"].values()))
print("no-JS content differs:", [n for n, v in R["nojs"].items() if not v["same"]], "| print: toc not hidden:", [n for n, v in R["print"].items() if v["toc"] not in (None, "none")], "| no sources in print:", [n for n, v in R["print"].items() if v["has_sources"] is False], "| pdf pages median/max:", statistics.median(v["pages"] for v in R["print"].values()), max(v["pages"] for v in R["print"].values()))
print("motion:", R["motion"], "| archive links unresolved:", R["links"]["archive_unresolved"])
for k, v in R["action_box_top"].items():
    vals = [x for x in v.values() if x is not None]; h = int(k.split("x")[1])
    print("action box", k, "median", int(statistics.median(vals)), "max", max(vals), "| first screen:", sum(1 for x in vals if x < h), "/", len(vals), "| missing box:", [n for n, x in v.items() if x is None])
print("done", round(time.time() - t0), "s")
