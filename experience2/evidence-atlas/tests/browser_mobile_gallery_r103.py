#!/usr/bin/env python3
"""Real Chromium R103 isolated DOM tests. Local set_content avoids host/CMS access.
This is not a hosted WordPress.com test or production Core Web Vitals.
"""
import argparse
import hashlib
import os
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright


def run(pkg, out, axe=None):
    out.mkdir(parents=True, exist_ok=True)
    html = (pkg/'review/R97_SOURCE_GALLERY.html').read_text()
    css = (pkg/'review/source_gallery_r97.css').read_text()
    js = (pkg/'review/source_gallery_r97.js').read_text()
    # Inlining trusted local assets is an isolated visual harness only, not CSP acceptance.
    html = re.sub(r'<link rel="stylesheet"[^>]+>', '', html)
    html = re.sub(r'<script defer src="[^"]+"></script>', '', html)
    html = html.replace('</head>', '<style>' + css + '</style></head>')
    html = html.replace('</body>', '<script>' + js + '</script></body>')
    receipt = {'schema':'fv.apollo.r103.chromium-local.v1','release':'STAGING_HOLD',
               'hosted_or_wordpress_acceptance':False,'configurations':[], 'screenshots_sha256':{}, 'axe': []}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or None, headless=True, args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for enabled in (False,True):
                context=browser.new_context(viewport={'width':width,'height':900}, java_script_enabled=enabled,
                    reduced_motion='reduce', is_mobile=width<=390,has_touch=width<=390,
                    forced_colors='active' if width==320 else 'none')
                page=context.new_page()
                page.set_content(html, wait_until='load')
                assert page.locator('[data-card]').count()==6
                assert page.locator('img,[data-lat],[data-lon],[data-geo-edge]').count()==0
                assert page.locator('a[href^="https://www.nasa.gov/image-detail/"]').count()==6
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), width
                if enabled:
                    assert page.locator('[data-compare-controls]:visible').count()==7
                    assert page.locator('[data-jump-compare]:visible').count()==0
                    for n in ('01','02'):
                        box=page.locator('#compare-'+n)
                        (box.tap() if width<=390 else box.check())
                    assert page.locator('[data-jump-compare]:visible').count()==6
                    assert page.locator('#comparison').is_visible()
                    assert page.locator('[data-heading]').all_text_contents()==['Source 01','Source 02']
                    if width<=390:
                        region=page.locator('.compare-viewport')
                        assert region.evaluate('(e)=>e.scrollWidth>e.clientWidth'), 'not scrollable mobile'
                        region.focus()
                        page.keyboard.press('ArrowRight')
                        page.wait_for_timeout(500)
                        assert region.evaluate('(e)=>e.scrollLeft>0'), 'keyboard scroll unavailable'
                    else:
                        page.locator('.compare-jump:visible').first.click()
                        assert page.evaluate("location.hash === '#comparison'"), 'native jump failed'
                    if axe and width in (390,1440):
                        page.add_script_tag(path=str(axe))
                        a=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:r.violations.map(v=>({id:v.id,nodes:v.nodes.length})),passes:r.passes.length};}''')
                        receipt['axe'].append({'width':width, **a})
                        assert not a['violations'], 'R103 axe violations'
                    if width in (390,1440):
                        im=out/f'R103_GALLERY_{width}.png'
                        page.screenshot(path=str(im),full_page=True,animations='disabled')
                        receipt['screenshots_sha256'][im.name]=hashlib.sha256(im.read_bytes()).hexdigest()
                    reset=page.locator('#compare-reset');(reset.tap() if width<=390 else reset.click())
                    assert page.locator('[data-jump-compare]:visible').count()==0
                    assert page.locator('[data-select]:checked').count()==0
                else:
                    assert page.locator('[data-compare-controls]:visible').count()==0
                    assert page.locator('[data-card]:visible').count()==6
                receipt['configurations'].append({'width':width,'js':enabled,'passed':True,'reduced_motion':True,'forced_colors':width==320})
                context.close()
        browser.close()
    (out/'R103_LOCAL_BROWSER_QA.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--package',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--axe',type=Path)
    x=a.parse_args()
    print(json.dumps(run(x.package,x.out,x.axe),sort_keys=True))
