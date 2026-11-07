#!/usr/bin/env python3
"""Exact pinned WordPress-preview PHP payload -> isolated Chromium acceptance.
No WordPress runtime, no network, no form submissions, no production writes.
"""
import argparse
import asyncio
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
from playwright.async_api import async_playwright

PINNED_BUNDLE_SHA256 = '9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d'
PHP = 'mu-plugins/fv-ex2-playground-review.php'
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
FOCUS = 'https://finalvestige.com/focus/'

def sha256(x): return hashlib.sha256(x).hexdigest()

def make_fixture(path: Path):
    raw = path.read_bytes()
    if sha256(raw) != PINNED_BUNDLE_SHA256:
        raise ValueError('STOP: pinned ZIP SHA mismatch; not the approved source package')
    with ZipFile(path) as z:
        content = z.read(PHP).decode('utf-8')
        custody = json.loads(z.read('SOURCE_CUSTODY.json'))
        if sha256(content.encode('utf-8')) != custody['files_sha256'][PHP]:
            raise ValueError('STOP: PHP differs from custody manifest')
        if custody.get('native_wordpress_tested') is not False:
            raise ValueError('STOP: unexpected provenance claim')
    parts = {}
    for key in ('HTML', 'CSS', 'JS'):
        found = re.search(r"<<<'FVPG_"+key+r"_END'\n(.*?)\nFVPG_"+key+r"_END",content,re.S)
        if not found: raise ValueError('STOP: missing real plugin '+key+' segment')
        parts[key] = found.group(1).lstrip('\n')
    html = parts['HTML']
    if len(re.findall(r'class="fv-margin-strip__item"',html))!=72: raise ValueError('STOP: 72 Margins invariant lost')
    if len(re.findall(r'<a[^>]+href="'+re.escape(FOCUS)+r'"',html))!=5: raise ValueError('STOP: 5 Focus links lost')
    if len(re.findall(r'<a href="#fv-hf-',html))<7: raise ValueError('STOP: chapter navigation potentially lost')
    if '<img ' not in html or 'Franklinexpeditionnote.jpg' not in html: raise ValueError('STOP: media source drift')
    if 'digitalcollections.nypl.org/items/' not in html or 'NYPL 5003296' not in html: raise ValueError('STOP: pending NYPL source credit lost')
    if 'ARCHIVAL REFERENCE · IMAGE NOT REPRODUCED' not in html: raise ValueError('STOP: protected NYPL media exclusion lost')
    assembled = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Isolated FV EX2 WordPress Payload Browser Proof — NOT WORDPRESS</title>'
        '<style>'+parts['CSS']+'</style></head><body>'+html+'<script>'+parts['JS']+'</script></body></html>')
    return assembled,{k:{'bytes':len(v.encode()),'sha256':sha256(v.encode())} for k,v in parts.items()}

async def run(bundle: Path, out: Path):
    html, source = make_fixture(bundle)
    out.mkdir(parents=True,exist_ok=True)
    results=[]; interactions={};negative_controls={}
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for zoom in (1,2):
                for js in (False,True):
                    for w in WIDTHS:
                        context=await browser.new_context(viewport={'width':w,'height':900},java_script_enabled=js,service_workers='block',reduced_motion='reduce' if zoom==2 else 'no-preference')
                        req=[]; page=await context.new_page(); errors=[]
                        page.on('pageerror',lambda err: errors.append(str(err)))
                        async def block(route):
                            req.append(route.request.url)
                            await route.abort()
                        await context.route('**/*',block)
                        await page.set_content(html,wait_until='domcontentloaded')
                        if zoom==2: await page.evaluate('document.documentElement.style.zoom="2"')
                        await page.wait_for_timeout(70)
                        record=await page.evaluate('''() => {
                          const root=document.documentElement;
                          const all=[...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')];
                          const hit=a=>{const b=a.getBoundingClientRect();if(b.top<0||b.left<0||b.bottom>innerHeight||b.right>innerWidth)return false;const e=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2);return !!e&&(e===a||a.contains(e))};
                          const chapters=[...document.querySelectorAll('.fv-hf__chapter-nav a')];
                          return {doc_width:root.scrollWidth,overflow:root.scrollWidth>innerWidth+1,
                            focus_count:all.length, firstscreen_focus:all.filter(hit).length,
                            chapters:chapters.length,chapter_targets_present:chapters.every(a=>!!document.querySelector(a.getAttribute('href'))),
                            margins:document.querySelectorAll('.fv-margin-strip__item').length,
                            visible_cases:[...document.querySelectorAll('[data-fv-case]')].filter(x=>getComputedStyle(x).display!=='none'&&!x.hidden).length,
                            scroll_height:root.scrollHeight};
                        }''')
                        good=record['chapters']==7 and record['chapter_targets_present'] and record['margins']==72 and record['focus_count']==5 and record['firstscreen_focus']>=1 and not record['overflow'] and not errors and record['visible_cases']==(1 if js else 3)
                        results.append({'width':w,'zoom':zoom,'javascript':js,'pass':good,'measurements':record,'js_exceptions':errors,'blocked_network_requests':len(req)})
                        if js and zoom==1 and w in (320,390,768,1440,1920):
                            await page.screenshot(path=str(out/f'fullpage_{w}.png'),full_page=True)
                            await page.screenshot(path=str(out/f'firstscreen_{w}.png'))
                        if js and zoom==2 and w in (390,1440): await page.screenshot(path=str(out/f'zoom200_firstscreen_{w}.png'))
                        if w==390 and js and zoom==1:
                            async def test_click(name,locator,condition):
                                try:
                                    await locator.click(timeout=4000)
                                    interactions[name]={'pass':bool(await page.evaluate(condition))}
                                except Exception as exc: interactions[name]={'pass':False,'error':str(exc)[:200]}
                            await test_click('case_switch_to_franklin',page.locator('[data-fv-case-button="franklin"]'),'''() => document.querySelector('[data-fv-case="franklin"]').hidden===false && document.querySelector('[data-fv-case="apollo"]').hidden===true''')
                            await test_click('chronicle_1848',page.locator('[data-fv-chronicle-view="addition"]'),'''() => document.querySelector('.fv-hf__chronicle').dataset.fvChronicleMode==='addition' ''')
                            await test_click('observer_b',page.locator('[data-fv-observer-switch="b"]'),'''() => document.querySelector('[data-fv-observer-switch="b"]').getAttribute('aria-pressed')==='true' ''')
                            await test_click('chapter_navigation',page.locator('.fv-hf__chapter-nav a[href="#fv-hf-evidence"]'),'''() => location.hash==='#fv-hf-evidence' ''')
                        await context.close()
            corrupted={
             'missing_margin':html.replace('class="fv-margin-strip__item"','class="fv-margin-strip__removed"',1),
             'missing_focus':html.replace('href="https://finalvestige.com/focus/"','href="/excluded-focus/"',1),
             'missing_chapter_target':html.replace('id="fv-hf-evidence"','id="fv-hf-gone"',1),
            }
            for name, altered in corrupted.items():
                ctx=await browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False,service_workers='block')
                await ctx.route('**/*',lambda route:route.abort())
                pg=await ctx.new_page();await pg.set_content(altered)
                d=await pg.evaluate('''() => ({margins:document.querySelectorAll('.fv-margin-strip__item').length, focus:document.querySelectorAll('a[href="https://finalvestige.com/focus/"]').length, targets:[...document.querySelectorAll('.fv-hf__chapter-nav a')].every(a=>document.querySelector(a.getAttribute('href')))})''')
                failed=(d['margins']!=72 or d['focus']!=5 or not d['targets'])
                negative_controls[name]={'correctly_rejected':failed,'observed':d}
                await ctx.close()
        finally:await browser.close()
    passed=sum(a['pass'] for a in results)
    report={'scope':'REAL PINNED WP-PLUGIN SOURCE, OFFLINE Chromium only; NOT WordPress/Assembler or hosted rendering',
            'bundle_sha256':PINNED_BUNDLE_SHA256,'sources':source,'configs':len(results),'passed':passed,
            'interactions':interactions,'negative_controls':negative_controls,'results':results,
            'release':'HOLD','not_qualified':['WordPress/Assembler integration','real image transfer bytes','Jetpack opt-in','WCAG 2.2 AA / axe','measured Lighthouse/CWV','hosted CI and independent QD','founder visual signoff']}
    (out/'acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    result=asyncio.run(run(a.bundle,a.out))
    print(f"Pinned-source offline Chromium: {result['passed']}/{result['configs']} configurations; interactions={result['interactions']}; controls={result['negative_controls']}")
    if result['passed']!=result['configs'] or not all(x['pass'] for x in result['interactions'].values()) or not all(x['correctly_rejected'] for x in result['negative_controls'].values()):raise SystemExit(1)
