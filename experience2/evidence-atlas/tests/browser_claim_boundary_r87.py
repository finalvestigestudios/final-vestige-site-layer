#!/usr/bin/env python3
"""Real Chromium acceptance for R87, file:// laboratory ONLY; no remote navigation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
import fitz

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experience2/evidence-atlas/tools'))
import build_claim_boundary_r87 as builder

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(src,out,axe=None):
    out.mkdir(parents=True,exist_ok=True)
    rows=builder.verify()
    errors=[];cases=[];shots={}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'],
            **({'executable_path':os.environ['APOLLO_CHROMIUM_BIN']} if os.getenv('APOLLO_CHROMIUM_BIN') else {}))
        for width in (320,390,768,1440,1920):
            for js in (False,True):
                context=browser.new_context(viewport={'width':width,'height':880},java_script_enabled=js,
                    reduced_motion='reduce' if width==390 else 'no-preference')
                page=context.new_page()
                requests=[];console=[]
                page.on('request', lambda r:requests.append('OUTSIDE_REQUEST') if r.url.startswith(('https:','http:')) else None)
                page.on('pageerror',lambda err:console.append('PAGE_ERROR'))
                if js:
                    page.add_init_script("""window.__r87perf={lcp:0,cls:0};
                        try{new PerformanceObserver(l=>l.getEntries().forEach(x=>window.__r87perf.lcp=x.startTime)).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
                        try{new PerformanceObserver(l=>l.getEntries().forEach(x=>{if(!x.hadRecentInput)window.__r87perf.cls+=x.value})).observe({type:'layout-shift',buffered:true})}catch(e){}""")
                page.goto((src/'R87_CLAIM_PHOTO_BOUNDARY.html').resolve().as_uri())
                assert page.locator('.finding').count()==6,'R87_SIX_FINDINGS'
                assert page.locator('.source-pair').count()==6,'R87_SIX_SOURCE_PAIRS'
                assert page.locator('img,picture,iframe,video,[data-lat],[data-lon],[data-geo-edge]').count()==0,'R87_MEDIA_GEO'
                assert page.locator('.source').evaluate_all('(a)=>a.map(x=>x.href)') == [v for r in rows for v in (r['research_url'],r['photo_url'])], 'R87_SOURCE_IDENTITY'
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 2'),'R87_DOCUMENT_OVERFLOW'
                assert not requests and not console,'R87_NETWORK_OR_SCRIPT_ERRORS'
                assert 'STAGING HOLD' in page.locator('.hold').inner_text(),'R87_HOLD_NOT_VISIBLE'
                page.locator('.finding summary').first.focus();page.keyboard.press('Enter')
                assert page.locator('.finding details').first.evaluate('(e)=>e.open'),'R87_NATIVE_OPEN'
                page.keyboard.press('Enter')
                assert not page.locator('.finding details').first.evaluate('(e)=>e.open'),'R87_NATIVE_CLOSE'
                page.locator('.jump a').nth(3).click()
                assert page.evaluate('location.hash')=='#r87-04','R87_ANCHOR'
                bounds=page.locator('.source').evaluate_all('(a)=>a.map(x=>({w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height}))')
                assert all(b['w']>=44 and b['h']>=44 for b in bounds),'R87_TOUCH_44'
                assert page.locator('.finding').first.evaluate('(x)=>getComputedStyle(x).backgroundColor')!='rgba(0, 0, 0, 0)','R87_CSS_UNLOADED'
                case={'width':width,'js':js,'no_overflow':True,'native_keyboard':True,
                      'touch_44px':True,'axe_violations':None,'lab_lcp_ms':None,'lab_cls':None}
                if js:
                    if axe:
                        page.add_script_tag(path=str(axe))
                        report=page.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                            return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passed:r.passes.length}}""")
                        case['axe_violations']=report['violations'];case['axe_rules_passed']=report['passed']
                        errors.extend(report['violations'])
                    page.wait_for_timeout(150)
                    perf=page.evaluate('window.__r87perf')
                    case['lab_lcp_ms']=perf['lcp'];case['lab_cls']=perf['cls']
                    assert perf['cls']<=0.1,'R87_CLS_LAB'
                if js and width in (390,1440):
                    screenshot=out/f'R87_BOUNDARY_{width}.png'
                    page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
                    shots[str(width)]=sha(screenshot)
                    if width==1440:
                        pdf=out/'R87_BOUNDARY_PRINT.pdf'
                        page.pdf(path=str(pdf),format='A4',print_background=True)
                        with fitz.open(pdf) as doc:
                            paper=''.join(page.get_text() for page in doc)
                            text=''.join(paper.split())
                            assert all(''.join(x.split()) in text for x in
                                {r[k] for r in rows for k in ('research_url','photo_url')}),'R87_PRINT_URLS'
                            assert all(''.join(r['catalog'].split()) in text for r in rows),'R87_PRINT_CATALOGS'
                            assert 'STAGINGHOLD' in text,'R87_PRINT_HOLD'
                            case['pdf_pages']=len(doc)
                        page.emulate_media(media='print')
                        contrast=page.evaluate("""()=>({hold_fg:getComputedStyle(document.querySelector('.hold')).color,
                            hold_bg:getComputedStyle(document.querySelector('.hold')).backgroundColor,
                            link_fg:getComputedStyle(document.querySelector('.source')).color})""")
                        assert contrast=={'hold_fg':'rgb(0, 0, 0)',
                            'hold_bg':'rgb(255, 255, 255)','link_fg':'rgb(0, 0, 0)'},'R87_PRINT_CONTRAST'
                cases.append(case)
                context.close()
        context=browser.new_context(viewport={'width':390,'height':850},forced_colors='active',reduced_motion='reduce')
        page=context.new_page();page.goto((src/'R87_CLAIM_PHOTO_BOUNDARY.html').resolve().as_uri())
        page.locator('summary').first.focus();page.keyboard.press('Enter')
        assert page.locator('details').first.evaluate('(x)=>x.open'),'R87_FORCED_KEYBOARD'
        shot=out/'R87_FORCED_390.png';page.screenshot(path=str(shot),full_page=True)
        shots['forced_390']=sha(shot);context.close();browser.close()
    assert not errors,'R87_AXE_VIOLATIONS'
    result={'schema':'fv.apollo.r87.chromium-qa.v1','release':'STAGING_HOLD','cases':cases,
            'axe_gate':'PASS' if axe else 'NOT_RUN_LOCAL', 'screenshots_sha256':shots,
            'photo_rights_cleared':0,'hosted_wp_tested':False,'production_cwv':False,
            'site_writes':False}
    (out/'R87_BROWSER_RECEIPT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--src',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--axe',type=Path)
    a=p.parse_args();print('R87 browser cases',len(run(a.src,a.out,a.axe)['cases']))
