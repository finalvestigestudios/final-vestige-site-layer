"""Full rendered QA of the private Preparedness Archive previews (local files, NOT the live WordPress theme)."""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

PREV = Path(r"C:\Users\brhod\OneDrive\Desktop\Projects\_wt-r47-lf\preparedness\build\preview")
OUT = Path("qa_out"); OUT.mkdir(exist_ok=True); (OUT / "shots").mkdir(exist_ok=True)
AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"
PAGES = sorted(p.stem for p in PREV.glob("*.html"))
WIDTHS = [360, 390, 768, 1440, 1920]

# map public archive paths -> preview files, so internal links can be resolved offline
def build_route_map():
    m = {"/preparedness/": "landing"}
    for p in PAGES:
        if p.startswith("hub-"): m[f"/preparedness/{p[4:]}/"] = p
    return m
ROUTES = build_route_map()
meta = {}
import sys as _s; _s.path.insert(0, r"C:\Users\brhod\OneDrive\Desktop\Projects\_wt-r47-lf\preparedness\tools")
import build
lib = build.Library()
for slug in lib.articles: ROUTES[lib.url_path(slug)] = slug

JS_CHECKS = """() => {
  const pa = document.querySelector('.pa'); const de = document.documentElement; const out = {};
  out.hOverflow = de.scrollWidth > de.clientWidth;
  const offenders = []; document.querySelectorAll('.pa *').forEach(e => { if (e.closest('.pa-tablewrap')) return; const r = e.getBoundingClientRect(); if (r.width && r.right > innerWidth + 1) offenders.push(e.tagName + '.' + (e.className||'')); });
  out.offenders = offenders.slice(0, 3);
  out.h1 = document.querySelectorAll('h1').length;
  const hs = [...document.querySelectorAll('.pa h1,.pa h2,.pa h3,.pa h4,.pa h5,.pa h6')].map(h => +h.tagName[1]);
  let jumps = 0; for (let i = 1; i < hs.length; i++) if (hs[i] > hs[i-1] + 1) jumps++; out.headingJumps = jumps; out.headings = hs.length;
  out.emptyHeadings = [...document.querySelectorAll('.pa h1,.pa h2,.pa h3')].filter(h => !h.textContent.trim()).length;
  const ids = [...document.querySelectorAll('[id]')].map(e => e.id); out.dupIds = ids.filter((x, i) => ids.indexOf(x) !== i).slice(0, 5);
  out.mains = document.querySelectorAll('main').length;
  out.imgs = document.querySelectorAll('img').length; out.imgsNoAlt = [...document.querySelectorAll('img')].filter(i => !i.getAttribute('alt')).length;
  out.nodes = document.querySelectorAll('*').length; out.height = de.scrollHeight;
  out.tables = [...document.querySelectorAll('table')].map(t => ({caption: !!t.querySelector('caption'), wrapped: !!t.closest('.pa-tablewrap'), wrapFocusable: t.closest('.pa-tablewrap') ? t.closest('.pa-tablewrap').getAttribute('tabindex') === '0' : false, wrapLabel: t.closest('.pa-tablewrap') ? !!t.closest('.pa-tablewrap').getAttribute('aria-label') : false, scrolls: t.closest('.pa-tablewrap') ? t.closest('.pa-tablewrap').scrollWidth > t.closest('.pa-tablewrap').clientWidth : false}));
  const cites = [...document.querySelectorAll('a[href^="#src-"]')]; out.citeLinks = cites.length; out.brokenCiteAnchors = cites.filter(a => !document.getElementById(a.getAttribute('href').slice(1))).length;
  const srcs = [...document.querySelectorAll('li[id^="src-"]')].map(l => l.id); out.sourceItems = srcs.length;
  out.unreferencedSources = srcs.filter(id => !cites.some(a => a.getAttribute('href') === '#' + id)).length;
  out.extLinks = [...document.querySelectorAll('a[href^="http"]')].length; out.extNoRel = [...document.querySelectorAll('a[href^="http"]')].filter(a => !/noopener/.test(a.rel)).length;
  const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')); out.internal = links.filter(h => h.startsWith('/')); out.hashes = links.filter(h => h.startsWith('#'));
  out.hashBroken = out.hashes.filter(h => h.length > 1 && !document.getElementById(h.slice(1))).length;
  out.textLen = (pa ? pa.innerText : '').length;
  out.skipLink = !!document.querySelector('.pa-skip'); out.crumbs = !!document.querySelector('nav[aria-label="Breadcrumb"]');
  out.jsonld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { JSON.parse(s.textContent); return true; } catch (e) { return false; } });
  out.draftBadge = /Draft: not public/.test(pa ? pa.innerText : '');
  return out; }"""

FOCUS = """async () => { const res = []; return res; }"""

report = {"pages": {}, "summary": {}}
t0 = time.time()
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    for name in PAGES:
        rec = {"widths": {}}
        for w in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": 900}); pg = ctx.new_page(); errs = []
            pg.on("console", lambda m: errs.append(m.text[:120]) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
            t1 = time.time(); pg.goto((PREV / f"{name}.html").as_uri(), wait_until="load"); load_ms = round((time.time() - t1) * 1000)
            r = pg.evaluate(JS_CHECKS); r["consoleErrors"] = errs[:3]; r["loadMs"] = load_ms
            if w == 360:
                # tables at the narrowest width must scroll inside their wrapper, never widen the page
                r["tableOverflowsPage"] = bool(r["hOverflow"] and any(t["wrapped"] for t in r["tables"]))
            rec["widths"][w] = r
            ctx.close()
        report["pages"][name] = rec
        print(f"{name}: widths done ({round(time.time()-t0)}s)", flush=True)
    b.close()
json.dump(report, open(OUT / "layout.json", "w"), indent=1)
print("layout pass complete", round(time.time() - t0), "s")
