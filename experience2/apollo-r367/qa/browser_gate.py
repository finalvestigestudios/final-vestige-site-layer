"""Chromium rendering of PHP-produced local fixture; NO HTTP or WordPress claim."""
import json, subprocess, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[2]
HERE=BASE/'apollo-r367'
OUT=HERE/'QA';OUT.mkdir(parents=True,exist_ok=True)
MAIN_CSS=(BASE/'apollo-r365/assets/chrono-rail.css').read_text()
NEW_CSS=(HERE/'assets/sequence-gate.css').read_text()
PHP=HERE/'qa/render_fixture.php'
def render(mode=''):
    return subprocess.check_output(['php',str(PHP),mode],text=True)

def measure(page):
    return page.evaluate('''() => ({width: innerWidth, scrollWidth:document.documentElement.scrollWidth,
      sourceCount:document.querySelectorAll('[data-fv-nasa-source]').length,
      drawerCount:document.querySelectorAll('[data-fv-source-drawer]').length,
      ctaCount:document.querySelectorAll('[data-fv-free-cta]').length,
      blocked:!!document.querySelector('.fv-apollo-r367__unavailable'),
      detailsOpen:[...document.querySelectorAll('details')].filter(d=>d.open).length,
      lcp:window.__r367LCP??null,cls:window.__r367CLS??null})''')

results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    tests=[('desktop-1440',1440,900,True,False,False,1,'',False),('mobile-nojs-320',320,700,False,True,False,1,'',False),('touch-390',390,844,True,True,False,1,'',False),('tablet-768',768,1024,True,False,False,1,'',False),('reduced-1920',1920,1080,True,False,True,1,'',False),('zoom-320',320,900,True,False,False,4,'',False),('withheld-390',390,844,False,True,False,1,'reordered',True),('altered-1440',1440,900,True,False,False,1,'altered',True)]
    for name,width,height,js,touch,reduced,scale,mode,blocked in tests:
        print('START',name,flush=True)
        context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,java_script_enabled=js,has_touch=touch,reduced_motion='reduce' if reduced else 'no-preference')
        page=context.new_page()
        if js:
            page.evaluate('''() => {window.__r367CLS=0; window.__r367LCP=null;
                try{new PerformanceObserver(list =>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__r367CLS+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){}
                try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__r367LCP=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
            }''')
        print('SET_CONTENT',name,flush=True)
        page.set_content(render(mode).replace('</head>','<style>'+MAIN_CSS+'\n'+NEW_CSS+'</style></head>'),wait_until='domcontentloaded',timeout=12000)
        if scale!=1: page.evaluate(f'document.documentElement.style.fontSize="{16*scale}px"')
        if not blocked:
            assert page.locator('a[data-fv-nasa-source]').count()==4
            assert page.locator('details[data-fv-source-drawer]').count()==4
            assert page.locator('a[data-fv-free-cta]').count()==1
            assert all(page.locator('a[data-fv-nasa-source]').nth(i).get_attribute('href').startswith('https://www.nasa.gov/') for i in range(4))
            if touch: page.locator('summary').first.tap()
            else: page.locator('summary').first.focus(); page.keyboard.press('Enter')
            assert page.locator('details').first.get_attribute('open') is not None
            assert page.locator('a[data-fv-nasa-source]').first.is_visible()
        else:
            assert page.locator('[data-fv-nasa-source]').count()==0
            assert page.locator('[data-fv-free-cta]').count()==1
            assert page.get_by_text('Evidence chronology temporarily unavailable').is_visible()
        if name=='reduced-1920':page.emulate_media(forced_colors='active')
        print("SCREENSHOT",name,flush=True)
        page.screenshot(path=str(OUT/(name+'.png')),full_page=(scale!=4),timeout=16000)
        row=measure(page) if js else {'width':width,'scrollWidth':None,'sourceCount':4 if not blocked else 0,'drawerCount':4 if not blocked else 0,'ctaCount':1,'blocked':blocked,'detailsOpen':None,'lcp':None,'cls':None};row['case']=name;row['js']=js;row['reduced_motion']=reduced;row['root_font_multiplier']=scale;row['fixture_mode']=mode or 'canonical';row['http_csp_verified']=False
        if js: assert row['scrollWidth']<=row['width']+1, (name,row)
        assert row['blocked']==blocked
        results.append(row)
        if name=='desktop-1440':
            page.emulate_media(media='print')
            page.pdf(path=str(OUT/'sealed-chronology-print.pdf'),format='A4',print_background=True)
        context.close()
    browser.close()
# verify native print source link annotations (not only text)
import fitz
pdf=fitz.open(OUT/'sealed-chronology-print.pdf')
urls=set()
for p in pdf:
    for a in p.get_links():
        if a.get('uri','').startswith('https://www.nasa.gov/'):urls.add(a['uri'])
assert len(urls)==3, f'Expected three unique NASA URLs, got {urls}'
record={'pass':True,'contexts':len(results),'cases':results,'printed_pages':len(pdf),'distinct_nasa_pdf_urls':len(urls),'css_sha256':hashlib.sha256(MAIN_CSS.encode()).hexdigest(),'browser':'Chromium Playwright set_content PHP fixtures','axe_core':'NOT_EXECUTED','http_navigation':'BLOCKED_BY_ADMINISTRATOR in R366 and rechecked R367','lcp_cls_scope':'synthetic local fixtures, not field performance','installed_wordpress':'NOT_VERIFIED'}
(OUT/'browser-results.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'pass':True,'contexts':len(results),'printed_pages':len(pdf),'distinct_source_urls':len(urls),'min_width':min(x['width'] for x in results),'max_width':max(x['width'] for x in results)},indent=2))
