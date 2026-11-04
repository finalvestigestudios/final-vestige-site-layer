#!/usr/bin/env python3
"""Nonproduction source-exact first-screen Focus CTA test, not WordPress staging.

Run after checkout: python -I experience2/home-flagship/tests/verify_focus_masthead_browser.py
No external URLs are loaded, and JavaScript is disabled. Historic image transfer,
WordPress.com/Jetpack, physical browser zoom, full-page axe and field CWV are NOT covered.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

WIDTHS = (320, 360, 390, 420, 600, 720, 768, 1440, 1920)
CSS_LINK = re.compile(r'<link\\s+rel="stylesheet"\\s+href="\\./([a-z0-9._-]+\\.css)"\\s*/?>', re.I)
FOCUS = 'https://finalvestige.com/focus/'


def source_html(root):
    html = (root / 'index.html').read_text(encoding='utf-8')
    assert html.count('class="fv-hf__chapter-nav"') == 1, 'Missing seven-chapter navigation'
    assert len(re.findall(r'<a\\s+href="#fv-hf-', html)) >= 7, 'Seven chapter links missing'
    assert 'fv-hf__mast-cta' in html and FOCUS in html, 'Focus source missing'
    count = 0

    def inline(match):
        nonlocal count
        name = match.group(1)
        css = (root / name).read_text(encoding='utf-8')
        if '</style' in css.lower():
            raise ValueError('Unexpected closing style tag in '+name)
        count += 1
        return '<style data-source-css="'+name+'">\\n'+css+'\\n</style>'

    prepared = CSS_LINK.sub(inline, html)
    assert count == 6, 'Expected all six real source stylesheets; got '+str(count)
    return prepared, hashlib.sha256(html.encode()).hexdigest()


def check(root, output):
    from playwright.sync_api import sync_playwright
    html, fingerprint = source_html(root)
    output.mkdir(parents=True, exist_ok=True)
    receipts = []
    with sync_playwright() as p:
        path = os.getenv('FV_EX2_CHROMIUM') or shutil.which('chromium') or shutil.which('google-chrome')
        browser = p.chromium.launch(headless=True, executable_path=path if path else None,
                                    args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                page = browser.new_page(viewport={'width': width, 'height': 844},
                                        java_script_enabled=False, reduced_motion='reduce')
                blocked = []
                page.route('**/*', lambda route: (blocked.append(route.request.url), route.abort()))
                try:
                    page.set_content(html, wait_until='domcontentloaded', timeout=30000)
                    data = page.evaluate("""() => {
                      const c=document.querySelector('.fv-hf__mast-cta');
                      const b=c?.getBoundingClientRect(), brand=document.querySelector('.fv-hf__brand');
                      if(!b)return {found:false};
                      const x=(b.left+b.right)/2,y=(b.top+b.bottom)/2;
                      const hit=document.elementFromPoint(x,y);
                      return {found:true,href:c.getAttribute('href'),
                        width:b.width,height:b.height,top:b.top,bottom:b.bottom,
                        firstScreen:b.top>=0&&b.bottom<=innerHeight,
                        hit:!!hit&&(hit===c||c.contains(hit)),
                        brandVisible:!!brand&&brand.getBoundingClientRect().width>0,
                        overflow:document.documentElement.scrollWidth>innerWidth+1};
                    }""")
                    errors=[]
                    if not data.get('found'):
                        errors.append('missing Focus CTA')
                    else:
                        if data['href'] != FOCUS: errors.append('wrong Focus destination')
                        if data['width'] < 44 or data['height'] < 44: errors.append('touch target under 44px')
                        if not data['firstScreen']: errors.append('CTA below first screen')
                        if not data['hit']: errors.append('CTA center obstructed')
                        if not data['brandVisible']: errors.append('brand not visible')
                        if data['overflow']: errors.append('horizontal overflow')
                        page.locator('.fv-hf__mast-cta').focus()
                        if not page.evaluate("document.activeElement?.classList.contains('fv-hf__mast-cta')"):
                            errors.append('CTA cannot receive keyboard focus')
                    if width in (320, 390, 1440):
                        page.screenshot(path=str(output / f'ex2-focus-{width}.png'),
                                        animations='disabled', full_page=False)
                    receipts.append({'width':width,'results':data,'errors':errors,
                                     'remoteRequestsAborted':len(blocked),'pass':not errors})
                finally:
                    page.close()
        finally:
            browser.close()
    report={'classification':'STANDALONE_SOURCE_EXACT_NOT_WORDPRESS_STAGING',
            'sourceHtmlSha256':fingerprint,'reducedMotion':True,'javaScriptEnabled':False,
            'externalNetworkBlocked':True,'viewports':list(WIDTHS),'results':receipts,
            'pass':all(r['pass'] for r in receipts)}
    (output/'ex2-focus-masthead-receipt.json').write_text(json.dumps(report,indent=2))
    for r in receipts:
        print(r['width'], 'PASS' if r['pass'] else 'FAIL', r['results'], r['errors'])
    if not report['pass']:
        raise SystemExit('Release HOLD: standalone source Focus masthead failure')


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    out=Path(os.environ.get('FV_EX2_FOCUS_QA_OUT','/tmp/fv-ex2-focus-masthead'))
    check(root,out)
