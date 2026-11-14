"""Real Chromium QA of PHP-generated fixture via set_content; no installed WP/axe/HTTP claims."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT = Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
HTML=(QA/'fixture.html').read_text(encoding='utf8')
CASES=[('nojs-320',320,False,False,False,False,16),('touch-390',390,True,True,False,False,16),('keyboard-768',768,True,False,False,False,16),('desktop-1440',1440,True,False,False,False,16),('forced-1920',1920,True,False,False,True,16),('zoom-320',320,True,False,True,False,64),('tablet-1024',1024,True,False,False,False,16)]
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for name,width,js,touch,reduced,forced,root in CASES:
        context=browser.new_context(viewport={'width':width,'height':800},is_mobile=touch,has_touch=touch,java_script_enabled=js,reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
        page=context.new_page()
        if js:
            page.evaluate("""() => { window.__fvMetrics={lcp:[],cls:0};
              new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__fvMetrics.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
              new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__fvMetrics.cls+=e.value}).observe({type:'layout-shift',buffered:true});
            }""")
        page.set_content(HTML,wait_until='load')
        if root!=16: page.add_style_tag(content=f'html{{font-size:{root}px!important}}')
        cards=page.locator('[data-fv-source-drawer]').count()
        sources=page.locator('a[data-fv-nasa-source]').count()
        ctas=page.locator('a[data-fv-free-cta]').count()
        assert cards==4 and sources==4 and ctas==1,(name,cards,sources,ctas)
        assert page.locator('img,form,iframe,canvas,script').count()==0,name
        assert page.locator('[data-fv-withheld]').count()==0,name
        assert page.locator('[data-fv-nasa-source]').first.get_attribute('href').startswith('https://www.nasa.gov/'),name
        assert len(set(page.locator('h3[id]').evaluate_all('(nodes)=>nodes.map(n=>n.id)')))==4,name
        assert all(page.locator('a[data-fv-nasa-source]').nth(i).get_attribute('aria-label') or page.locator('a[data-fv-nasa-source]').nth(i).text_content().strip() for i in range(4)),name
        if js:
            summary=page.locator('summary').first
            summary.focus();page.keyboard.press('Enter')
            assert page.locator('details').first.get_attribute('open') is not None,name+' keyboard open'
            page.keyboard.press('Enter')
            assert page.locator('details').first.get_attribute('open') is None,name+' keyboard close'
            if touch:
                summary.tap();assert page.locator('details').first.get_attribute('open') is not None,name+' touch open'
            # Native details hide/show their disclosure without javascript handlers.
        else:
            # no-JS still exposes the facts, headings, summaries and optional sources
            assert page.locator('h3').filter(has_text='102 deliberate Command Module ignitions').count()==1,name
        sizes=page.evaluate('''()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,body:document.body.scrollWidth})''')
        assert sizes['sw']<=sizes['cw']+1,(name,sizes)
        if name in ('desktop-1440','zoom-320','nojs-320','touch-390','forced-1920'):
            page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
        if js: page.wait_for_timeout(170)
        metric=page.evaluate('window.__fvMetrics') if js else None
        results.append({'lcp_ms':round(max(metric['lcp'])) if metric and metric['lcp'] else None,'cls':metric['cls'] if metric else None,'name':name,'viewport':width,'js':js,'touch':touch,'root_px':root,'source_drawers':cards,'source_links':sources,'cta':ctas,'overflow_px':max(0,sizes['sw']-sizes['cw']),'pass':True})
        context.close()
    ctx=browser.new_context(viewport={'width':1000,'height':800});pg=ctx.new_page();pg.set_content(HTML);pg.pdf(path=str(QA/'source-chronology-print.pdf'),format='A4',print_background=True);ctx.close();browser.close()
from subprocess import run
from shutil import which
if which('pdftotext'):
    pdf=run(['pdftotext',str(QA/'source-chronology-print.pdf'),'-'],capture_output=True,text=True,check=True).stdout
    assert pdf.count('Read the NASA source')==4,'print lost NASA links behind native closed details'
(QA/'browser-results.json').write_text(json.dumps({'browser':'Chromium /usr/bin/chromium','conditions':results,'axe_core':'NOT_EXECUTED','http_csp':'NOT_EXECUTED','wp_installed':False,'production_cwv':False},indent=2)+'\n')
print(json.dumps({'passed':len(results),'widths':[x['viewport'] for x in results],'http_csp':False,'axe_core':False},indent=2))
