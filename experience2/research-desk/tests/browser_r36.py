"""Chromium regression on ACTUAL Research Desk PHP + NASA template + CSS + JS.
Run from full PR checkout: python experience2/research-desk/tests/browser_r36.py
Local-file navigation may be administrator-blocked; report fallback, never fake metrics.
"""
import hashlib, json, pathlib, subprocess
from playwright.sync_api import sync_playwright, Error as PlaywrightError
BASE=pathlib.Path(__file__).resolve().parents[1]
OUT=BASE/'tests/generated-r36'
OUT.mkdir(exist_ok=True)
r=subprocess.run(['php',str(BASE/'tests/r36_wp_probe.php'),str(BASE/'final-vestige-ex2-research-desk.php')],capture_output=True,text=True,check=True)
parts=json.loads(r.stdout)['html']
assert len(parts)==3 and all(p.count('data-fvx-record ') == 6 for p in parts)
css=(BASE/'assets/source-ledger.css').read_text()
js=(BASE/'assets/source-ledger.js').read_text()
assert all('S67-19766' in p for p in parts)
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R36 staged Research Desk</title><style>'+css+'</style></head><body>'+''.join(parts)+'<script>'+js+'</script></body></html>'
fixture=OUT/'research-desk-3x.html'; fixture.write_text(html)
observer="""(()=>{window.__fvPerf={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fvPerf.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fvPerf.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}})();"""
records=[]; js_errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        for enabled in (True,False):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,has_touch=width<768,reduced_motion='reduce')
            page=ctx.new_page()
            page.on('pageerror',lambda error:js_errors.append(str(error)))
            page.add_init_script(observer)
            mode='file_navigation'
            try:page.goto(fixture.as_uri(),wait_until='load')
            except PlaywrightError as ex:
                if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(ex):raise
                mode='set_content_fallback'
                page.close();page=ctx.new_page()
                page.on('pageerror',lambda error:js_errors.append(str(error)))
                page.set_content(html,wait_until='load')
            roots=page.locator('[data-fvx-ledger]')
            assert roots.count()==3
            ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
            assert len(ids)==len(set(ids))
            assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
            for i in range(3):
                root=roots.nth(i)
                assert root.locator('[data-fvx-record]').count()==6
                assert root.get_attribute('aria-labelledby')==root.locator('h1').get_attribute('id')
                assert root.locator('label').get_attribute('for')==root.locator('input[data-fvx-search]').get_attribute('id')
                assert root.locator('input[data-fvx-search]').get_attribute('aria-controls')==root.locator('.fv-ex2-ledger__grid').get_attribute('id')
                assert root.locator('a[href^="https://www.nasa.gov/"]').count()>=6
                assert root.locator('[data-fvx-record]:visible').count()==6
                assert root.locator('[data-fvx-tools]').is_visible()==enabled
            page.wait_for_timeout(180)
            perf=page.evaluate('window.__fvPerf || null') if enabled and mode=='file_navigation' else None
            if enabled:
                roots.nth(1).locator('input').fill('oxygen')
                assert roots.nth(1).locator('[data-fvx-record]:visible').count()<6
                assert roots.nth(0).locator('[data-fvx-record]:visible').count()==6
                roots.nth(1).locator('input').fill('')
                assert roots.nth(1).locator('[data-fvx-record]:visible').count()==6
                roots.nth(0).locator('summary').first.focus();page.keyboard.press('Enter')
                assert roots.nth(0).locator('details').first.get_attribute('open') is not None
                roots.nth(1).locator('[data-fvx-record]').nth(3).evaluate('(e)=>e.removeAttribute("data-fvx-search")')
                roots.nth(1).locator('input').fill('oxygen')
                assert roots.nth(1).locator('[data-fvx-record]:visible').count()==6
                assert not roots.nth(1).locator('[data-fvx-tools]').is_visible()
                assert roots.nth(2).locator('[data-fvx-tools]').is_visible()
                if width<768:
                    roots.nth(2).locator('summary').first.tap()
                    assert roots.nth(2).locator('details').first.get_attribute('open') is not None
            if width in (390,1440):
                page.screenshot(path=str(OUT/f'r36-{width}-{"js" if enabled else "nojs"}.png'),full_page=True)
            records.append({'width':width,'javascript':enabled,'mode':mode,'roots':3,'total_records':18,'unique_ids':True,'local_lcp_ms':None if perf is None else perf['lcp'],'local_cls':None if perf is None else perf['cls']})
            ctx.close()
    browser.close()
assert not js_errors,js_errors
receipt={'checks':len(records),'results':records,'js_errors':js_errors,'html_sha256':hashlib.sha256(html.encode()).hexdigest(),'limitations':['Not an installed WordPress environment','File-navigation metrics are local synthetic, not hosted CWV','No axe-core audit','NASA image rights and S67-19766 identity still unresolved']}
(OUT/'r36-browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(f'PASS {len(records)} Chromium configurations; modes={sorted(set(x["mode"] for x in records))}; no claims of hosted CWV')
