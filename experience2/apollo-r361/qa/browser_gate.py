#!/usr/bin/env python3
"""Real Chromium browser fixtures. No installed WordPress, axe-core or live HTTP claims."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
ROOT=Path(__file__).resolve().parents[3]; EX=ROOT/'experience2'
OUT=EX/'apollo-r361/QA';OUT.mkdir(parents=True,exist_ok=True)
php=(EX/'apollo-r361/rights-asset-bridge.php').resolve()
code='define("ABSPATH",true); require '+json.dumps(str(php))+'; echo fv_apollo_r361_shortcode();'
content=subprocess.check_output(['php','-r',code],text=True)
assert content.count('data-fv-rights-reviewed-link')==9
assert '<script' not in content and '<img' not in content
style=(EX/'apollo-r360/assets/rights-audit.css').read_text()
fixture='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R361 custody</title><style>'+style+'</style></head><body><main>'+content+'</main></body></html>'
cases=[('mobile-nojs',320,False,16,'reduce','none',False),('mobile-400pct',320,True,64,'reduce','none',False),('keyboard-390',390,True,16,'no-preference','none',False),('touch-768',768,True,16,'reduce','none',True),('desktop-1440',1440,True,16,'no-preference','none',False),('forced-1920',1920,True,16,'reduce','active',False)]
results=[]
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,width,js,font,motion,colors,touch in cases:
        ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion=motion,forced_colors=colors,has_touch=touch)
        if js:
            ctx.add_init_script("""window.__vitals={cls:0,lcp:null};
            new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__vitals.cls+=e.value;}).observe({type:'layout-shift',buffered:true});
            try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__vitals.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){};""")
        page=ctx.new_page();page.set_content(fixture,wait_until='load');
        if font!=16: page.evaluate('(size)=>document.documentElement.style.fontSize=size+"px"',font)
        # Real browser interaction/AX checks on the rendered original PHP output.
        assert page.locator('[data-fv-rights-annex]').count()==1,name
        assert page.locator('[data-fv-commercial-clearance="not-cleared"]').count()==9,name
        links=page.locator('[data-fv-rights-reviewed-link]')
        assert links.count()==9,name
        assert all((x.get_attribute('href') or '').startswith('https://www.nasa.gov/') for x in links.all()),name
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),name
        links.first.focus();assert links.first.evaluate('(a)=>document.activeElement===a'),name
        if touch:
            links.first.evaluate('(a)=>a.addEventListener("click",ev=>ev.preventDefault(),{once:true})')
            links.first.tap(timeout=2000,no_wait_after=True)
        tree=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        a=[n for n in tree if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
        names=[n.get('name',{}).get('value') for n in a]
        assert len(names)==9 and len(set(names))==9,name
        assert not page.locator('img,form,iframe,video,script').count(),name
        vitals=page.evaluate('window.__vitals||null') if js else None
        page.screenshot(path=str(OUT/(name+'.png')),full_page=False)
        results.append({'case':name,'width':width,'js':js,'font_px':font,'touch':touch,'forced_colors':colors,'reduced_motion':motion,'a11y_named_links':len(names),'horizontal_overflow':False,'local_fixture_vitals':vitals,'pass':True})
        ctx.close()
    ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
    page=ctx.new_page();page.set_content(fixture,wait_until='load');page.emulate_media(media='print')
    pdf=OUT/'source-custody-print.pdf';pdf.write_bytes(page.pdf(format='A4',print_background=True))
    ctx.close();browser.close()
printed=fitz.open(pdf)
links=set(l.get('uri') for pg in printed for l in pg.get_links() if (l.get('uri') or '').startswith('https://www.nasa.gov/'))
text=' '.join(pg.get_text() for pg in printed)
assert len(links)==9 and 'NOT CLEARED' in text and 'ignitions' in text
report={'pass':True,'browser':'Chromium system binary','cases':results,'pdf_pages':len(printed),'print_nasa_links':len(links),'limitations':['Fixtures via Playwright page.set_content; no installed WordPress/Assembler','No genuine axe-core, NVDA/VoiceOver, Firefox/WebKit','No browser-enforced HTTP response/CSP; no live CWV','No verified seller checkout or paid revenue']}
(OUT/'browser-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed_real_chromium_cases':len(results),'pdf_pages':len(printed),'pdf_sources':len(links),'lcp_ms':[x['local_fixture_vitals']['lcp'] for x in results if x['local_fixture_vitals']],'cls':[x['local_fixture_vitals']['cls'] for x in results if x['local_fixture_vitals']]},indent=2))
