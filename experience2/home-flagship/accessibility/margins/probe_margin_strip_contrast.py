#!/usr/bin/env python3
"""Offline, source-inspected 72-slot page-6 Margins contrast experiment.

Local synthetic text only; no production requests, authentication or CMS writes.
Not an axe run, full homepage browser audit, or WCAG certification.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

CSS = Path(__file__).with_name("margin_strip_contrast_safe.css")
WIDTHS = (320, 390, 768, 1440, 1920)
PHASES = (0.5, 0.74, 2.5, 4.6, 5.5, 9.6, 355.5, 359.5, 360.5, 715.5)

# First Gutenberg HTML block of published WP page 6, inspected Nov 2, 2026.
# This captures the original animation and contrast-affecting properties,
# not the entire source-controlled experience or a complete host rendering.
BASE_CSS = """
.fv-margin-strip{background:#0f100f;border-top:1px solid #2a2927;border-bottom:1px solid #2a2927;color:#d8d2c7;overflow:hidden}
.fv-margin-strip__inner{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:18px;max-width:1440px;margin:0 auto;padding:10px clamp(18px,4vw,44px)}
.fv-margin-strip__label{white-space:nowrap;color:#b8955e;font-size:10px;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.fv-margin-strip__window{position:relative;min-height:46px;overflow:hidden;padding-left:18px;border-left:1px solid #34322e}
.fv-margin-strip__window:before{content:"";position:absolute;left:8px;top:50%;width:4px;height:4px;border-radius:999px;background:#b8955e;transform:translateY(-50%);opacity:.9}
.fv-margin-strip__item{position:absolute;left:18px;right:0;top:50%;transform:translateY(-38%);opacity:0;color:#d8d2c7;font-size:13px;line-height:1.35;letter-spacing:.01em;white-space:normal;filter:blur(7px);will-change:opacity,transform,filter;animation:fvMarginReveal 360s linear infinite;animation-delay:calc(var(--i) * 5s)}
.fv-margin-strip__window:hover .fv-margin-strip__item,.fv-margin-strip__window:focus .fv-margin-strip__item,.fv-margin-strip__window:focus-within .fv-margin-strip__item{animation-play-state:paused}
.fv-margin-strip__window:focus-visible{outline:1px solid #b8955e;outline-offset:3px}
@keyframes fvMarginReveal{0%{opacity:0;filter:blur(8px);transform:translateY(-22%) scale(.99)}.22%{opacity:.46;filter:blur(5px);transform:translateY(-42%) scale(.995)}.42%{opacity:1;filter:blur(0);transform:translateY(-50%) scale(1)}1.08%{opacity:1;filter:blur(0);transform:translateY(-50%) scale(1)}1.25%{opacity:.42;filter:blur(4px);transform:translateY(-61%) scale(.998)}1.39%{opacity:0;filter:blur(8px);transform:translateY(-75%) scale(.995)}100%{opacity:0;filter:blur(8px);transform:translateY(-75%) scale(.995)}}
@media(max-width:900px){.fv-margin-strip__inner{grid-template-columns:1fr;gap:7px;padding-top:12px;padding-bottom:12px}.fv-margin-strip__label{font-size:9px}.fv-margin-strip__window{min-height:58px;padding-left:16px}.fv-margin-strip__item{left:16px;font-size:12px}}
@media(max-width:520px){.fv-margin-strip__window{min-height:76px}.fv-margin-strip__item{line-height:1.4}}
@media(prefers-reduced-motion:reduce){.fv-margin-strip__window{height:auto;min-height:0;overflow:visible}.fv-margin-strip__window:before{top:14px}.fv-margin-strip__item{position:relative;display:none;left:auto;right:auto;top:auto;transform:none;opacity:1;filter:none;animation:none;padding:2px 0 6px 16px}.fv-margin-strip__item:nth-child(1){display:block}}
"""

def fixture(corrected: bool) -> str:
    items = "".join('<span class="fv-margin-strip__item" style="--i:%d">Synthetic record %02d. This is offline test text, not a historical claim.</span>' % (i, i + 1) for i in range(72))
    extra = CSS.read_text() if corrected else ""
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>body{margin:0;background:#0f100f;font-family:Arial,sans-serif;}'
            + BASE_CSS + "\n" + extra + '</style>'
            '<div class="fv-margin-strip fv-margin-strip--rotator" role="region" '
            'aria-label="Hidden in the Margins record fragments">'
            '<div class="fv-margin-strip__inner"><div class="fv-margin-strip__label">'
            'Hidden in the Margins</div><div class="fv-margin-strip__window" '
            'tabindex="0" aria-live="off" aria-label="Rotating source and accountability notes">'
            + items + '</div></div></div></html>')

OBSERVE = """(t) => {
 const items = [...document.querySelectorAll('.fv-margin-strip__item')];
 if (t !== null) items.forEach((el,i) => {
   el.style.animationDelay = (i * 5 - t) + 's';
 });
 const background = getComputedStyle(document.querySelector('.fv-margin-strip')).backgroundColor;
 const states = items.map((el,i) => {
   const s = getComputedStyle(el);
   return {i, opacity:Number(s.opacity), visibility:s.visibility, filter:s.filter, color:s.color};
 });
 return {background,states,overflow:document.documentElement.scrollWidth>innerWidth+2};
}"""

def rgb(value: str):
    nums = re.findall(r"[\d.]+", value)
    if len(nums) < 3: raise ValueError("INVALID_RGB")
    return [float(x) for x in nums[:3]]

def luminance(values):
    def linear(v):
        v /= 255.0
        return v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4
    return sum(a*linear(v) for a,v in zip((0.2126,0.7152,0.0722),values))

def contrast(foreground,background,opacity=1):
    fg,bg=rgb(foreground),rgb(background)
    mixed=[opacity*x+(1-opacity)*y for x,y in zip(fg,bg)]
    hi,lo=sorted((luminance(mixed),luminance(bg)),reverse=True)
    return (hi+0.05)/(lo+0.05)

def browser_probe(screenshots: str | None = None) -> dict:
    from playwright.sync_api import sync_playwright
    receipt={"fixture":"Synthetic 72-slot replay of Nov 2 page-6 strip CSS",
             "hosted_document":False,"axe":False,"release_gate":"HOLD",
             "baseline":{},"candidate":[],"reduced_motion":[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(
            executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").is_file() else None,
            args=["--no-sandbox"],headless=True)
        try:
            for corrected in (False,True):
                for width in (WIDTHS if corrected else (390,)):
                    context=browser.new_context(viewport={"width":width,"height":844})
                    page=context.new_page()
                    samples=[]
                    for t in (PHASES if corrected else (0.74,)):
                        page.set_content(fixture(corrected), wait_until="domcontentloaded")
                        page.evaluate(OBSERVE,t)
                        page.wait_for_timeout(65)
                        observed=page.evaluate(OBSERVE,t)
                        visible=[s for s in observed["states"] if s["visibility"]=="visible" and s["opacity"]>0]
                        minimum=min((contrast(s["color"],observed["background"],s["opacity"])
                                     for s in visible),default=0)
                        samples.append({"phase":t,"visible_indexes":[s["i"] for s in visible],
                                        "contrast":round(minimum,3),
                                        "unblurred":all(s["filter"]=="none" for s in visible),
                                        "overflow":observed["overflow"]})
                    if screenshots and width==390:
                        Path(screenshots).mkdir(parents=True,exist_ok=True)
                        page.set_content(fixture(corrected))
                        page.evaluate(OBSERVE,2.5 if corrected else 0.74)
                        page.wait_for_timeout(65)
                        page.screenshot(path=str(Path(screenshots)/("corrected" if corrected else "baseline")+"_390.png"))
                    if corrected:
                        passed=all(s["visible_indexes"]==[int(s["phase"]//5)%72]
                                   and s["contrast"]>=4.5 and s["unblurred"] and not s["overflow"]
                                   for s in samples)
                        receipt["candidate"].append({"width":width,"passed":passed,"samples":samples})
                    else:
                        receipt["baseline"]={"contrast_issue_reproduced":samples[0]["contrast"]<4.5,
                                             "samples":samples}
                    context.close()
            for js in (True,False):
                context=browser.new_context(viewport={"width":390,"height":844},
                                            reduced_motion="reduce",java_script_enabled=js)
                page=context.new_page()
                page.set_content(fixture(True))
                observed=page.evaluate(OBSERVE,None)
                shown=[s["i"] for s in observed["states"]
                       if s["visibility"]=="visible" and s["opacity"]>0]
                receipt["reduced_motion"].append({"javascript":js,"visible_indexes":shown,
                    "passed":shown==[0] and not observed["overflow"]})
                context.close()
        finally:
            browser.close()
    receipt["candidate_passed"]=bool(receipt["baseline"].get("contrast_issue_reproduced")
        and all(x["passed"] for x in receipt["candidate"])
        and all(x["passed"] for x in receipt["reduced_motion"]))
    return receipt

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--screenshots")
    args=parser.parse_args()
    receipt=browser_probe(args.screenshots)
    Path(args.output).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"candidate_passed":receipt["candidate_passed"],
                      "tested_widths":[x["width"] for x in receipt["candidate"]],
                      "baseline_reproduced":receipt["baseline"]["contrast_issue_reproduced"],
                      "release_gate":"HOLD"}))
    if not receipt["candidate_passed"]:raise SystemExit(1)

if __name__=="__main__":
    main()
