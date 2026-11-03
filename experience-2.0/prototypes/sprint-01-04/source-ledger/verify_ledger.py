"""Source-ledger contract tests: real Chromium; no dependencies beyond Python Playwright/Chromium."""
from pathlib import Path
import sys
import json
from playwright.sync_api import sync_playwright
from build_ledger import load_and_validate, BadRecord, safe_https, render_content, CSS, JS
from html import escape

ROOT=Path(__file__).resolve().parent
OUT={"browser":"Chromium", "viewports":{}, "outcomes":{}}

def check(cond, message):
    if not cond: raise AssertionError(message)

m=load_and_validate()
check(len(m['records'])==6,'six source records required')
for bad in ['http://www.nasa.gov/source','javascript:alert(1)','https://evil.example/preview','https://nasa.gov.evil.test/report','https://someone:secret@www.nasa.gov/steal']:
    try: safe_https(bad)
    except BadRecord: pass
    else: raise AssertionError(f'unsafe URL admitted: {bad}')
check('data-fvx-ledger' in (ROOT/'wordpress-block.html').read_text(),'WordPress markup missing root')
check('<!-- wp:html -->' in (ROOT/'wordpress-block.html').read_text(),'Gutenberg html wrapper missing')
html=(ROOT/'index.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for w,h in [(360,780),(390,844),(768,1024),(1024,850),(1440,900),(1920,1080)]:
        page=browser.new_page(viewport={'width':w,'height':h},reduced_motion='reduce')
        page.set_content(html,wait_until='domcontentloaded')
        result=page.evaluate('''() => ({width: document.documentElement.scrollWidth,viewport: innerWidth,cards: document.querySelectorAll('[data-fvx-record]:not([hidden])').length,enhanced: !!document.querySelector('[data-fvx-ledger][data-fvx-initialized="yes"]'),searchVisible: getComputedStyle(document.querySelector('[data-fvx-tools]')).display!=='none',brokenLinks:[...document.querySelectorAll('.fv-ex2-ledger__recordlinks a')].filter(x=>!x.href.startsWith('https://www.nasa.gov/')).length})''')
        check(result['width']<=w,f'horizontal overflow {w}: {result}')
        check(result['cards']==6 and result['enhanced'] and result['searchVisible'], f'initial enhancement failed at {w}: {result}')
        check(result['brokenLinks']==0, f'unapproved source links {w}')
        if w==1440:
            search=page.locator('input[data-fvx-search]')
            search.fill('hatch')
            matches=page.locator('[data-fvx-record]:visible').count()
            check(matches>=1 and matches<6,'search filtering failed')
            check('of 6 evidence records' in page.locator('[data-fvx-status]').inner_text(),'count missing')
            search.fill('word-no-record-matches')
            check(page.locator('[data-fvx-record]:visible').count()==0,'empty results not applied')
            check(page.locator('[data-fvx-empty]').is_visible(),'empty-state message absent')
            search.fill('')
            check(page.locator('[data-fvx-record]:visible').count()==6,'clear search did not restore all')
            first=page.locator('.fv-ex2-ledger__fulltext').first
            first.locator('summary').click()
            check(first.get_attribute('open') is not None,'details native toggle failed')
            check(page.locator('a[href="https://www.nasa.gov/image-detail/apollo-1-crew-honored/"]').count()==1,'source record link absent')
        page.screenshot(path=str(ROOT/f'ledger-{w}.png'),animations='disabled',full_page=(w in [390,1440]))
        OUT['viewports'][str(w)]=result
        page.close()
    nojs=browser.new_page(viewport={'width':390,'height':844},java_script_enabled=False)
    nojs.set_content(html,wait_until='domcontentloaded')
    check(nojs.locator('[data-fvx-record]').count()==6,'no-JS records missing')
    check(nojs.locator('[data-fvx-tools]').is_hidden(),'no-JS search should remain hidden')
    check(nojs.locator('.fv-ex2-ledger__fulltext').count()==6,'native details missing')
    nojs.locator('.fv-ex2-ledger__fulltext').first.locator('summary').click()
    check(nojs.locator('.fv-ex2-ledger__fulltext').first.get_attribute('open') is not None, 'no-JS details not operable')
    OUT['outcomes']['nojs']='pass'
    nojs.close()
    # A missing enhancement script should leave the source list intact.
    static=browser.new_page(viewport={'width':390,'height':844})
    static.set_content(html.replace('<script>'+JS+'</script>',''))
    check(static.locator('[data-fvx-record]').count()==6 and static.locator('[data-fvx-tools]').is_hidden(),'missing JS damaged static content')
    OUT['outcomes']['script_absent']='pass'
    static.close()
    # Multiple independent instances with distinct IDs and namespaced filtering.
    two=browser.new_page(viewport={'width':1440,'height':900})
    pair='<!doctype html><html><head><style>'+CSS+'</style></head><body>'+render_content(m,'a')+render_content(m,'b')+'<script>'+JS+'</script></body></html>'
    two.set_content(pair)
    check(two.locator('[id="fv-ex2-ledger-a-search"]').count()==1 and two.locator('[id="fv-ex2-ledger-b-search"]').count()==1,'non-unique IDs')
    two.locator('#fv-ex2-ledger-a-search').fill('hatch')
    a_count=two.locator('[data-fvx-ledger]').nth(0).locator('[data-fvx-record]:visible').count()
    b_count=two.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-record]:visible').count()
    check(a_count<6 and b_count==6, 'instance isolation failed')
    OUT['outcomes']['multi_instance']='pass'
    two.close()
    browser.close()
(ROOT/'QA_RESULTS.json').write_text(json.dumps(OUT,indent=2)+'\n')
print('PASS: scoped Source Ledger, six verified records, URL safety, responsive, no-JS, native details, filters, multiple independent instances')
