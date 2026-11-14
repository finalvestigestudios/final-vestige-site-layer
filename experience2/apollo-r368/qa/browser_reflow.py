"""REAL Chromium Playwright QA of PHP-generated staging fixture, not installed WP.
No network, no CDNs, no WordPress writes. Test inheritance + additive R368 reflow.
Explicitly records axe-core missing; does NOT call CDP tree inspection 'axe'.
"""
from pathlib import Path
import hashlib, json, subprocess
from playwright.sync_api import sync_playwright
import fitz

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE/'QA'; OUT.mkdir(exist_ok=True)
CSS365 = (ROOT/'apollo-r365/assets/chrono-rail.css').read_text()
CSS367 = (ROOT/'apollo-r367/assets/sequence-gate.css').read_text()
CSS368 = (HERE/'assets/reflow.css').read_text()

def html(mode=''):
    return subprocess.check_output(['php', str(HERE/'qa/render_fixture.php'), mode], text=True)

def install(page, mode='', overlay=True):
    css=CSS365+'\n'+CSS367+('\n'+CSS368 if overlay else '')
    page.set_content(html(mode).replace('</head>','<style>'+css+'</style></head>'), wait_until='domcontentloaded')

def dimensions(page):
    return page.evaluate('''() => {
       const root = document.querySelector('.fv-apollo-r365');
       const plate = document.querySelector('.fv-apollo-r365__plate');
       const paragraph = plate?.querySelector('p:not(.fv-apollo-r365__class)');
       return {
         viewportWidth:innerWidth, bodyScrollWidth:document.documentElement.scrollWidth,
         plateWidth:plate?Math.round(plate.getBoundingClientRect().width):null,
         paragraphWidth:paragraph?Math.round(paragraph.getBoundingClientRect().width):null,
         paragraphFontPx:paragraph?parseFloat(getComputedStyle(paragraph).fontSize):null,
         rootFontPx:parseFloat(getComputedStyle(document.documentElement).fontSize),
         sources:document.querySelectorAll('[data-fv-nasa-source]').length,
         drawers:document.querySelectorAll('[data-fv-source-drawer]').length,
         freeCTA:document.querySelectorAll('[data-fv-free-cta]').length,
         withheld:!!document.querySelector('.fv-apollo-r367__unavailable'),
         sourceLinkNames:[...document.querySelectorAll('[data-fv-nasa-source]')].map(x=>x.textContent.trim()),
         missingLinkNames:[...document.querySelectorAll('a')].filter(x=>!x.textContent.trim()).length,
         lcp:window.__r368Lcp??null,cls:window.__r368Cls??null
       };
    }''')

def observe(page):
    page.evaluate('''() => {
       window.__r368Lcp=null;window.__r368Cls=0;
       try{new PerformanceObserver(list=>{for(const e of list.getEntries()) window.__r368Lcp=e.startTime;})
          .observe({type:'largest-contentful-paint', buffered:true});}catch(e){}
       try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__r368Cls+=e.value;})
          .observe({type:'layout-shift', buffered:true});}catch(e){}
    }''')

results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    testcases=[
        ('mobile-nojs-320',320,740,False,False,False,False,1,'',False),
        ('touch-390',390,844,True,True,False,False,1,'',False),
        ('tablet-768',768,1024,True,False,False,False,1,'',False),
        ('desktop-1440',1440,900,True,False,False,False,1,'',False),
        ('wide-1920',1920,1080,True,False,False,False,1,'',False),
        ('reduced-motion-390',390,844,True,False,True,False,1,'',False),
        ('forced-colors-320',320,850,True,False,False,True,1,'',False),
        ('root4x-320',320,900,True,False,False,False,4,'',False),
        ('root4x-390',390,900,True,False,False,False,4,'',False),
        ('altered-390',390,844,False,True,False,False,1,'altered',True),
        ('reordered-1440',1440,900,True,False,False,False,1,'reordered',True),
    ]
    # Run paired legacy/patch comparison without guessing subjective WCAG outcomes.
    context=browser.new_context(viewport={'width':320,'height':900})
    page=context.new_page();install(page, overlay=False)
    page.evaluate('document.documentElement.style.fontSize="64px"')
    old=dimensions(page)
    install(page, overlay=True)
    page.evaluate('document.documentElement.style.fontSize="64px"')
    new=dimensions(page)
    assert new['paragraphWidth'] >= old['paragraphWidth'] + 50,(old,new)
    assert new['bodyScrollWidth'] <= 321, (old,new)
    context.close()
    for name,width,height,js,touch,reduced,forced,mult,mode,withheld in testcases:
        context=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,
           has_touch=touch,reduced_motion=('reduce' if reduced else 'no-preference'),forced_colors=('active' if forced else 'none'))
        page=context.new_page();install(page,mode=mode)
        if mult!=1: page.evaluate(f'document.documentElement.style.fontSize="{16*mult}px"')
        if js:observe(page)
        if withheld:
            assert page.locator('a[data-fv-nasa-source]').count()==0
            assert page.get_by_text('Evidence chronology temporarily unavailable').is_visible()
        else:
            assert page.locator('a[data-fv-nasa-source]').count()==4
            assert page.locator('[data-fv-source-drawer]').count()==4
            if touch:page.locator('summary').first.tap()
            else:page.locator('summary').first.focus();page.keyboard.press('Enter')
            assert page.locator('details').first.get_attribute('open') is not None
            assert page.locator('a[data-fv-nasa-source]').first.is_visible()
        assert page.locator('a[data-fv-free-cta]').count()==1
        if js:page.wait_for_timeout(70)
        metrics=dimensions(page)
        assert metrics['bodyScrollWidth']<=width+1,(name,metrics)
        assert metrics['missingLinkNames']==0,(name,metrics)
        assert metrics['withheld']==withheld,(name,metrics)
        if not withheld:assert len(set(metrics['sourceLinkNames']))==4
        # 4x root-font can be tall, but keep 320px inline viewport usable.
        if mult==4:assert metrics['paragraphWidth']>=200,(name,metrics)
        page.screenshot(path=str(OUT/(name+'.png')),full_page=mult!=4,timeout=18000)
        if name=='desktop-1440':
            page.emulate_media(media='print')
            page.pdf(path=str(OUT/'r368-dossier.pdf'),format='A4',print_background=True)
        metrics.update({'case':name,'javaScriptEnabled':js,'rootFontMultiplier':mult,
           'touch':touch,'reducedMotion':reduced,'forcedColors':forced,'fixtureVariant':mode or 'reviewed',
           'httpCspAcceptance':False,'installedWordPressAcceptance':False})
        results.append(metrics);context.close()
    browser.close()

pdf=fitz.open(OUT/'r368-dossier.pdf'); urls=set()
for page in pdf:
    for link in page.get_links():
        u=link.get('uri','')
        if u.startswith('https://www.nasa.gov/'):urls.add(u)
assert len(urls)==3,(len(pdf),urls)
record={'passed':True,'contexts':len(results),'cases':results,'fourXParagraphWidthBefore':old['paragraphWidth'],
    'fourXParagraphWidthAfter':new['paragraphWidth'],'fourXWidthGainPx':new['paragraphWidth']-old['paragraphWidth'],
    'printPages':len(pdf),'printedDistinctNASAUrls':len(urls),'cssOverlaySHA256':hashlib.sha256(CSS368.encode()).hexdigest(),
    'browser':'real Chromium via Playwright, local PHP HTML via set_content',
    'axeCore':'NOT EXECUTED: no installed package and npm registry unavailable (EAI_AGAIN)',
    'screenReader':'NOT EXECUTED','httpCsp':'NOT VERIFIED (local browser navigation blocked by administrator)',
    'realWordPressAssembler':'NOT VERIFIED',
    'performanceScope':'LCP/CLS where observable on synthetic set_content fixture; no field CWV or production claim',
    'wcag':'Automated checks are a partial regression; independent manual AT and axe required'}
(OUT/'browser-results.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print(json.dumps({'passed':True,'contexts':len(results),'fourXParagraphWidthBefore':old['paragraphWidth'],
    'fourXParagraphWidthAfter':new['paragraphWidth'],'printPages':len(pdf),'printedNASAUrls':len(urls)},indent=2))
