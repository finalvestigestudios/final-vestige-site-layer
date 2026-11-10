#!/usr/bin/env python3
"""R263: ACTUAL R224+R262 PHP function code in an offline WP hook simulation.

The browser uses Playwright set_content because local HTTP navigation is blocked by
ERR_BLOCKED_BY_ADMINISTRATOR. Genuine WordPress/Assembler, HTTP/CSP, axe and
field CWV acceptance remain release blockers. No network or production writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ORIGINAL_FIXTURE_MANIFEST_SHA = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
R262_EXPECTED_GIT_BLOBS = {
    'fv-apollo-staging-overlay.php': 'e6406fea01435d51817edcc20d69b9b3808505ac',
    'qa/integration_acceptance.py': 'dbf311a8f39fa4bd687a8cbacb8ce7e2ae448fb9',
    'qa/wp-hook-mock.php': 'a0c70c40d6f6fe37cd4deba3df9e0122ebd781c0',
    'assets/source-drawer-focus.js': '2c196dbb733345e6e51a27af2d2894ca4461a2c9',
    'integrity.json': '4dd45c5fc2fb35d93d702c079f83528b85c937c2',
}
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MODES = ('direct','synced','absent','admin','non_singular','late','duplicate',
         'corrupt_base_css','corrupt_base_fragment','corrupt_overlay_css','corrupt_overlay_js')


def digest(b): return hashlib.sha256(b).hexdigest()
def gitblob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def check(v, reason):
    if not v: raise AssertionError(reason)


def run_php(test_file, fixture, r262, mode):
    completed = subprocess.run(['php', str(test_file),
       str(fixture / 'fv-ex2-apollo-r224.php'),str(r262 / 'fv-apollo-staging-overlay.php'),mode],
       check=True,capture_output=True,text=True, timeout=8)
    return json.loads(completed.stdout)


def main(args):
    fixture, r262, out = args.fixture.resolve(), args.r262.resolve(),args.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    check(digest((fixture/'manifest.json').read_bytes())==ORIGINAL_FIXTURE_MANIFEST_SHA,
          'protected original Atlas manifest mismatch')
    for f,h in json.loads((fixture/'manifest.json').read_text())['files'].items():
        check(digest((fixture/f).read_bytes())==h,'protected fixture drift: '+f)
    for f,h in R262_EXPECTED_GIT_BLOBS.items():
        check(gitblob((r262/f).read_bytes())==h,'R262 actual GitHub source drift: '+f)
    for f,h in json.loads((r262/'integrity.json').read_text())['generated_asset_sha256'].items():
        check(digest((r262/'assets'/f).read_bytes())==h,'R262 generated asset drift: '+f)
    test_file=Path(__file__).with_name('wp-real-source-sequence.php').resolve()
    cases=[]
    with tempfile.TemporaryDirectory(prefix='fv-r263-source-tests-') as tmp:
        for mode in MODES:
            # Every mode runs isolated with copies of the intact, SHA-verified sources;
            # faults never touch the canonical source or another test scenario.
            base=Path(tmp)/mode/'base';over=Path(tmp)/mode/'overlay'
            shutil.copytree(fixture,base);shutil.copytree(r262,over)
            mutated=None
            if mode.startswith('corrupt_'):
                target={
                   'corrupt_base_css': base/'assets/atlas-scoped.css',
                   'corrupt_base_fragment': base/'templates/atlas-fragment.html',
                   'corrupt_overlay_css': over/'assets/apollo-overlays.css',
                   'corrupt_overlay_js': over/'assets/source-drawer-focus.js'
                }[mode]
                with target.open('ab') as f: f.write(b'\nR263_NEGATIVE_CONTROL_NON_SHIP')
                mutated=target.name
            result=run_php(test_file,base,over,mode)
            hooks=result['hooks']
            check(hooks==[['fv_ex2_r224_preflight',20],['fv_apollo_r262_enqueue',25]],
                  'WordPress hook ordering '+mode)
            base_style='fv-apollo-r224' in result['styles']
            overlay_style='fv-apollo-r262-overlays' in result['styles']
            overlay_js='fv-apollo-r262-drawer-focus' in result['scripts']
            expect_base=mode in ('direct','synced','duplicate','corrupt_overlay_css','corrupt_overlay_js')
            expect_overlay=mode in ('direct','synced','duplicate')
            check(base_style==expect_base and overlay_style==expect_overlay and overlay_js==expect_overlay,
                  'exact-style and script loading gate '+mode)
            if expect_overlay:
                check(result['styles']['fv-apollo-r262-overlays']['deps']==['fv-apollo-r224'],
                      'source CSS dependency '+mode)
                check(result['scripts']['fv-apollo-r262-drawer-focus']['in_footer'] is True,
                      'nonblocking JS footer '+mode)
            if expect_base:
                check(result['atlas_present'] and not result['fallback'],'protected Atlas rendered '+mode)
                check(result['html_sha256']=='50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6',
                      'original bytes preserved '+mode)
            elif mode in ('absent','admin','non_singular'):
                check(not result['render_invoked'] and not result['atlas_present'] and not result['fallback'],
                      'no shortcode render on ineligible page '+mode)
            else:
                check(result['render_invoked'] and not result['atlas_present'] and result['fallback'],
                      'fail open to investigation '+mode)
            if mode=='duplicate':
                check(result['second_fallback'] and not result['second_atlas'],'duplicate IDs prevented')
            cases.append({'scenario':mode,'pass':True,'base_enqueued':base_style,
                          'overlay_css_enqueued':overlay_style,'overlay_js_enqueued':overlay_js,
                          'fallback':result['fallback'],'negative_corruption':mutated})
    # Separate actual browser behavior: only original PHP output, not a synthetic replica.
    original=run_php(test_file,fixture,r262,'direct')
    check(original['html'] is not None,'PHP output unavailable')
    cssbase=(fixture/'assets/atlas-scoped.css').read_text()
    cssover=(r262/'assets/apollo-overlays.css').read_text()
    js=(r262/'assets/source-drawer-focus.js').read_text()
    html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<style>'+cssbase+'\n'+cssover+'</style></head><body>'+original['html']+'</body></html>')
    browser=[];screenshots={};perf_notes=[]
    with sync_playwright() as playwright:
        b=playwright.chromium.launch(executable_path=args.chromium,args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for enabled in (False,True):
                ctx=b.new_context(viewport={'width':width,'height':900}, java_script_enabled=enabled,
                       is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                page=ctx.new_page();requests=[]
                page.on('request',lambda request: requests.append(request.url))
                page.set_content(html,wait_until='load')
                if enabled:page.add_script_tag(content=js)
                check(page.locator('a[href^="https://www.nasa.gov/"]').count()==55,'NASA links '+str(width))
                check(page.locator('a[href^="#"]').count()==31,'native navigation '+str(width))
                check(page.locator('a[href="'+FREE+'"]').count()==1,'only original investigation '+str(width))
                destination=page.locator('a[href="#fv-apollo-source-drawer"]')
                destination.focus();destination.press('Enter');page.wait_for_timeout(45)
                state=page.evaluate("""() => {
                  const d=document.querySelector('#fv-apollo-source-drawer');
                  return {hash:location.hash, open:d.open,
                   focus:document.activeElement===d.querySelector('summary'),
                   overflow:document.documentElement.scrollWidth>innerWidth+1}; }""")
                check(state['hash']=='#fv-apollo-source-drawer' and not state['overflow'],
                      'navigation/reflow '+str(width))
                check(not requests,'unexpected remote resource '+str(width))
                if enabled:
                    check(state['open'] and state['focus'],'focus continuity '+str(width))
                else:
                    check(not state['open'],'no-JS native preserved '+str(width))
                    s=page.locator('#fv-apollo-source-drawer summary');s.focus();s.press('Enter')
                    check(page.locator('#fv-apollo-source-drawer').evaluate('(d)=>d.open'),
                          'no-JS disclosure keyboard '+str(width))
                if width in (390,1440):
                    name=f'{width}-'+('js' if enabled else 'nojs')+'.png'
                    shot=page.screenshot(animations='disabled');(out/name).write_bytes(shot)
                    screenshots[name]=digest(shot)
                browser.append({'width':width,'js':enabled,'pass':True})
                ctx.close()
        ctx=b.new_context(viewport={'width':390,'height':900},forced_colors='active',reduced_motion='reduce')
        page=ctx.new_page();page.set_content(html);page.add_script_tag(content=js)
        page.locator('a[href="#fv-apollo-source-drawer"]').click();page.wait_for_timeout(45)
        check(page.locator('#fv-apollo-source-drawer summary').evaluate('(e)=>e===document.activeElement'),
              'forced color focus');ctx.close()
        browser.append({'forced_colors':True,'pass':True})
        b.close()
    report={'original_manifest_sha256':ORIGINAL_FIXTURE_MANIFEST_SHA,
            'original_php_sha256':digest(original['html'].encode()),
            'r262_source_git_blobs':R262_EXPECTED_GIT_BLOBS,
            'php_scenarios':cases,'chromium_contexts':browser,'screenshots':screenshots,
            'axe_core':'NOT EXECUTED; vendor bundle unavailable',
            'installed_wordpress':'NOT EXECUTED; real source PHP under offline simulated WP functions',
            'actual_http_csp':'BLOCKED_BY_ADMINISTRATOR for localhost page.goto',
            'lcp_cls':'NOT ACCEPTED: set_content cannot establish production navigation Core Web Vitals',
            'production':'UNCHANGED; staging hold'}
    report['receipt_sha256']=digest(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    (out/'receipt.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'pass':True,'php_scenarios':len(cases),
          'browser_contexts':len(browser),'receipt_sha256':report['receipt_sha256']},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--fixture',type=Path,required=True)
    p.add_argument('--r262',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--chromium',default='/usr/bin/chromium')
    main(p.parse_args())
