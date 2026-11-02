#!/usr/bin/env python3
"""Pixel-measured text contrast for text over gradients/imagery (what axe reports as 'incomplete').

For every visible text element: read its computed colour, hide ALL text, screenshot the page, then
compare the text colour with the real background pixels under the element's box (95th-percentile
luminance for light text, 5th for dark text = the hardest pixels). WCAG 1.4.3: 4.5:1, or 3:1 for
large text (>=24px, or >=18.66px bold). Reports failures; ignores elements that are not visibly painted.

  python contrast_audit.py --url http://127.0.0.1:9400/ --out <dir> [--scope flagship|page]
"""
import argparse, io, json, re
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

JS_COLLECT = """(scope)=>{const out=[];const root=scope==='flagship'?document.querySelector('[data-fv-home-flagship]'):document.body;
const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;const seen=new Set();
while(n=w.nextNode()){const t=n.textContent.trim();if(!t)continue;const e=n.parentElement;if(seen.has(e))continue;seen.add(e);
 if(e.closest('script,style,noscript,[aria-hidden="true"],[hidden]'))continue;
 const cs=getComputedStyle(e);if(cs.visibility==='hidden'||cs.display==='none')continue;
 let op=1;for(let x=e;x&&x!==document.documentElement;x=x.parentElement){op*=parseFloat(getComputedStyle(x).opacity)}
 const r=document.createRange();r.selectNodeContents(n);const b=r.getBoundingClientRect();if(b.width<2||b.height<2)continue;
 out.push({t:t.slice(0,48),color:cs.color,fs:parseFloat(cs.fontSize),fw:parseInt(cs.fontWeight)||400,op,
   x:b.left+scrollX,y:b.top+scrollY,w:b.width,h:b.height,cls:(e.className||e.tagName).toString().slice(0,40)})}
return out}"""


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def parse(c):
    m = re.findall(r"[\d.]+", c)
    r, g, b = (float(x) for x in m[:3]); a = float(m[3]) if len(m) > 3 else 1.0
    return np.array([r, g, b]), a


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url", default="http://127.0.0.1:9400/"); ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--scope", default="flagship"); ap.add_argument("--widths", default="390,1440"); a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True); R = {}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        for w in [int(x) for x in a.widths.split(",")]:
            pg = b.new_page(viewport={"width": w, "height": 900}); pg.emulate_media(reduced_motion="reduce")
            pg.goto(a.url, wait_until="load"); pg.wait_for_timeout(1500)
            # open every details so text inside is painted and measurable
            pg.add_style_tag(content=".fv-home-shell,.fv-enter-record{content-visibility:visible!important}")
            pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            # make every case panel visible too (chooser shows one at a time)
            els = pg.evaluate(JS_COLLECT, a.scope)
            pg.add_style_tag(content="*,*::before,*::after{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important;caret-color:transparent!important} *::selection{background:transparent!important}")
            pg.wait_for_timeout(300)
            h = pg.evaluate("document.documentElement.scrollHeight")
            png = pg.screenshot(full_page=True)
            im = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"))
            fails, worst, n = [], [], 0
            for e in els:
                rgb, alpha = parse(e["color"]); alpha *= e["op"]
                if alpha < 0.05: continue
                x0, y0 = max(0, int(e["x"])), max(0, int(e["y"])); x1, y1 = min(im.shape[1], int(e["x"] + e["w"])), min(im.shape[0], int(e["y"] + e["h"]))
                if x1 - x0 < 2 or y1 - y0 < 2: continue
                px = im[y0:y1, x0:x1].reshape(-1, 3).astype(float)
                L = lum(px); tl = float(lum(rgb))
                large = e["fs"] >= 24 or (e["fs"] >= 18.66 and e["fw"] >= 700)
                need = 3.0 if large else 4.5
                # effective text colour when alpha<1 is blended over each bg pixel
                if alpha < 1: eff = lum(px * (1 - alpha) + rgb * alpha)
                else: eff = np.full_like(L, tl)
                ratio = (np.maximum(eff, L) + 0.05) / (np.minimum(eff, L) + 0.05)
                r5 = float(np.percentile(ratio, 5))   # hardest 5% of pixels
                n += 1
                if r5 < need:
                    fails.append({"text": e["t"], "cls": e["cls"], "fs": e["fs"], "ratio_p5": round(r5, 2), "need": need, "x": round(e["x"]), "y": round(e["y"])})
            R[str(w)] = {"measured": n, "failures": len(fails), "items": sorted(fails, key=lambda f: f["ratio_p5"])[:60]}
            print(w, "measured", n, "below threshold", len(fails))
            pg.close()
        b.close()
    (a.out / f"contrast_audit_{a.scope}.json").write_text(json.dumps(R, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
