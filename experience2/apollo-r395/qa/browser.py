#!/usr/bin/env python3
"""R395 Chromium-first-paint regression, not WordPress staging acceptance.

Reuses exact PHP-generated R393 fixture and reviewed R384 CSS. The R394
mobile-fit patch is loaded in the *initial* head, not injected after paint.
Offline page.set_content() intentionally performs no network requests.
"""
from __future__ import annotations
import sys, hashlib, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parents[1]
E=HERE.parent
QA=HERE/'QA'; QA.mkdir(exist_ok=True)
FIXTURE=E/'apollo-r393/QA/local-php-fixture.html'
FIT=HERE/'assets/mobile-fit.css'
BASE=E/'apollo-r384/assets/gallery.css'
sys.path[:0]=[str(E/'apollo-r394/qa'),str(E/'apollo-r393/qa'),str(E/'apollo-r392/qa')]
from visibility_custody import verify_page as verify_visibility
from topology import verify_page as verify_topology

BASE_SHA='4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9'
FIT_SHA='93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756'
FIXTURE_SHA='5242da6c49b64d7f37484b6f5924042a69872073e4fd15d9a0ed694920bb11eb'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
for path,want in [(BASE,BASE_SHA),(FIT,FIT_SHA),(FIXTURE,FIXTURE_SHA)]:
    if digest(path)!=want: raise SystemExit(f'HARD HOLD: source altered {path}')

fixture=FIXTURE.read_text(encoding='utf8')
fit=FIT.read_text(encoding='utf8')
# Observer registration is parser-executed before the gallery markup. Note that
# page.set_content cannot emulate real HTTP, caching or CSP behavior.
perf='''<script>window.__r395={cls:0,lcp:null,shifts:[]};try{
 new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput){window.__r395.cls+=e.value;window.__r395.shifts.push(e.value)}}).observe({type:'layout-shift',buffered:true});
 new PerformanceObserver(l=>{for(const e of l.getEntries())window.__r395.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
}catch(e){window.__r395.error=String(e)}</script>'''

def head_markup(root4=False,fit_initial=True):
    additions=("<style id='r395-root'>html{font-size:400%!important}</style>" if root4 else '')
    if fit_initial: additions+='<style media="screen" id="r395-reviewed-mobile-fit">'+fit+'</style>'
    return fixture.replace('</head>', additions+'</head>',1).replace('<head>','<head>'+perf,1)

report={'scope':'LOCAL_CHROMIUM_PHP_FIXTURE_NOT_INSTALLED_WORDPRESS',
 'baseline_sha256':BASE_SHA,'fit_sha256':FIT_SHA,'fixture_sha256':FIXTURE_SHA,
 'tests':0,'contexts':[], 'axe_core':'NOT_RUN: reviewed genuine axe build unavailable',
 'network':'PAGE_SET_CONTENT_ONLY', 'release_allowed':False}

def require(cond,label):
    report['tests']+=1
    if not cond: raise AssertionError(label)

contexts=[
 ('320-mobile',320,780,False,False,'no-preference','none',False),
 ('390-mobile',390,850,False,False,'no-preference','none',False),
 ('768-tablet',768,900,False,False,'no-preference','none',False),
 ('1440-desktop',1440,900,False,False,'no-preference','none',False),
 ('1920-wide',1920,1080,False,False,'no-preference','none',False),
 ('320-nojs',320,800,False,True,'no-preference','none',False),
 ('390-touch',390,850,True,False,'no-preference','none',False),
 ('390-reduced',390,850,False,False,'reduce','none',False),
 ('320-forced',320,850,False,False,'no-preference','active',False),
 ('320-root4x-prepaint',320,900,False,False,'no-preference','none',True),
 ('390-root4x-prepaint',390,900,False,False,'no-preference','none',True),
]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    try:
        for name,w,h,touch,nojs,motion,colors,root4 in contexts:
            ctx=browser.new_context(viewport={'width':w,'height':h},has_touch=touch,
                 java_script_enabled=not nojs, reduced_motion=motion,forced_colors=colors)
            page=ctx.new_page()
            page.set_content(head_markup(root4),wait_until='load')
            page.wait_for_timeout(240)
            o1,c1=verify_topology(page); o2,c2=verify_visibility(page)
            require(o1 and o2,f'{name}: NASA custody {c1+c2}')
            require(page.locator('.fv-r384__card').count()==6,f'{name}: cards')
            require(page.locator('[data-fv-r384-publication]').count()==2,f'{name}: sources')
            require(page.locator('details').count()==6,f'{name}: no-JS native drawers')
            require(page.locator('[data-fv-free-cta]').count()==1,f'{name}: one free CTA')
            overflow=page.evaluate('document.documentElement.scrollWidth-window.innerWidth')
            require(overflow<=1,f'{name}: horizontal overflow {overflow}px')
            # Confirm this CSS is already in document HEAD before the body; never
            # a post-paint inject. A real staging header/network test remains open.
            require(page.locator('head style#r395-reviewed-mobile-fit').count()==1,f'{name}: CSS in initial head')
            require(page.locator('.fv-r384__source-index').is_visible(),f'{name}: source index visible')
            require(page.locator('[data-fv-free-cta]').is_visible(),f'{name}: free CTA visible')
            # Native details operate by keyboard even when JS is disabled.
            summ=page.locator('details summary').first
            summ.focus()
            page.keyboard.press('Enter')
            require(page.locator('details').first.get_attribute('open') is not None,f'{name}: Enter opens details')
            page.keyboard.press('Enter')
            require(page.locator('details').first.get_attribute('open') is None,f'{name}: Enter closes details')
            # Touch interaction on native summary; no JS event controller.
            if touch:
                summ.tap()
                require(page.locator('details').first.get_attribute('open') is not None,f'{name}: touch opens details')
            if root4:
                fs=float(page.evaluate('getComputedStyle(document.documentElement).fontSize').replace('px',''))
                require(fs>=60,f'{name}: reader 400% font preserved {fs}')
            if name in ('320-mobile','1440-desktop','320-nojs','320-root4x-prepaint'):
                page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
            perfdata=(page.evaluate('window.__r395') if not nojs else None)
            if perfdata and perfdata['cls'] is not None:
                require(perfdata['cls']<=0.1,f'{name}: prepaint fixture CLS {perfdata["cls"]}')
            report['contexts'].append({'name':name,'width':w,'root4x':root4,'nojs':nojs,
                'overflow_px':max(overflow,0),'source_pass':o1 and o2,
                'fixture_cls':None if not perfdata else perfdata['cls'],
                'fixture_lcp_ms':None if not perfdata else perfdata['lcp']})
            ctx.close()
        # Explicitly replicate R394's previous late patch strategy as comparison,
        # demonstrating why before-first-paint matters. The result is diagnostic.
        ctx=browser.new_context(viewport={'width':320,'height':900})
        pg=ctx.new_page();pg.set_content(head_markup(root4=True,fit_initial=False),wait_until='load')
        pg.wait_for_timeout(250)
        report['late_patch_before_overflow_px']=pg.evaluate('document.documentElement.scrollWidth-innerWidth')
        require(report['late_patch_before_overflow_px']>1,'late-style comparison must reproduce overflow')
        pg.add_style_tag(content=fit)
        pg.wait_for_timeout(250)
        report['late_patch_after_overflow_px']=pg.evaluate('document.documentElement.scrollWidth-innerWidth')
        report['late_patch_fixture_cls']=pg.evaluate('window.__r395.cls')
        require(report['late_patch_after_overflow_px']<=1,'late patch fixes overflow')
        ctx.close()
    finally:browser.close()
report['status']='PASS_LOCAL_ONLY'
(QA/'prepaint-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'status':report['status'],'tests':report['tests'],'contexts':len(report['contexts']),
  'late_cls':report['late_patch_fixture_cls'],'max_prepaint_cls':max(c['fixture_cls'] or 0 for c in report['contexts'])}))
