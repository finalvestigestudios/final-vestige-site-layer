#!/usr/bin/env python3
"""R416 real Chromium, original R415 PHP fixture. No page navigation or claim of axe/CWV."""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from journey_acceptance import render_fixture, inspect_markup, release_gate

ROOT = Path(__file__).resolve().parents[1]
QA=ROOT/'QA'; SHOTS=QA/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)
HTML=render_fixture()
REPORT={'runtime':'chromium page.set_content on actual R415 PHP-rendered offline fixture',
        'state':'NOT_EXECUTED','check_methods':[],'screenshots':[],
        'responsive':[],'axe_core':'NOT_EXECUTED — dependency unavailable',
        'navigated_LCP':'NOT_MEASURED — browser navigation administratively blocked',
        'navigated_CLS':'NOT_MEASURED — browser navigation administratively blocked',
        'WordPress_staging':'NOT_TESTED','real_user_p75_CWV':'NOT_MEASURED'}

def run():
    dom=inspect_markup(HTML)
    assert dom['status']=='PASS',dom
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        def new_page(w=390,h=900,**kw):
            ctx=browser.new_context(viewport={'width':w,'height':h},**kw)
            p=ctx.new_page()
            p.set_content(HTML,wait_until='load')
            return ctx,p
        def test(name,call):
            call();REPORT['check_methods'].append(name)
        def layout():
            for width in (320,360,390,768,1024,1440,1920):
                ctx,p=new_page(width)
                metrics=p.evaluate('''()=>({width:innerWidth,document_width:document.documentElement.scrollWidth,
                  cards:[...document.querySelectorAll('.fv-r414__card')].map(x=>Math.round(x.getBoundingClientRect().width)),
                  overflow_elements:[...document.querySelectorAll('.fv-r415 *')].filter(x=>{let r=x.getBoundingClientRect();return r.width>0&&(r.left< -2||r.right>innerWidth+2)}).length})''')
                assert metrics['document_width']<=width+1,metrics
                assert len(metrics['cards'])==12 and min(metrics['cards'])>=160,metrics
                assert p.locator('[data-fv-r415-journey]').count()==2
                name=f'{width}.png';p.screenshot(path=str(SHOTS/name),full_page=True)
                REPORT['responsive'].append(metrics);REPORT['screenshots'].append(name);ctx.close()
        test('320-1920 layout, source cards and screenshot series',layout)
        def keyboard():
            ctx,p=new_page(390)
            d=p.locator('.fv-r414__card details').first
            summary=d.locator('summary')
            summary.focus();p.keyboard.press('Enter');assert d.evaluate('(e)=>e.open')
            p.keyboard.press('Space');assert not d.evaluate('(e)=>e.open')
            # The native disclosure must remain functional without scripted event handlers.
            assert p.locator('script').count()==0
            name='390-keyboard.png';p.screenshot(path=str(SHOTS/name),full_page=True)
            REPORT['screenshots'].append(name);ctx.close()
        test('keyboard-native-disclosures',keyboard)
        def nojs():
            ctx,p=new_page(390,900,java_script_enabled=False)
            d=p.locator('.fv-r414__card details').first
            d.locator('summary').focus();p.keyboard.press('Enter')
            assert d.evaluate('(e)=>e.open')
            assert p.locator('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==2
            name='390-nojs.png';p.screenshot(path=str(SHOTS/name),full_page=True)
            REPORT['screenshots'].append(name);ctx.close()
        test('nojs-expanded-source-and-one-CTA-per-instance',nojs)
        def touch():
            ctx,p=new_page(390,844,has_touch=True,is_mobile=True,reduced_motion='reduce')
            disclosure=p.locator('.fv-r414__card details').first
            disclosure.locator('summary').tap();assert disclosure.evaluate('(e)=>e.open')
            p.locator('.fv-r415__nav a').first.tap()
            assert p.evaluate('location.hash')=='#fv-r415-1-chronology'
            name='390-touch-reduced.png';p.screenshot(path=str(SHOTS/name),full_page=True)
            REPORT['screenshots'].append(name);ctx.close()
        test('touch-navigation-reduced-motion',touch)
        def zoom_and_colors():
            ctx,p=new_page(320,900,forced_colors='active')
            p.evaluate('document.documentElement.style.fontSize="64px"')
            metrics=p.evaluate('''()=>({width:innerWidth,doc:document.documentElement.scrollWidth,
                        cards:[...document.querySelectorAll('.fv-r414__card')].map(e=>e.getBoundingClientRect().width)})''')
            assert metrics['doc']<=metrics['width']+1,metrics
            assert min(metrics['cards'])>=160,metrics
            name='320-4x-forced-colors.png';p.screenshot(path=str(SHOTS/name),full_page=True)
            REPORT['screenshots'].append(name);ctx.close()
        test('400pct-root-font-and-forced-colors',zoom_and_colors)
        def aria_structures():
            ctx,p=new_page(390)
            assert p.locator('.fv-r415__rail li').count()==6
            assert p.locator('.fv-r414__card').count()==12
            assert p.locator('[aria-labelledby]').count()>=4
            ids=p.locator('[id]').evaluate_all('(arr)=>arr.map(x=>x.id)')
            assert len(ids)==len(set(ids))
            # Real browser accessibility tree via Chrome DevTools Protocol; NOT an axe-core scan.
            cdp=ctx.new_cdp_session(p)
            tree=cdp.send('Accessibility.getFullAXTree')['nodes']
            named=[n for n in tree if n.get('name',{}).get('value')]
            assert len(named)>45,len(named)
            REPORT['ax_tree']={'method':'Chrome DevTools Protocol Accessibility.getFullAXTree',
                               'node_count':len(tree),'named_node_count':len(named),
                               'not_equivalent_to_axe':True}
            ctx.close()
        test('CDP-browser-accessibility-tree-and-no-duplicate-IDs',aria_structures)
        browser.close()
    REPORT['state']='FIXTURE_PASS'
    REPORT['release']=release_gate(dom,REPORT)
    (QA/'browser_results.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(f"R416 browser: {len(REPORT['check_methods'])}/{len(REPORT['check_methods'])} methods PASS, {len(REPORT['screenshots'])} captures; production HARD_HOLD")

if __name__=='__main__':
    try:run()
    except Exception as err:
        REPORT['state']='FIXTURE_FAIL';REPORT['error']=str(err)
        (QA/'browser_results.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True)+'\n')
        raise
