import json, sys, statistics
from pathlib import Path
from playwright.sync_api import sync_playwright
PREV = Path(r"C:\Users\brhod\OneDrive\Desktop\Projects\_wt-r47-lf\preparedness\build\preview")
SEL = {"crumbs": ".pa-crumbs", "kicker": ".pa-kicker", "h1": ".pa-head h1", "dek": ".pa-head .pa-dek", "meta": ".pa-meta", "chips": ".pa-head .pa-chips", "printbar": ".pa-printbar", "toc": ".pa-toc", "act": ".pa-act"}
slugs = sorted(p.stem for p in PREV.glob("*.html") if not p.stem.startswith("hub-") and p.stem not in ("landing", "water-planner"))
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    for w, h in ((390, 844), (360, 740)):
        rows = []
        for s in slugs:
            ctx = b.new_context(viewport={"width": w, "height": h}); pg = ctx.new_page(); pg.goto((PREV / f"{s}.html").as_uri())
            r = pg.evaluate("""(sel) => { const o = {}; for (const [k, q] of Object.entries(sel)) { const e = document.querySelector(q); if (e) { const r = e.getBoundingClientRect(); o[k] = [Math.round(r.top + scrollY), Math.round(r.height)]; } } return o; }""", SEL)
            r["slug"] = s; rows.append(r); ctx.close()
        out[f"{w}x{h}"] = rows
    b.close()
for k, rows in out.items():
    print(k, "n =", len(rows))
    for key in SEL:
        vals = [r[key][1] for r in rows if key in r]
        tops = [r[key][0] for r in rows if key in r]
        if vals: print(f"  {key:9} height median {int(statistics.median(vals)):5} max {max(vals):5} | top median {int(statistics.median(tops)):5} max {max(tops):5} (n={len(vals)})")
    act_tops = sorted(r["act"][0] for r in rows if "act" in r)
    print("  articles without .pa-act:", [r["slug"] for r in rows if "act" not in r][:12])
json.dump(out, open(sys.argv[1], "w"), indent=1)
