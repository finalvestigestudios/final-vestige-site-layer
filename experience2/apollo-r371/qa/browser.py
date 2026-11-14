"""R371 actual Chromium engine against local PHP HTML fixture; no HTTP/WP/axe claims.
Requires: php, python playwright and installed Chromium. Outputs deterministic-ish
machine-readable results; screenshots/PDF are reproducible but Chromium timestamps
and rendering can vary across browser versions.
"""
import json, pathlib, subprocess, sys
from playwright.sync_api import sync_playwright
BASE=pathlib.Path(__file__).resolve().parents[1]
qa=BASE/'QA'; qa.mkdir(exist_ok=True)
html=subprocess.check_output(['php',str(BASE/'qa/fixture.php')],text=True)
scenarios=[
    ('mobile-320',320,740,{},16,False),
    ('mobile-nojs-320',320,740,{'java_script_enabled':False},16,False),
    ('mobile-390',390,840,{},16,False),
    ('touch-390',390,840,{'has_touch':True,'is_mobile':True},16,False),
    ('tablet-768',768,980,{},16,False),
    ('desktop-1440',1440,900,{},16,False),
    ('wide-1920',1920,1080,{},16,False),
    ('root4x-320',320,740,{},64,False),
    ('reduced-390',390,840,{'reduced_motion':'reduce'},16,False),
    ('forced-320',320,740,{'forced_colors':'active'},16,False),
]
result={'runner':'actual Playwright Chromium page.set_content local PHP fixture','scope':'NOT installed WordPress, NOT HTTP, NOT production, NOT axe-core, NOT real visitor CWV','cases':[], 'errors':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    for label,w,h,options,rootfont,_ in scenarios:
        ctx=browser.new_context(viewport={'width':w,'height':h},**options)
        page=ctx.new_page()
        if rootfont != 16: page.add_style_tag(content=f':root{{font-size:{rootfont}px!important}}')
        page.set_content(html,wait_until='load')
        if rootfont != 16: page.add_style_tag(content=f':root{{font-size:{rootfont}px!important}}')
        page.evaluate('document.fonts.ready')
        summary=page.locator('details summary')
        checks={
            'cards':page.locator('.fv-apollo-r371__card').count()==4,
            'drawers':summary.count()==4,
            'source_urls':page.locator('[data-fv-nasa-source]').count()==4,
            'one_free_cta':page.locator('[data-fv-free-cta]').count()==1,
            'ids_unique':page.evaluate("(()=>{let ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size})()"),
            'no_horizontal_overflow':page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),
            'no_external_media':page.locator('img,iframe,video,script').count()==0,
            'source_hidden_before_details':not page.locator('[data-fv-nasa-source]').first.is_visible(),
        }
        # Native details must work without JS, using pointer or keyboard navigation.
        summary.first.focus()
        page.keyboard.press('Enter')
        checks['keyboard_details_open']=page.locator('details').first.get_attribute('open') is not None
        checks['keyboard_source_visible']=page.locator('[data-fv-nasa-source]').first.is_visible()
        page.keyboard.press('Enter')
        checks['keyboard_details_close']=page.locator('details').first.get_attribute('open') is None
        summary.nth(2).click()
        checks['pointer_details_open']=page.locator('details').nth(2).get_attribute('open') is not None
        if label=='touch-390':
            page.locator('details summary').nth(3).tap()
            checks['touch_details_open']=page.locator('details').nth(3).get_attribute('open') is not None
        width=page.locator('.fv-apollo-r371__card').first.evaluate('(n)=>Math.round(n.getBoundingClientRect().width)')
        page.screenshot(path=str(qa/(label+'.png')),full_page=True)
        entry={'case':label,'viewport':w,'root_font_px':rootfont,'first_card_width_px':width,'checks':checks}
        result['cases'].append(entry)
        if not all(checks.values()): result['errors'].append(entry)
        ctx.close()
    ctx=browser.new_context(viewport={'width':1024,'height':768}); page=ctx.new_page(); page.set_content(html)
    page.emulate_media(media='print')
    page.pdf(path=str(qa/'documentary-gallery-print.pdf'),format='A4',print_background=True,prefer_css_page_size=False)
    ctx.close(); browser.close()
(qa/'browser-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'cases':len(result['cases']),'checks':sum(len(x['checks']) for x in result['cases']), 'failures':len(result['errors']), 'notes':result['scope']},indent=2))
if result['errors']: sys.exit(1)
