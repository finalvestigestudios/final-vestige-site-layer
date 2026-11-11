#!/usr/bin/env python3
"""R280 exact renderer identity gate with old-version negative controls (offline WordPress shim).

Real PHP is executed for each original/mutated sibling file, then the resulting
HTML is loaded in real local Chromium for navigation, no-JS and print parity.
No installed WordPress, HTTP/CSP, external requests or axe-core are represented
as tested. All receipts omit clock data so reruns can be compared byte-for-byte.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
ADAPTER=ROOT/'apollo-r277/apollo-review-shortcode.php'
SOURCE=ROOT/'apollo-r273/review-custody.php'
CSS=ROOT/'apollo-r273/assets/review-custody.css'
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r280-evidence')
OUT.mkdir(parents=True,exist_ok=True)
NASA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PIN='3f3c5a01e64cbc68349dd20c3daceadb64bf8a2e68ec5a0a2ea4bb6a3eed9107'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==PIN
assert PIN in ADAPTER.read_text()
original=SOURCE.read_text()

cases={
 'reviewed_original':original,
 'misleading_review_completed':original.replace('Editorial review pending', 'Editorial review complete'),
 'misleading_nasa_endorsement':original.replace('NASA has not endorsed', 'NASA has endorsed'),
 'misleading_independent_corroboration':original.replace('not two independent source confirmations', 'two independent source confirmations'),
 'misleading_commercial_cta':original.replace('Read the free Apollo 1 investigation','Buy this exclusive Apollo 1 collection'),
 'nonreviewed_event_handler':original.replace('target="_blank"','onclick="alert(1)" target="_blank"'),
 'altered_nasa_url':original.replace(NASA,'https://not-nasa.example/'),
 'altered_review_id':original.replace('fv-r273-title','fv-r273-unsafe-title'),
 'invalid_sibling_php':original+'\nfunction bad( {\n',
 'unreviewed_one_byte_change':original+'\n',
 'missing_sibling':None,
}
assert len(cases)==11
assert len({v for v in cases.values() if v is not None})==10

harness='''<?php
error_reporting(E_ALL);
define('ABSPATH','/offline-qa-only/');
function add_action($event,$callback,$priority=10) {}
function add_shortcode($name,$callback) {}
function plugins_url($path,$file){return '/local/review-custody.css';}
function wp_style_is($style,$status){return true;}
require __DIR__.'/experience2/apollo-r277/apollo-review-shortcode.php';
echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://merchant.invalid']);
'''

def render(adapter: str, sibling: str | None) -> str:
    with tempfile.TemporaryDirectory(prefix='apollo-r280-') as dirname:
        base=Path(dirname)
        (base/'experience2/apollo-r273').mkdir(parents=True)
        (base/'experience2/apollo-r277').mkdir(parents=True)
        (base/'experience2/apollo-r277/apollo-review-shortcode.php').write_text(adapter)
        if sibling is not None:
            (base/'experience2/apollo-r273/review-custody.php').write_text(sibling)
        (base/'fixture.php').write_text(harness)
        p=subprocess.run(['php',str(base/'fixture.php')],capture_output=True,text=True,timeout=8)
        assert p.returncode==0, (p.returncode,p.stderr[-1500:])
        assert not p.stderr, p.stderr
        return p.stdout

# Negative control reconstructs the exact committed R279 adapter from this patch.
# Check its Git blob identity: no external archive, network or unpinned fixture.
current=ADAPTER.read_text()
first=current.index('/**\n * Exact reviewed staging-renderer byte identity.')
last=current.index('function fv_r277_render_shortcode(',first)
old_adapter=(current[:first]+current[last:]).replace(
    'if (!fv_r277_renderer_source_matches($source)) { return fv_r277_source_fallback(); }',
    'if (!is_readable($source)) { return fv_r277_source_fallback(); }')
blob=old_adapter.encode()
assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()=='821edd4118c44543dcf1cf3187fc2aedf289c116'

results=[]; htmls={}
for name,sibling in cases.items():
    actual=render(ADAPTER.read_text(),sibling)
    expected_valid=name=='reviewed_original'
    assert actual.strip().startswith('<aside'),name
    assert 'merchant.invalid' not in actual,name
    assert NASA in actual and FREE in actual,name
    assert ('data-fv-review-ready="false"' in actual)==expected_valid,name
    assert ('The review panel is unavailable' in actual)==(not expected_valid),name
    assert actual.count('<a ')==(3 if expected_valid else 2),name
    if name=='misleading_nasa_endorsement': assert 'NASA has endorsed' not in actual
    if name=='misleading_review_completed': assert 'Editorial review complete' not in actual
    if name=='nonreviewed_event_handler': assert 'onclick=' not in actual
    htmls[name]=actual
    old_result=render(old_adapter,sibling) if name in (
        'reviewed_original','misleading_review_completed','misleading_nasa_endorsement',
        'misleading_independent_corroboration','misleading_commercial_cta','nonreviewed_event_handler'
        ) else None
    old_accepted=old_result is not None and 'data-fv-review-ready="false"' in old_result
    if name=='reviewed_original': assert old_accepted
    elif old_result is not None: assert old_accepted,(name,'negative control did not demonstrate parent weakness')
    results.append({'case':name,'result':'PASS','new_fallback':not expected_valid,
      'old_r279_accepted_mutation':old_accepted,'html_sha256':hashlib.sha256(actual.encode()).hexdigest()})

ctx_results=[]; screens={}
css=CSS.read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for case in ('reviewed_original','misleading_review_completed','misleading_nasa_endorsement','nonreviewed_event_handler','missing_sibling'):
        for width in (320,390,768,1440,1920):
            for js in (True,False):
                context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    reduced_motion='reduce',has_touch=width<=390,forced_colors='active' if width==320 else 'none')
                page=context.new_page(); errors=[];requests=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('request',lambda request:requests.append(request.url))
                doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+htmls[case]+'</body></html>'
                page.set_content(doc)
                assert not errors and not requests,(case,width,errors,requests)
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),(case,width)
                assert page.locator(f'a[href="{FREE}"]').count()==1,(case,width)
                if case=='reviewed_original':
                    assert page.get_by_role('heading',name='Editorial review remains open').count()==1
                    assert page.locator('details').count()==1
                    page.locator('summary').focus();page.keyboard.press('Enter')
                    assert page.locator('details[open]').count()==1
                    assert page.locator(f'a[href="{NASA}"]').first.is_visible()
                    page.keyboard.press('Enter')
                    page.emulate_media(media='print')
                    assert page.locator(f'a[href="{NASA}"]').first.is_visible()
                else:
                    assert page.get_by_role('complementary',name='Apollo 1 research custody').count()==1
                    assert page.get_by_role('link',name='NASA Apollo 204 Review Board report').count()==1
                    assert page.locator('details').count()==0
                if case in ('reviewed_original','misleading_nasa_endorsement') and width in (390,1440) and not js:
                    path=OUT/f'{case}-{width}-nojs.png'
                    page.emulate_media(media='screen')
                    page.screenshot(path=str(path),full_page=True,animations='disabled')
                    screens[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
                ctx_results.append({'case':case,'width':width,'javascript':js,'status':'PASS'})
                context.close()
    browser.close()
receipt={'suite':'Apollo R280 byte-pinned NASA review renderer actual-PHP/browser regression',
         'trusted_source_sha256':PIN,'php':results,'chromium':ctx_results,'screenshots':screens,
         'tested':'local PHP shim and offline Chromium; real screenshot hashes stable when reproducible',
         'not_tested':['installed WordPress','axe-core','screen reader','HTTP/CSP Chromium','field LCP/CLS','merchant/paid orders','founder production approval'],
         'release':'HARD_HOLD'}
(OUT/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(f'R280 PHP {len(results)}/{len(results)}; Chromium {len(ctx_results)}/{len(ctx_results)}; old accepted {sum(x["old_r279_accepted_mutation"] for x in results)-1} altered variants; receipt '+hashlib.sha256((OUT/'receipt.json').read_bytes()).hexdigest())
