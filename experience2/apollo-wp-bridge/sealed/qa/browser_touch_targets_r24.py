#!/usr/bin/env python3
"""Real Chromium/Playwright staging QA: 79 undersized Apollo anchors repaired.

Measures the *actual* generated PHP preview (rendered through a local PHP
WordPress-function shim) via page.set_content. Not axe, WP staging, or browser
HTTP-navigation/CSP certification. Captures reproducible evidence and receipts.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from browser_exact import get_fixture
from touch_targets_r24 import SELECTORS
OUT=HERE/'r24-screenshots'
OUT.mkdir(parents=True,exist_ok=True)
RESULT=HERE/'R24_TOUCH_BROWSER_RESULTS.json'
WIDTHS=(320,360,390,768,1024,1440,1920)
MEASURE="""(selectors) => {
 const elems = [...document.querySelectorAll(selectors.join(','))];
 const visible = elems.map(e => {
    const r=e.getBoundingClientRect();const css=getComputedStyle(e);
    return {html:e.tagName, height:r.height, width:r.width,
      text:(e.textContent||'').trim().slice(0,70),
      id:e.id, visible:r.width>0 && r.height>0 && css.display!=='none' && css.visibility!=='hidden'}
 }).filter(e=>e.visible);
 return {total:visible.length, under44:visible.filter(e=>e.height<43.99),
         under24:visible.filter(e=>e.width<23.99),
         minHeight:Math.min(...visible.map(e=>e.height)),
         minWidth:Math.min(...visible.map(e=>e.width)),
         docWidth:document.documentElement.scrollWidth,
         viewport:document.documentElement.clientWidth};
}"""
PERF="""(() => { window._r24Perf={lcp:null,cls:0};
 try{new PerformanceObserver(x=>{for(const e of x.getEntries())window._r24Perf.lcp=e.startTime})
 .observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
 try{new PerformanceObserver(x=>{for(const e of x.getEntries())if(!e.hadRecentInput)window._r24Perf.cls+=e.value})
 .observe({type:'layout-shift',buffered:true})}catch(e){}
})()"""

def run():
    html, plugin_sha=get_fixture()
    report={'test_kind':'real Chromium Playwright, PHP CLI shim, in-memory HTML with meta CSP approximation',
       'release_scope':'STAGING_ONLY — NOT WordPress integration, HTTP header CSP, axe, or field CWV',
       'plugin_php_sha256':plugin_sha,'widths':[], 'screenshots':[],
       'keyboard':False,'touch':False,'no_js':False,'zoom_approximation':False,
       'axe_core':'NOT_RUN_VERIFIED_BUNDLE_MISSING'}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce' if width==320 else 'no-preference')
            page=ctx.new_page();errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(html,wait_until='load')
            page.evaluate(PERF)
            m=page.evaluate(MEASURE,list(SELECTORS))
            assert m['total']==79,(width,m['total'],'expected 79 pinned-source formerly short targets')
            assert m['minHeight']>=44 and not m['under44'],(width,m['under44'][:6])
            assert m['minWidth']>=24 and not m['under24'],(width,m['under24'][:6])
            assert m['docWidth']<=width+1,(width,m,'horizontal overflow')
            assert page.locator('input[type=radio]#fv-ex2-lens-1967').count()==1
            assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
            assert page.locator('[data-ex2-gallery-item]').count()==6
            assert page.locator('[data-ex2-atlas-item]').count()==6
            assert not errors,(width,errors)
            page.locator('.ex2-hero__actions .ex2-textlink').first.focus()
            a=page.locator('.ex2-hero__actions .ex2-textlink').first.evaluate('e=>({h:e.getBoundingClientRect().height,outline:getComputedStyle(e).outlineStyle,outlineWidth:getComputedStyle(e).outlineWidth})')
            assert a['h']>=44 and a['outline']!='none' and a['outlineWidth']=='3px',(width,a)
            if width in (390,1440):
                for label,sel in (('hero','.ex2-hero'),('source','#stage-01'),('gallery','#source-gallery')):
                    dest=OUT/f'r24-{label}-{width}.png'
                    page.locator(sel).screenshot(path=str(dest),animations='disabled')
                    report['screenshots'].append({'file':str(dest.relative_to(HERE)),
                          'sha256':sha256(dest.read_bytes()).hexdigest()})
            page.keyboard.press('Enter')
            assert page.evaluate('location.hash')=='#research-desk'
            report['keyboard']=True
            page.wait_for_timeout(160)
            perf=page.evaluate('window._r24Perf')
            report['widths'].append({'width':width, 'target_count':m['total'],
                      'small_touch_targets_after':len(m['under44']),
                      'small_24px_targets_after':len(m['under24']),
                      'min_height_px':round(m['minHeight'],2),
                      'min_width_px':round(m['minWidth'],2),
                      'doc_width_px':m['docWidth'], 'lab_lcp_ms':perf['lcp'],
                      'lab_cls':perf['cls'],'js_errors':errors})
            ctx.close()
        # Truly disabled JS (CSS native 1967 source filter + disclosures retain content).
        ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=ctx.new_page();page.set_content(html,wait_until='load')
        nojs=page.evaluate(MEASURE,list(SELECTORS))
        assert nojs['total']==79 and not nojs['under44']
        page.locator('#fv-ex2-lens-1967').check()
        assert page.locator('#source-concordance [data-concordance-record]:visible').count()==3
        page.locator('#fv-ex2-lens-all').check()
        assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
        page.locator('#source-01 summary').click()
        assert page.locator('#source-01').evaluate('(e)=>e.open')
        report['no_js']=True;ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1)
        page=ctx.new_page();page.set_content(html,wait_until='load')
        page.locator('#fv-ex2-lens-1966').tap()
        assert page.locator('[data-concordance-record]:visible').count()==1
        page.locator('#fv-ex2-lens-all').tap()
        assert page.locator('[data-concordance-record]:visible').count()==6
        report['touch']=True;ctx.close()
        # 200%-equivalent CSS zoom/reflow probe: simulation, NOT actual OS zoom.
        ctx=browser.new_context(viewport={'width':640,'height':850})
        page=ctx.new_page();page.set_content(html,wait_until='load')
        page.evaluate('document.documentElement.style.zoom="2"')
        report['zoom_approximation']={'zoom_factor':2,'viewport':640,'doc_width':page.evaluate('document.documentElement.scrollWidth')}
        assert page.evaluate('document.documentElement.scrollWidth')<=641,report['zoom_approximation']
        ctx.close();browser.close()
    RESULT.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R24_CHROMIUM_PASS: 7 widths x 79 links >=44px; noJS/touch/keyboard; zero overflow; screenshots', len(report['screenshots']))
    return report

if __name__=='__main__':run()
