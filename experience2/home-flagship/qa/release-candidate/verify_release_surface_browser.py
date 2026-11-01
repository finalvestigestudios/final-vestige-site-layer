#!/usr/bin/env python3
"""Actual seven-chapter release-output Chromium QA, source-verified and OFFLINE.

Never invokes WordPress, never touches production, and does not certify hosted CSP,
Axe/WCAG, field CWV, archival media transfer or rights. This exercises the exact
source-pinned release builder output with the committed stylesheet/JS bytes.
"""
import argparse
import hashlib
import html as html_module
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]  # home-flagship
SIZES = [320,360,390,768,1024,1440,1920]
SCRIPTS = ['flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js']
STYLES = ['flagship.css','chronicle.css','chronicle-lens.css','inquiry.css','observer-lab.css','reading-trail.css']
NONCE = 'fv-ex2-static-browser-qa'

def sha256(raw): return hashlib.sha256(raw).hexdigest()
def check(condition, reason):
    if not condition: raise AssertionError(reason)

def create_page(bundle):
    manifest = json.loads((bundle/'SOURCE_MANIFEST.json').read_text())
    for filename, record in manifest['files'].items():
        raw = (bundle/filename).read_bytes()
        check(len(raw)==record['bytes'] and sha256(raw)==record['sha256'], f'source seal drift: {filename}')
    source=(bundle/'index.release-review.html').read_text(encoding='utf8')
    for css in STYLES:
        link=f'<link rel="stylesheet" href="./{css}">'
        check(source.count(link)==1, f'CSS source link count: {css}')
        original=(bundle/css).read_text(encoding='utf8')
        check('</style' not in original.lower(), f'unsafe closing style: {css}')
        source=source.replace(link,f'<style nonce="{NONCE}" data-fv-exact-asset="{css}">\n{original}\n</style>')
    scripts=[]
    for js in SCRIPTS:
        tag=f'<script src="./{js}" defer></script>'
        check(source.count(tag)==1, f'JS source tag count: {js}')
        source=source.replace(tag,'')
        original=(bundle/js).read_text(encoding='utf8')
        check('</script' not in original.lower(),f'unsafe closing script: {js}')
        scripts.append(f'<script nonce="{NONCE}" data-fv-exact-asset="{js}">\n{original}\n</script>')
    csp=f"default-src 'none'; img-src 'none'; style-src 'nonce-{NONCE}'; script-src 'nonce-{NONCE}'; object-src 'none'; connect-src 'none'; base-uri 'none'"
    source=source.replace('</head>',f'<meta http-equiv="Content-Security-Policy" content="{html_module.escape(csp,quote=True)}">\n</head>')
    source=source.replace('</body>', '\n'.join(scripts)+'\n</body>')
    check(source.count('data-fv-exact-asset=')==10,'all 10 original assets present')
    return source,manifest

def browser_test(html, outdir, chromium):
    results=[]
    def plain_page(w,javascript=True,source=None):
        context=chromium.new_context(viewport={'width':w,'height':900},device_scale_factor=1,
            reduced_motion='reduce',java_script_enabled=javascript)
        page=context.new_page()
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        # All images are intentionally denied by our offline CSP, not loaded from a remote website.
        page.set_content(source if source is not None else html,wait_until='load',timeout=15000)
        page.wait_for_timeout(80)
        return context,page,errors
    for width in SIZES:
        context,page,errors=plain_page(width)
        try:
            check(page.locator('[data-fv-home-flagship]').count()==1,f'{width}: root missing')
            check(page.locator('.fv-hf__chapter-nav a').count()==7,f'{width}: chapter-nav count')
            check(page.locator('[data-fv-case-button]').count()==3,f'{width}: case-button count')
            overflow=page.evaluate('({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
            check(overflow['sw']<=overflow['cw']+1,f'{width}: horizontal overflow {overflow}')
            check(not errors,f'{width}: page errors {errors}')
            check(page.locator('[data-fv-case-buttons]').is_visible(),f'{width}: case controls not enhanced')
            check(page.locator('[data-fv-chronicle-lens]').is_visible(),f'{width}: reading lens hidden')
            check(page.locator('[data-fv-observer-controls]').is_visible(),f'{width}: observer controls hidden')
            check(page.locator('.fv-hf__chapter-nav').get_attribute('data-fv-trail-enhanced') is not None,f'{width}: reading trail missing')
            page.screenshot(path=str(outdir/f'first-screen-{width}.png'))
            if width in (320,390,768,1440,1920):
                page.screenshot(path=str(outdir/f'full-page-{width}.png'),full_page=True)
            results.append({'width':width,'overflow':overflow,'enhancements':4,'script_errors':len(errors),'passed':True})
        finally: context.close()

    context,page,errors=plain_page(390)
    try:
        # Real interactions against actual committed JS, not a synthetic JS stub.
        page.locator('[data-fv-case-button="franklin"]').click()
        check(page.locator('[data-fv-case="franklin"]').is_visible(),'case chooser failed franklin')
        check(page.locator('[data-fv-case="apollo"]').is_hidden(),'case chooser failed hide apollo')
        check(page.locator('[data-fv-case-button="franklin"]').get_attribute('aria-pressed')=='true','case aria state')
        case='PASS'
        page.locator('[data-fv-chronicle-view="original"]').click()
        check(page.locator('.fv-hf__chronicle').get_attribute('data-fv-chronicle-mode')=='original','chronicle lens failed')
        chronicle='PASS'
        page.locator('[data-fv-observer-switch="b"]').click()
        check(page.locator('[data-fv-observer-frame="b"]').is_visible(),'observer frame B invisible')
        check('lower-right' not in page.locator('[data-fv-observer-status]').inner_text(),'observer reveals answer')
        observer='PASS'
        # Click a link and verify the browser-native fragment and programmatic focus semantics.
        link=page.locator('.fv-hf__chapter-nav a[href="#fv-hf-inquiry"]')
        link.focus();link.press('Enter');page.wait_for_timeout(120)
        check(page.evaluate('location.hash')=='#fv-hf-inquiry','chapter anchor navigation failed')
        check(page.evaluate('document.activeElement.id')=='fv-hf-inquiry','keyboard target focus missing')
        trail='PASS'
        check(not errors,f'interaction errors {errors}')
    finally: context.close()

    context,page,errors=plain_page(390,False)
    try:
        check(page.locator('[data-fv-case]').count()==3,'no-JS cases missing')
        check(all(page.locator(f'[data-fv-case="{x}"]').is_visible() for x in ('apollo','franklin','malbone')),'no-JS cases hidden')
        check(page.locator('[data-fv-case-buttons]').is_hidden(),'no-JS controls incorrectly visible')
        check(page.locator('[data-fv-observer-frame]').count()==2,'no-JS observer missing')
        check(all(page.locator(f'[data-fv-observer-frame="{x}"]').is_visible() for x in ('a','b')),'no-JS observer concealed')
        check(not errors,f'no-JS errors {errors}')
    finally: context.close()

    # Three negative CSP tests use the same actual HTML, appending injected scripts.
    # They verify Browser CSP policy in set_content (NOT a hosted HTTP CSP header).
    csp_checks=[]
    for label,malicious in [
        ('unnonced_inline','<script>window.fvCspInjected=1;</script>'),
        ('wrong_nonce','<script nonce="wrong">window.fvCspInjected=1;</script>'),
        ('inline_event','<img id="fv-injected" src="x" onerror="window.fvCspInjected=1">')
    ]:
        modified=html.replace('</body>',malicious+'</body>')
        context,page,errors=plain_page(390,source=modified)
        try:
            page.wait_for_timeout(50)
            check(page.evaluate('window.fvCspInjected===undefined'),f'CSP negative failed: {label}')
            csp_checks.append(label)
        finally:context.close()

    context,page,errors=plain_page(390)
    try:
        page.evaluate('document.documentElement.style.zoom="200%"')
        overflow=page.evaluate('({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
        check(overflow['sw']<=overflow['cw']+1,f'CSS 200% zoom overflow {overflow}')
        page.screenshot(path=str(outdir/'css-zoom-200-390.png'))
    finally:context.close()
    return {'widths':results,'interactions':{'case':case,'chronicle':chronicle,'observer':observer,'keyboard_trail':trail},
            'no_js':'PASS','csp_negative':csp_checks,'zoom_css_200':'PASS',
            'limitations':['NO real WordPress/Assembler runtime','NO remote archival image fetch/rights','NO Axe/WCAG','NO Lighthouse/field CWV','NO HTTP CSP or cookies','NO Safari/AT']}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fv-ex2-release-review-') as temp:
        bundle=Path(temp)/'release';cmd=['node',str(HERE/'build_release_review.cjs'),'--out-dir',str(bundle)]
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        html,manifest=create_page(bundle)
        with sync_playwright() as p:
            chromium_bin = os.getenv('FV_CHROMIUM_EXECUTABLE') or shutil.which('chromium') or shutil.which('chromium-browser')
            launch_args = {'headless': True, 'args': ['--no-sandbox']}
            if chromium_bin: launch_args['executable_path'] = chromium_bin
            chromium=p.chromium.launch(**launch_args)
            try: results=browser_test(html,args.output_dir,chromium)
            finally:chromium.close()
    receipt={'status':'OFFLINE_BROWSER_REVIEW_ONLY','sourceGitBlob':manifest['sourceGitBlob'],'source_sha256':manifest['sourceSha256'],
             'assetGitBlobs':manifest['assetGitBlobs'],'browser':results}
    (args.output_dir/'RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
    print(json.dumps({'status':receipt['status'],'widths':len(results['widths']),'interactions':results['interactions'],
                      'csp_negative':len(results['csp_negative'])},indent=2))

if __name__=='__main__':
    from playwright.sync_api import sync_playwright
    main()
