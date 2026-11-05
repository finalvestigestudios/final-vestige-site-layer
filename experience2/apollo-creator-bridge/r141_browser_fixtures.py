#!/usr/bin/env python3
"""R141 representative DOM-only browser regression; NOT actual finalvestige.com navigation.
Uses a local in-memory test fixture, no network or NASA photo distribution.
"""
import argparse, hashlib, json, pathlib
from playwright.sync_api import sync_playwright
WIDTHS = (320, 360, 390, 768, 1440, 1920)
BASE = '''<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo CTA DOM fixture</title><style>html{background:#090a0a;color:#f4efe6;font:16px/1.55 system-ui}body{margin:0}main{margin:auto;max-width:1100px;padding:24px}a{color:#e9c58d}a:focus-visible{outline:3px solid #e9c58d;outline-offset:4px}h1{font:clamp(2rem,6vw,4rem)/1.1 Georgia,serif}article{border:1px solid #998368;padding:24px;max-width:650px}p{overflow-wrap:anywhere}</style><main><h1>Historical source custody</h1><article><p>Apollo 1 — evidence and limitations, not a NASA endorsement.</p>{cta}<p>NASA's Apollo 204 Review Board provides the technical source record.</p></article></main></html>'''
LINK = '<a id="read" href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the full investigation</a>'
def run(destination):
    destination.mkdir(parents=True, exist_ok=True)
    rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in WIDTHS:
            context=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=False, reduced_motion='reduce')
            page=context.new_page()
            page.set_content(BASE.replace("{cta}",LINK),wait_until='domcontentloaded')
            page.keyboard.press('Tab')
            focused=page.evaluate('document.activeElement && document.activeElement.id')
            link=page.locator('#read')
            visible=link.is_visible()
            outline=page.evaluate("getComputedStyle(document.querySelector('#read')).outlineWidth")
            overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
            assert focused=='read' and visible and not overflow, (width,focused,visible,overflow)
            assert float(outline.rstrip('px'))>=3,(width,outline)
            shot=destination/f'r141-fixture-cta-{width}.png'
            page.screenshot(path=str(shot),full_page=True)
            rows.append({'width':width,'fixture':'synthetic','no_js':True,'reduced_motion':True,'focused':focused,'outline':outline,'horizontal_overflow':overflow,'sha256':hashlib.sha256(shot.read_bytes()).hexdigest()})
            context.close()
        for label,cta in [('hidden_ancestor',f'<div hidden>{LINK}</div>'),('aria_hidden_ancestor',f'<div aria-hidden="true">{LINK}</div>'),('style_hidden_ancestor',f'<div style="display:none">{LINK}</div>')]:
            page=browser.new_page()
            page.set_content(BASE.replace("{cta}",cta))
            page.keyboard.press('Tab')
            focused=page.evaluate('document.activeElement && document.activeElement.id')
            visible=page.locator('#read').is_visible()
            if label=='aria_hidden_ancestor':
                # ARIA hidden may remain visibly keyboard-focusable: this is why DOM/source custody must reject it.
                assert focused=='read' and visible
            else: assert focused!='read' and not visible,(label,focused,visible)
            rows.append({'fixture':label,'focused':focused,'visible':visible,'expected_rejection':'SOURCE_GATE'})
            page.close()
        browser.close()
    evidence={'schema':'fv.apollo.r141.synthetic-browser.v1','browser':'CHROMIUM_REAL_RENDERING_WITH_PAGE_SET_CONTENT','navigation':'NOT_ATTEMPTED_ACTUAL_PAGE','axe':'NOT_EXECUTED','lcp_cls':'NOT_MEASURED_ON_ACTUAL_PAGE','sizes':rows,'release':'STAGING_HOLD'}
    (destination/'r141_fixture_browser_receipt.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='r141_artifacts');args=ap.parse_args()
    x=run(pathlib.Path(args.out));print('PASS',len(x['sizes']),'synthetic Chromium cases; actual-page navigation/axe/LCP/CLS not performed')
