"""Actual local Chromium / Playwright of PHP-generated fixture, NOT WP/HTTP.
Records real widths, interactions, local fixture performance and a print dossier.
"""
import hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
HERE=Path(__file__).resolve().parents[1]; ROOT=HERE.parent; OUT=HERE/'QA';OUT.mkdir(exist_ok=True)
CSS='\n'.join((p.read_text() for p in [ROOT/'apollo-r365/assets/chrono-rail.css', ROOT/'apollo-r367/assets/sequence-gate.css', ROOT/'apollo-r368/assets/reflow.css',HERE/'assets/evidence-bridge.css']))

def rendered(mode=''):
    return subprocess.check_output(['php',str(HERE/'qa/fixture.php'),mode],text=True)

def install(page,mode=''):
    markup=rendered(mode)
    page.set_content(markup.replace('</head>','<style>'+CSS+'</style></head>'),wait_until='domcontentloaded')

def stats(page):
    return page.evaluate('''() => {
      const q=s=>document.querySelectorAll(s), el=document.documentElement;
      const p=document.querySelector('.fv-apollo-r365__plate p:not(.fv-apollo-r365__class)');
      return {width:innerWidth,scroll:el.scrollWidth,rootFont:parseFloat(getComputedStyle(el).fontSize),
       paragraphWidth:p?Math.round(p.getBoundingClientRect().width):null, sourceLinks:q('[data-fv-nasa-source]').length,
       drawers:q('[data-fv-source-drawer]').length, editorPrompts:q('.fv-apollo-r369__lens').length,
       oneFreeCTA:q('[data-fv-free-cta]').length, links:[...q('a')].map(a=>({text:a.textContent.trim(),href:a.href})),
       duplicateIDs:(()=>{let a=[...q('[id]')].map(x=>x.id);return a.length-new Set(a).size;})(),
       lcp:window.__lcp??null,cls:window.__cls??null};}''')

cases=[('mobile-nojs-320',320,740,False,False,False,False,1,''),('touch-390',390,844,True,True,False,False,1,''),
 ('tablet-768',768,1024,True,False,False,False,1,''),('desktop-1440',1440,900,True,False,False,False,1,''),
 ('wide-1920',1920,1080,True,False,False,False,1,''),('reduced-motion',390,844,True,False,True,False,1,''),
 ('forced-colors',320,900,True,False,False,True,1,''),('root4x-320',320,900,True,False,False,False,4,''),
 ('root4x-390',390,900,True,False,False,False,4,''),('tampered',390,844,True,False,False,False,1,'altered'),
 ('reordered',1440,900,True,False,False,False,1,'reordered'),('omitted',320,740,False,False,False,False,1,'missing'),
 ('duplicated',390,844,True,False,False,False,1,'duplicate')]
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,width,height,js,touch,reduced,forced,mult,mode in cases:
        context=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,has_touch=touch,
          reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
        page=context.new_page();install(page,mode)
        if mult==4:page.evaluate('document.documentElement.style.fontSize="64px"')
        if js:page.evaluate('''() => {window.__lcp=null;window.__cls=0;
          try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
          try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value;}).observe({type:'layout-shift',buffered:true})}catch(e){}
        }''')
        if mode:
            assert page.locator('[data-fv-nasa-source]').count()==0, name
            assert page.locator('.fv-apollo-r369__lens').count()==0,name
            assert page.locator('.fv-apollo-r369__unavailable').count()==1,name
        else:
            assert page.locator('.fv-apollo-r369__lens').count()==3,name
            assert page.locator('[data-fv-nasa-source]').count()==4,name
            if touch:page.locator('.fv-apollo-r369__lens summary').first.tap()
            else:page.locator('.fv-apollo-r369__lens summary').first.focus();page.keyboard.press('Enter')
            assert page.locator('.fv-apollo-r369__lens').first.get_attribute('open') is not None
            page.locator('[data-fv-source-drawer] summary').first.focus();page.keyboard.press('Enter')
            assert page.locator('[data-fv-source-drawer]').first.get_attribute('open') is not None
        if js:page.wait_for_timeout(70)
        s=stats(page)
        assert s['scroll']<=width+1,(name,s)
        assert s['oneFreeCTA']==1,(name,s)
        assert s['duplicateIDs']==0,(name,s)
        assert all(x['text'] for x in s['links']),(name,s)
        assert not any('payhip.com' in x['href'] for x in s['links']),(name,s)
        if mult==4:assert s['paragraphWidth']>=200,(name,s)
        page.screenshot(path=str(OUT/(name+'.png')),full_page=(mult!=4),timeout=20000)
        if name=='desktop-1440':
            page.emulate_media(media='print');page.pdf(path=str(OUT/'educator-evidence-print.pdf'),format='A4',print_background=True)
        s.update({'case':name,'javascript':js,'mode':mode,'rootMultiplier':mult,'touch':touch,
          'reducedMotion':reduced,'forcedColors':forced,'httpNavigation':False,'actualWP':False})
        results.append(s);context.close()
    browser.close()
pdf=fitz.open(str(OUT/'educator-evidence-print.pdf'))
urls=set(x.get('uri') for p in pdf for x in p.get_links() if str(x.get('uri','')).startswith('https://www.nasa.gov/'))
assert len(urls)==3,(len(pdf),urls)
record={'passed':True,'cases':results,'contexts':len(results),'pdfPages':len(pdf),'uniqueNasaPrintURLs':len(urls),
  'cssSHA256':hashlib.sha256(CSS.encode()).hexdigest(),
  'testScope':'Local PHP-generated HTML injected into real Playwright Chromium. NOT installed WP or HTTP browser navigation.',
  'lcpCls':'Synthetic fixtures; not production CWV',
  'axeCore':'NOT EXECUTED', 'actualWordPress':'NOT EXECUTED','httpCSP':'NOT VERIFIED',
  'screenReader':'NOT EXECUTED', 'native400pctZoom':'NOT EXECUTED; 4× root font measured separately'}
(OUT/'browser-results.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':True,'contexts':len(results),'pdfPages':len(pdf),'uniqueNasaPrintURLs':len(urls),'zoomWidth320':next(x['paragraphWidth'] for x in results if x['case']=='root4x-320')},indent=2))
