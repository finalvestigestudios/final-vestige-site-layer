"""Real Chromium Playwright, locally rendered PHP HTML; NOT installed WP or HTTP.
Recreates the four WordPress stylesheet handles in pre-head dependency order.
"""
import hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'apollo-r370'
OUT=HERE/'QA';OUT.mkdir(exist_ok=True)
CSS=[ROOT/'apollo-r365/assets/chrono-rail.css',ROOT/'apollo-r367/assets/sequence-gate.css',ROOT/'apollo-r368/assets/reflow.css',ROOT/'apollo-r369/assets/evidence-bridge.css']
html=subprocess.check_output(['php',str(ROOT/'apollo-r369/qa/fixture.php')],text=True)
styles='\n'.join('<style data-handle="'+handle+'">'+p.read_text()+'</style>' for handle,p in zip(['fv-apollo-r365-chronology','fv-apollo-r367-sequence','fv-apollo-r368-reflow','fv-apollo-r369-educator-bridge'],CSS))
assert html.count('</head>')==1
html=html.replace('</head>',styles+'</head>')
records=[]
checks=[('mobile-320-nojs',320,740,False,False,1,False,False),('touch-390',390,844,True,True,1,False,False),('tablet-768',768,900,True,False,1,False,False),('desktop-1440',1440,900,True,False,1,False,False),('wide-1920',1920,1080,True,False,1,False,False),('enlarged-320',320,900,True,False,4,False,False),('reduced-390',390,844,True,False,1,True,False),('forced-320',320,900,True,False,1,False,True)]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,w,h,js,touch,zoom,reduced,forced in checks:
        context=browser.new_context(viewport={'width':w,'height':h},java_script_enabled=js,has_touch=touch,reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
        page=context.new_page()
        if js:
            page.evaluate('''() => {window.__lcp=null;window.__cls=0;new PerformanceObserver(list=>{for(const e of list.getEntries())window.__lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__cls+=e.value;}).observe({type:'layout-shift',buffered:true});}''')
        page.set_content(html,wait_until='load')
        if zoom==4: page.evaluate('document.documentElement.style.fontSize="64px"')
        assert page.locator('head style[data-handle]').count()==4,name
        assert page.locator('[data-fv-nasa-source]').count()==4,name
        assert page.locator('.fv-apollo-r369__lens').count()==3,name
        assert page.locator('[data-fv-free-cta]').count()==1,name
        assert page.locator('[data-fv-source-drawer]').count()==4,name
        if js:
            if touch: page.locator('.fv-apollo-r369__lens summary').first.tap()
            else: page.locator('.fv-apollo-r369__lens summary').first.focus();page.keyboard.press('Enter')
            assert page.locator('.fv-apollo-r369__lens').first.get_attribute('open') is not None,name
            page.wait_for_timeout(120)
        met=page.evaluate('''() => {let doc=document.documentElement;return {width:innerWidth,scrollWidth:doc.scrollWidth,rootFont:getComputedStyle(doc).fontSize,rootBackground:getComputedStyle(document.querySelector('.fv-apollo-r369')).backgroundColor,ctaCount:document.querySelectorAll('[data-fv-free-cta]').length,sourceCount:document.querySelectorAll('[data-fv-nasa-source]').length,paragraphWidth:Math.round(document.querySelector('.fv-apollo-r365__plate p:not(.fv-apollo-r365__class)').getBoundingClientRect().width),duplicates:(a=>a.length-new Set(a).size)([...document.querySelectorAll('[id]')].map(x=>x.id)),lcp:window.__lcp??null,cls:window.__cls??null};}''')
        assert met['scrollWidth']<=w+1,(name,met)
        assert met['duplicates']==0,(name,met)
        assert met['rootBackground']!='rgba(0, 0, 0, 0)',(name,met)
        if zoom==4: assert met['paragraphWidth']>=200,(name,met)
        page.screenshot(path=str(OUT/(name+'.png')),full_page=False)
        if name=='desktop-1440':
            page.emulate_media(media='print')
            page.pdf(path=str(OUT/'prehead-evidence.pdf'),format='A4',print_background=True)
        met.update({'case':name,'javascript':js,'touch':touch,'multiplier':zoom,'reducedMotion':reduced,'forcedColors':forced,'actualWordPress':False,'httpNavigation':False,'axeCore':False})
        records.append(met);context.close()
    browser.close()
result={'passed':True,'chromiumCases':len(records),'cases':records,'scope':'Real local Chromium with PHP-rendered fixtures; NOT real WP/HTTP/CSP, axe-core or p75 CWV','cssSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CSS}}
(OUT/'browser-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'passed':True,'chromiumCases':len(records),'viewports':[r['width'] for r in records],'lcpFixtureObserved':[r['lcp'] for r in records],'clsFixtureObserved':[r['cls'] for r in records]},indent=2))
