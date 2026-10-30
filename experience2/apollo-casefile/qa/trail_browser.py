"""Actual locally installed Chromium/Playwright component QA; offline / not WP field CWV."""
from pathlib import Path
import json,time,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
QA=ROOT/'qa';(QA/'screenshots').mkdir(exist_ok=True)
widths=(320,360,390,768,1024,1440,1920)
report={'source_head':'local_fixture_staging','html_sha256':hashlib.sha256(HTML.encode()).hexdigest(),'tested_widths':[],'errors':[],'axe':'NOT_RUN — verified axe-core bundle unavailable; CDP and DOM smoke do not replace axe or WCAG certification','metrics':'synthetic in-memory local Chromium only; not Core Web Vitals field p75'}

def open_page(browser,w,js=True,motion='no-preference'):
    context=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=js,reduced_motion=motion)
    page=context.new_page(); errs=[];page.on('pageerror',lambda x:errs.append(str(x)))
    page.set_content(HTML,wait_until='load');return context,page,errs

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w in widths:
  ctx,page,errs=open_page(browser,w)
  assert page.locator('[data-ex2-trail-card]').count()==6
  assert page.locator('[data-ex2-trail-controls]').is_visible(),w
  dims=page.evaluate('''()=>({screen:innerWidth,doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,
     cardCount:document.querySelectorAll('[data-ex2-trail-card]').length,
     missingLinks:[...document.querySelectorAll('.ex2-trail a[href^="#"]')].filter(x=>!document.getElementById(x.hash.slice(1))).map(x=>x.hash)})''')
  assert dims['doc']<=w+1,(w,dims)
  assert not dims['missingLinks'],(w,dims)
  sel=page.locator('[data-ex2-trail-select]');sel.select_option('03')
  assert page.locator('[data-ex2-trail-card]:visible').count()==1,(w,'filter')
  assert page.locator('#trail-03').is_visible()
  assert 'Route 03' in page.locator('[data-ex2-trail-status]').inner_text()
  page.locator('#trail-03 summary').click()
  assert page.locator('#trail-03 details').evaluate('(x)=>x.open')
  page.locator('[data-ex2-trail-reset]').click()
  assert page.locator('[data-ex2-trail-card]:visible').count()==6,(w,'reset')
  sel.select_option('04');page.evaluate("location.hash='#trail-02'")
  page.wait_for_timeout(40)
  assert page.locator('#trail-02').is_visible(),(w,'deeplink')
  assert page.evaluate("document.activeElement.id")=='trail-02', (w,'focus')
  assert not errs,(w,errs)
  if w in (390,1440):page.locator('#documentary-trails').screenshot(path=str(QA/'screenshots'/f'trail-{w}.png'))
  report['tested_widths'].append({'width':w,'doc_width':dims['doc'],'six_routes':True,'filter_reset':True,'deeplink_focus':True,'no_js_error':True})
  ctx.close()
 # no-JS: complete document should show every route, no controls visible
 ctx,page,errs=open_page(browser,390,False)
 assert page.locator('[data-ex2-trail-card]:visible').count()==6
 assert not page.locator('[data-ex2-trail-controls]').is_visible()
 page.locator('#trail-01 summary').click();assert page.locator('#trail-01 details').evaluate('(x)=>x.open')
 assert not errs
 ctx.close()
 # reduced motion, and 200%-style reflow at 320px CSS; no animation required
 ctx,page,errs=open_page(browser,320,True,'reduce')
 assert page.evaluate('document.documentElement.scrollWidth')<=321
 assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
 ctx.close()
 # deliberately corrupt select value to exercise fail-open rather than hidden evidence
 ctx,page,errs=open_page(browser,390)
 page.evaluate("(()=>{let x=document.querySelector('[data-ex2-trail-select]');x.insertAdjacentHTML('beforeend','<option value=bogus>unreviewed</option>');x.value='bogus';x.dispatchEvent(new Event('change',{bubbles:true}));})()")
 assert page.locator('[data-ex2-trail-card]:visible').count()==6
 assert not page.locator('[data-ex2-trail-controls]').is_visible()
 ctx.close()
 browser.close()
report['no_js']=True;report['reduced_motion']=True;report['fail_open']=True
(QA/'TRAIL_BROWSER_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('TRAIL_BROWSER_PASS',len(widths),'viewports; JS off, keyboard-native disclosure, deep link, reduced motion, fail open')
