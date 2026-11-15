#!/usr/bin/env python3
"""Actual Chromium / local PHP-derived fixture regression, never installed WordPress staging."""
import hashlib, json, pathlib, subprocess
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[3]
QA = ROOT / 'experience2/apollo-r383/QA'; QA.mkdir(parents=True, exist_ok=True)
JS = ROOT / 'experience2/apollo-r381/assets/atlas.js'
PHPFIX = ROOT / 'experience2/apollo-r381/qa/fixture.php'
ARCHIVE_FIX = ROOT / 'experience2/apollo-r383/qa/source-fixture-r382.html'
if PHPFIX.exists():
    document = subprocess.check_output(['php', str(PHPFIX)], text=True)
    fixture_type = 'actual-R381-PHP-renderer'
else:
    document = ARCHIVE_FIX.read_text(encoding='utf8')
    fixture_type = 'committed-R382-PHP-derived-specimen'
assert 'data-fv-atlas' in document
js = JS.read_text(encoding='utf8')
sha = hashlib.sha256(js.encode()).hexdigest()
assert sha == '5a4d82f76a06b9c3781c522d0b2483a3ef36c21a897a0cb0b3a1f742992a5105', 'unreviewed JS bytes'
# The R381 renderer includes the reviewed JS inline; the fallback has no script.
add_script = '<script' not in document
observer = """<script>window.__apollo_vitals={lcp:null,cls:0};try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__apollo_vitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__apollo_vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){window.__apollo_vitals.error=String(e)}</script>"""
document = document.replace('<head>','<head>'+observer,1)
contexts=[('320-mobile',320,720,True,False,False,False),('390-mobile',390,820,True,False,False,False),('768-tablet',768,1000,False,False,False,False),('1440-desktop',1440,900,False,False,False,False),('1920-wide',1920,1080,False,False,False,False),('320-nojs',320,720,True,True,False,False),('390-touch',390,820,True,False,False,True),('390-reduced',390,820,True,False,False,False),('320-forced',320,800,True,False,True,False),('320-root4x',320,900,True,False,False,False)]
report={'status':'LOCAL_CHROMIUM_FIXTURE_PASS_NOT_STAGING','boundary':fixture_type,'expected_script_sha256':sha,'axe_core':'NOT RUN — genuine axe-core unavailable','installed_wordpress':'NOT TESTED','http_csp':'NOT TESTED','contexts':[],'assertions':0}
def check(test,desc):
    report['assertions'] += 1
    if not test: raise AssertionError(desc)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,w,h,mobile,nojs,forced,touch in contexts:
        ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile or touch,java_script_enabled=not nojs,reduced_motion='reduce' if name=='390-reduced' else 'no-preference',forced_colors='active' if forced else 'none')
        page=ctx.new_page(); page.set_content(document,wait_until='load')
        if add_script and not nojs: page.add_script_tag(content=js)
        if name=='320-root4x': page.add_style_tag(content='html{font-size:400%!important}')
        page.wait_for_timeout(130)
        plates=page.locator('[data-fv-atlas-plate]'); phases=page.locator('[data-fv-atlas-phase]'); rail=page.locator('.fv-a381__rail a')
        check(plates.count()==6, name+' six source records')
        check(phases.count()==3, name+' three chronological phases')
        check(rail.count()==3, name+' three navigation links')
        check(page.locator('[data-fv-free-cta]').count()==1,name+' exactly one free CTA')
        check(page.locator('img,iframe,canvas').count()==0,name+' no unsourced imagery or geo')
        check(plates.filter(visible=True).count()==6,name+' all records initially visible')
        check(page.locator('[data-fv-atlas-filter]').is_visible()==(not nojs),name+' controls fail open without JS')
        check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),name+' no horizontal scrolling')
        if not nojs and name!='320-root4x':
            select=page.locator('[data-fv-atlas-filter]')
            select.select_option('response')
            check(plates.filter(visible=True).count()==1,name+' response record isolated')
            check(rail.filter(visible=True).count()==1,name+' rail synchronized to visible phase')
            check(rail.filter(visible=True).first.get_attribute('href').endswith('-response'),name+' correct phase link')
            check('1 reviewed source' in page.locator('[data-fv-atlas-status]').inner_text(),name+' live status')
            page.locator('[data-fv-atlas-reset]').click()
            check(plates.filter(visible=True).count()==6,name+' reset restores all records')
            check(rail.filter(visible=True).count()==3,name+' reset restores rail')
            check(select.evaluate('(s)=>s===document.activeElement'),name+' keyboard focus returned')
        if name=='390-touch':
            page.locator('summary').first.tap()
            check(page.locator('details').first.evaluate('(e)=>e.open'),name+' touch disclosure')
        if name=='1440-desktop':
            page.locator('summary').first.focus();page.keyboard.press('Enter')
            check(page.locator('details').first.evaluate('(e)=>e.open'),name+' keyboard disclosure')
            page.locator('[data-fv-atlas-filter]').select_option('response')
            page.pdf(path=str(QA/'Apollo_R383_Source_Print.pdf'),format='A4',print_background=False)
        page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
        values=None if nojs else page.evaluate('window.__apollo_vitals')
        report['contexts'].append({'name':name,'width':w,'checks':'PASS','local_lcp_ms': None if not values else values['lcp'],'local_cls':None if not values else values['cls']})
        ctx.close()
    browser.close()
if (QA/'Apollo_R383_Source_Print.pdf').exists():
    pdf=subprocess.check_output(['pdftotext',str(QA/'Apollo_R383_Source_Print.pdf'),'-'],text=True)
    check('Apollo' in pdf, 'Apollo title survives printable document')
    if fixture_type == 'actual-R381-PHP-renderer':
        check(pdf.count('Print source:') == 6, 'six NASA citations survive R381 print styles')
    else:
        report['fallback_print_citations'] = 'NOT VERIFIED: R382 specimen omits production print CSS'
(QA/'browser-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'browser_contexts':len(report['contexts']),'assertions':report['assertions'],'fixture':fixture_type,'axe':report['axe_core']},indent=2))
