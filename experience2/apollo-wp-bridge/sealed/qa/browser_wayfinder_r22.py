#!/usr/bin/env python3
"""Real Chromium Playwright evidence navigation, source status and visual QA.

`page.set_content` uses the exact, hash-checked PHP WordPress *stub* output;
this is NOT real WordPress, HTTP CSP, axe-core or production Core Web Vitals.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_exact import get_fixture, INIT

HERE=Path(__file__).resolve().parent
OUT=HERE/'r22-screenshots'
WIDTHS=(320,360,390,768,1024,1440,1920)

# Browser-computed WCAG relative-luminance arithmetic against the fixed opaque
# backgrounds of the R22 wayfinder only. Not a substitute for full axe checks.
CONTRAST_JS=r'''() => {
const parse=c=>{let m=c.match(/rgba?\(([^)]+)\)/);if(!m)return null;let a=m[1].replace(/,/g,' ').replace(/\//g,' ').split(/\s+/).filter(Boolean).map(Number);return a};
const lum=a=>{let x=a.slice(0,3).map(n=>n/255).map(n=>n<=0.04045?n/12.92:((n+0.055)/1.055)**2.4);return .2126*x[0]+.7152*x[1]+.0722*x[2]};
const ratio=(a,b)=>{let [x,y]=[lum(a),lum(b)].sort((a,b)=>b-a);return (x+.05)/(y+.05)};
const row=[];const root=document.querySelector('#fv-ex2-wayfinder');
for(const el of root.querySelectorAll('h2,p,a,span')){
 let style=getComputedStyle(el),fg=parse(style.color);if(!fg||!el.innerText.trim()||!el.getClientRects().length)continue;
 let cur=el,bg=null,layer=[];while(cur&&cur!==document.documentElement){const computed=getComputedStyle(cur),col=parse(computed.backgroundColor);if(col&&col.length>=3&&((col.length<4)||col[3]>0.99)){bg=col;break}cur=cur.parentElement}
 if(!bg)throw Error('No opaque text background for '+el.tagName);
 row.push({tag:el.tagName,contrast:+ratio(fg,bg).toFixed(2),label:el.innerText.slice(0,55),foreground:style.color,background:bg.slice(0,3)});
}
return {evaluated:row.length,minimum:Math.min(...row.map(r=>r.contrast)),violations:row.filter(r=>r.contrast<4.5)};
}'''

def run():
    fixture,plugin_sha=get_fixture()
    OUT.mkdir(parents=True,exist_ok=True)
    report={'status':'PLAYWRIGHT_CHROMIUM_IN_MEMORY_PASS',
            'source_mode':'real PHP output; synthetic WP stub; Playwright page.set_content',
            'not_axe_or_real_wordpress':True,'not_field_web_vitals':True,
            'generated_php_sha256':plugin_sha,'responsive':[], 'screenshots':[],
            'touch':None,'no_js':None,'narrow_embedded':None}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            context=browser.new_context(viewport={'width':width,'height':930},
                     reduced_motion='reduce' if width==320 else 'no-preference',device_scale_factor=1)
            page=context.new_page();page.set_content(fixture,wait_until='load');page.evaluate(INIT)
            nav=page.locator('#fv-ex2-wayfinder')
            assert nav.count()==1 and nav.get_attribute('aria-labelledby')=='fv-ex2-wayfinder-title'
            assert nav.locator('a').count()==7
            targets=nav.locator('a').evaluate_all('(a)=>a.map(x=>x.getAttribute("href"))')
            assert len(set(targets))==7 and all(page.locator(t).count()==1 for t in targets),(width,targets)
            assert nav.locator('img,script,iframe').count()==0
            assert nav.locator('a').first.is_visible()
            card_sizes=nav.locator('a').evaluate_all('(a)=>a.map(x=>({w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height}))')
            assert min(x['w'] for x in card_sizes)>=240 or width<280,(width,card_sizes)
            assert min(x['h'] for x in card_sizes)>=100,(width,card_sizes)
            doc_width=page.evaluate('document.documentElement.scrollWidth')
            assert doc_width <= width+1,(width,doc_width)
            assert nav.locator('a').first.evaluate('(x)=>getComputedStyle(x).minHeight')=='106px'
            # Keyboard navigation and visible focus; native anchor jump works without JS.
            nav.locator('a').first.focus()
            assert nav.locator('a').first.evaluate('(x)=>x===document.activeElement')
            # Focus is also exercised by real keyboard Tab from the nav.
            page.keyboard.press('Tab')
            focused=page.evaluate('document.activeElement.getAttribute("href")')
            assert focused==targets[1],(width,focused)
            color=page.evaluate(CONTRAST_JS)
            page.wait_for_timeout(110)
            synthetic_cwv=page.evaluate("({lcp:window.__fv_cwv?.lcp??null,cls:window.__fv_cwv?.cls??null,shifts:window.__fv_cwv?.shifts??null})")
            assert color['evaluated']>=19 and not color['violations'],(width,color)
            # Reveal source year 1967, confirm navigation does not modify evidence filters.
            page.locator('#fv-ex2-lens-1967').check()
            visible=page.locator('#source-concordance [data-concordance-record]:visible').count()
            assert visible==3
            if width in (390,1440):
                nav.locator('a').first.focus()
                dest=OUT/f'r22-wayfinder-{width}.png'
                nav.screenshot(path=str(dest),animations='disabled',timeout=16000)
                report['screenshots'].append({'name':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
            report['responsive'].append({'width':width,'document_width':doc_width,'destinations':len(targets),
                                        'minimum_wayfinder_text_contrast':color['minimum'],
                                        'contrast_nodes_evaluated':color['evaluated'],
                                        'visible_1967_photo_records':visible,
                                        'in_memory_lcp_ms':synthetic_cwv['lcp'],
                                        'in_memory_cls':synthetic_cwv['cls'],
                                        'in_memory_layout_shifts':synthetic_cwv['shifts'],
                                        'cards_min_height':round(min(x['h'] for x in card_sizes),2),
                                        'keyboard_next_href':focused})
            context.close()
        ctx=browser.new_context(viewport={'width':390,'height':850},has_touch=True,is_mobile=True,
                               device_scale_factor=1)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        nav=page.locator('#fv-ex2-wayfinder')
        nav.locator('a[href="#source-gallery"]').tap()
        assert page.evaluate('location.hash')=='#source-gallery'
        assert page.locator('#source-gallery').count()==1
        report['touch']={'status':'PASS_TOUCH_TAP_NATIVE_ANCHOR','hash':'#source-gallery'}
        ctx.close()
        for width in (390,1920):
            ctx=browser.new_context(viewport={'width':width,'height':930},java_script_enabled=False)
            page=ctx.new_page();page.set_content(fixture,wait_until='load')
            nav=page.locator('#fv-ex2-wayfinder')
            assert nav.locator('a:visible').count()==7
            nav.locator('a[href="#fv-ex2-media-rights"]').click()
            assert page.evaluate('location.hash')=='#fv-ex2-media-rights'
            assert page.locator('#fv-ex2-media-rights').count()==1
            assert page.locator('#fv-ex2-media-rights [data-media-review]').count()==6
            assert page.locator('#source-concordance [data-concordance-record]:visible').count()==6
            report['no_js']={'status':'PASS_NATIVE_LINKS_NO_JS','widths':[390,1920],
                             'rights_holds':6,'all_sources_visible':6}
            ctx.close()
        ctx=browser.new_context(viewport={'width':1920,'height':930},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture)
        nav=page.locator('#fv-ex2-wayfinder')
        nav.evaluate('(x)=>{x.style.width="420px";x.style.maxWidth="420px"}')
        columns=nav.locator('ol').evaluate('(x)=>getComputedStyle(x).gridTemplateColumns.split(" ").length')
        assert columns==1,columns
        report['narrow_embedded']={'width':420,'columns':columns,'no_js':True}
        ctx.close();browser.close()
    (HERE/'R22_WAYFINDER_BROWSER_RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('R22_WAYFINDER_BROWSER_PASS',len(report['responsive']),'widths',len(report['screenshots']),'screenshots',
          'minimum contrast',min(a['minimum_wayfinder_text_contrast'] for a in report['responsive']))
    return report

if __name__=='__main__':run()
