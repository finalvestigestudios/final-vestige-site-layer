#!/usr/bin/env python3
"""Real Playwright Chromium fixture tests; never installed WordPress acceptance."""
import hashlib
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from topology import verify_page, verify_semantic_page

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'; QA.mkdir(parents=True,exist_ok=True)
FIXTURE=QA/'local-php-fixture.html'
if not FIXTURE.is_file():
    raise SystemExit('HOLD: generate local-php-fixture.html from reviewed R389 PHP contract')
html=FIXTURE.read_text(encoding='utf8')
report={'kind':'REAL_CHROMIUM_LOCAL_PHP_FIXTURE_NOT_WORDPRESS_STAGING',
        'fixture_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        'assertions':0,'viewports':[],'adversarial':[],
        'axe_core':'NOT RUN - real pinned axe-core bundle unavailable',
        'lcp_cls':'Chromium PerformanceObserver on local page.set_content, not field CWV or installed staging',
        'release_allowed':False}

def check(x,why):
    report['assertions']+=1
    if not x: raise AssertionError(why)

modes=[('320-mobile',320,780,True,False,'no-preference','none',False),
 ('390-mobile',390,850,True,False,'no-preference','none',False),
 ('768-tablet',768,900,False,False,'no-preference','none',False),
 ('1440-desktop',1440,900,False,False,'no-preference','none',False),
 ('1920-wide',1920,1080,False,False,'no-preference','none',False),
 ('320-nojs',320,800,True,True,'no-preference','none',False),
 ('390-touch',390,850,True,False,'no-preference','none',True),
 ('390-reduced',390,850,True,False,'reduce','none',False),
 ('320-forced',320,850,True,False,'no-preference','active',False),
 ('320-root4x',320,900,True,False,'no-preference','none',False)]
# These all pass R392's count/membership test, but disconnect proof from its
# chronological phase, source index, accessible name, or actual reader access.
mutations=[
 ('misdated_postfire_tests', '''let phases=document.querySelectorAll('.fv-r384__phase');phases[1].querySelector('.fv-r384__grid').append(phases[2].querySelector('[data-fv-r384-record]'));''','phase_2_membership'),
 ('ignition_in_event', '''let phases=document.querySelectorAll('.fv-r384__phase');phases[0].querySelector('.fv-r384__grid').append(phases[1].querySelector('[data-fv-r384-record]'));''','phase_1_membership'),
 ('swap_source_index_links', '''let a=document.querySelectorAll('.fv-r384__source-index a[href^="#"]');let t=a[0].getAttribute('href');a[0].setAttribute('href',a[1].getAttribute('href'));a[1].setAttribute('href',t);''','publication_1_link_order_and_labels'),
 ('swap_rail_destinations', '''let a=document.querySelectorAll('.fv-r384__rail a');let t=a[0].getAttribute('href');a[0].setAttribute('href',a[2].getAttribute('href'));a[2].setAttribute('href',t);''','chronology_rail_sequence_and_labels'),
 ('misnamed_source_index_item', '''document.querySelector('.fv-r384__source-index a[href^="#"]').textContent='Question 1 · Fake astronaut quote';''','publication_1_link_order_and_labels'),
 ('hidden_checkout_bridge', '''document.querySelector('[data-fv-free-cta]').setAttribute('hidden','');''','free_cta_operability'),
 ('aria_hidden_gallery', '''document.querySelector('[data-fv-r384-gallery]').setAttribute('aria-hidden','true');''','free_cta_operability'),
 ('missing_gallery_heading_linkage', '''document.querySelector('[data-fv-r384-gallery]').setAttribute('aria-labelledby','invisible-heading');''','gallery_accessible_heading'),
 ('publication_B_in_A', '''let a=document.querySelectorAll('.fv-r384__source-group');a[0].querySelector('.fv-r384__citation').append(a[1].querySelector('[data-fv-r384-publication]'));''','publication_group_custody'),
 ('inert_evidence_card', '''document.querySelector('[data-fv-r384-record]').inert=true;''','record_1_accessible_visibility'),
 ('pointer_disabled_cta', '''document.querySelector('[data-fv-free-cta]').style.pointerEvents='none';''','free_cta_operability'),
 ('mislabelled_phase', '''document.querySelector('.fv-r384__phase').setAttribute('aria-labelledby','fv-r384-1-finding-heading');''','phase_1_accessible_heading')]

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    try:
        for name,w,h,mobile,nojs,reduced,forced,touch in modes:
            ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=(mobile or touch),
                java_script_enabled=not nojs,reduced_motion=reduced,forced_colors=forced)
            page=ctx.new_page()
            page.evaluate('''() => { window.__fvFixtureVitals={lcp_ms:null,cls:0};
              new PerformanceObserver(list=>{for(const e of list.getEntries())
                window.__fvFixtureVitals.lcp_ms=e.startTime;})
                .observe({type:'largest-contentful-paint',buffered:true});
              new PerformanceObserver(list=>{for(const e of list.getEntries())
                if(!e.hadRecentInput)window.__fvFixtureVitals.cls+=e.value;})
                .observe({type:'layout-shift',buffered:true});
            }''')
            page.set_content(html)
            page.wait_for_timeout(120)
            if name=='320-root4x':page.add_style_tag(content='html{font-size:400%!important}')
            valid,errors=verify_page(page)
            check(valid,name+': '+str(errors))
            check(page.locator('[data-fv-r384-record]').count()==6,name+': six cards')
            check(not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),name+': overflow')
            if name=='390-touch':
                page.locator('summary').first.tap()
                check(page.locator('details').first.evaluate('(e)=>e.open'),'touch opens native source drawer')
            if name=='1440-desktop':
                page.locator('summary').first.focus();page.keyboard.press('Enter')
                check(page.locator('details').first.evaluate('(e)=>e.open'),'keyboard opens drawer')
                page.keyboard.press('Enter')
                check(not page.locator('details').first.evaluate('(e)=>e.open'),'keyboard closes drawer')
                tree=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
                check(any(n.get('role',{}).get('value')=='link' and not n.get('ignored') for n in tree),'AX tree contains exposed links')
            if name=='320-nojs':
                page.locator('summary').first.tap()
                check(page.locator('details').first.evaluate('(e)=>e.open'),'no-JS native drawer works')
            if name in ('320-mobile','1440-desktop','320-nojs'):
                page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
            vitals=page.evaluate('window.__fvFixtureVitals')
            report['viewports'].append({'name':name,'width':w,'pass':True,'fixture_only':True,
                                          'lcp_ms':vitals['lcp_ms'],'cls':round(vitals['cls'],6)})
            ctx.close()
        ctx=browser.new_context();page=ctx.new_page()
        for name,mutate,code in mutations:
            page.set_content(html)
            page.evaluate('() => {'+mutate+'}')
            old_ok,old_errors=verify_semantic_page(page)
            check(old_ok,name+': must expose bypass in R392 '+str(old_errors))
            ok,errors=verify_page(page)
            check(not ok and code in errors,name+': R393 must detect '+str(errors))
            report['adversarial'].append({'case':name,'R392_count_text_check':'PASS despite tamper',
                                           'R393_topology_gate':'BLOCKED', 'code':code})
        ctx.close()
    finally:
        browser.close()
(QA/'topology-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'contexts':len(modes),'mutations':len(mutations),'assertions':report['assertions'],
                  'kind':report['kind']},indent=2))
