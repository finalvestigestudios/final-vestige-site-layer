"""Optional actual local Chromium fixture QA. Never accesses or modifies finalvestige.com.
Run: python test_browser_margin.py
Requires playwright Python and Chromium. All URLs are local data documents.
"""
from __future__ import annotations

import pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
CANDIDATE = (HERE / 'margin_strip_candidate.css').read_text()
BASE = """
html, body {padding:0; margin:0; background:#0f100f; color:#d8d2c7;}
.fv-margin-strip--rotator {background:#0f100f; color:#d8d2c7;overflow:hidden;}
.fv-margin-strip__inner {display:grid;grid-template-columns: auto minmax(0,1fr);gap:18px;padding:10px 18px;align-items:center;}
.fv-margin-strip__label {color:#b8955e;font-size:10px;font-weight:800;white-space:nowrap;}
.fv-margin-strip__window {position:relative;min-height:76px;overflow:hidden;}
.fv-margin-strip__item {position:absolute;left:18px;right:0;top:50%;opacity:0;
color:#d8d2c7;font-size:13px;line-height:1.35;white-space:normal;animation: fvMarginReveal 360s linear infinite;
animation-delay:calc(var(--i) * 5s);}
@keyframes fvMarginReveal {
0% {opacity:0;filter:blur(8px)} .22%{opacity:.46;filter:blur(5px)}
.42% {opacity:1;filter:blur(0)} 1.08% {opacity:1;filter:blur(0)}
1.25% {opacity:.42;filter:blur(4px)} 1.39% {opacity:0;filter:blur(8px)}
100% {opacity:0;filter:blur(8px)}
}
@media(max-width:900px){.fv-margin-strip__inner{grid-template-columns:1fr;gap:7px;}}
"""
ITEMS = '\n'.join(f'<span class="fv-margin-strip__item" style="--i:{i}">Archive record fragment {i+1}: Read its source and limits.</span>' for i in range(72))
HTML = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<style>{BASE}\n{CANDIDATE}</style><div class="fv-margin-strip fv-margin-strip--rotator">'
        '<div class="fv-margin-strip__inner"><div class="fv-margin-strip__label">Hidden in the Margins</div>'
        f'<div class="fv-margin-strip__window" tabindex="0" aria-live="off">{ITEMS}</div></div></div>')


def run() -> None:
    passed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in (320, 390, 1440):
            context = browser.new_context(viewport={'width':width, 'height':850}, reduced_motion='no-preference')
            page = context.new_page()
            page.set_content(HTML)
            assert page.locator('.fv-margin-strip__item').count() == 72
            for t in (0, 100, 400, 800, 1200, 2500, 4800, 4970, 4990, 5010, 5200):
                state = page.evaluate('''ms => {
                  const els = [...document.querySelectorAll('.fv-margin-strip__item')];
                  for(const el of els) for(const animation of el.getAnimations()) {animation.pause();animation.currentTime=ms;}
                  return els.map(el=>{const s=getComputedStyle(el);return {opacity:+s.opacity,visibility:s.visibility,filter:s.filter,display:s.display}});
                }''', t)
                for s in state:
                    if s['visibility'] == 'visible' and s['display']!='none':
                        assert s['opacity'] == 1.0, (width,t,s)
                        assert s['filter'] == 'none', (width,t,s)
                    else:
                        assert s['opacity'] == 0 or s['display']=='none', (width,t,s)
                passed += 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            context.close()
            context = browser.new_context(viewport={'width':width, 'height':850}, reduced_motion='reduce', java_script_enabled=False)
            page = context.new_page()
            page.set_content(HTML)
            assert page.locator('.fv-margin-strip__item:visible').count() == 1
            assert page.locator('.fv-margin-strip__item').count() == 72
            assert page.locator('.fv-margin-strip__item').first.is_visible()
            passed += 1
            context.close()
        browser.close()
    print(f'LOCAL FIXTURE CHROMIUM PASS: {passed} checkpoints across 320/390/1440, plus 3 reduced-motion no-JS checks')

if __name__=='__main__':
    run()
