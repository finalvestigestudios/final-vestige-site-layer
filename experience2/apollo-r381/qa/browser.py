#!/usr/bin/env python3
"""Executable Playwright Chromium QA against PHP-rendered fixture. NOT WordPress staging."""
from __future__ import annotations
import json, pathlib, subprocess
from playwright.sync_api import sync_playwright
BASE=pathlib.Path(__file__).resolve().parents[1]
QA=BASE/'QA'; QA.mkdir(exist_ok=True)
html=subprocess.check_output(['php',str(BASE/'qa/fixture.php')],text=True)
assert '<!doctype html>' in html.lower() and html.count('data-fv-atlas-plate ') == 6
observer = """<script>window.__fvVitals={lcp:0,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries()){window.__fvVitals.lcp=e.startTime}}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput)window.__fvVitals.cls+=e.value}}).observe({type:'layout-shift',buffered:true})}catch(e){window.__fvVitals.error=String(e)}</script>"""
html=html.replace('<head>', '<head>'+observer,1)
(QA/'local-fixture.html').write_text(html,encoding='utf-8')
cases=[('320-mobile',320,720,True,False,False,False),('390-mobile',390,800,True,False,False,False),('768-tablet',768,980,False,False,False,False),('1440-desktop',1440,900,False,False,False,False),('1920-wide',1920,1080,False,False,False,False),('320-nojs',320,720,True,True,False,False),('390-touch',390,800,True,False,False,True),('390-reduced',390,800,True,False,False,False),('320-forced',320,800,True,False,True,False),('320-root4x',320,850,True,False,False,False)]
report={'boundary':'real local Chromium set_content with PHP-rendered fixture, NOT installed WordPress or HTTP staging','browser':'Chromium','axe_core':'NOT EXECUTED: audited axe-core runtime unavailable','http_csp':'NOT VERIFIED: set_content fixture','contexts':[], 'assertions':0}

def check(cond,msg):
 report['assertions']+=1
 if not cond: raise AssertionError(msg)

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name,w,h,mobile,nojs,forced,touch in cases:
  ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=mobile,has_touch=(mobile or touch),java_script_enabled=not nojs,reduced_motion='reduce' if name=='390-reduced' else 'no-preference',forced_colors='active' if forced else 'none')
  page=ctx.new_page()
  page.set_content(html, wait_until='load')
  page.wait_for_timeout(160)
  if name=='320-root4x':page.add_style_tag(content='html{font-size:400%!important}')
  check(page.locator('[data-fv-atlas]').count()==1,name+' one root')
  check(page.locator('[data-fv-atlas-plate]').count()==6,name+' six records in DOM')
  check(page.locator('[data-fv-atlas-phase]').count()==3,name+' three phases')
  check(page.locator('[data-fv-free-cta]').count()==1,name+' single editorial action')
  check(page.locator('[data-fv-nasa-source]').count()==6,name+' six NASA citations')
  check(page.locator('img,iframe,canvas').count()==0,name+' no external imagery / geo canvas')
  check(page.locator('[data-fv-atlas-filter]').is_visible() == (not nojs),name+' enhancement only with JS')
  check(page.locator('[data-fv-atlas-plate]:visible').count()==6,name+' six visible plates initially')
  check(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'),name+' no horizontal overflow')
  cta=page.locator('[data-fv-free-cta]')
  check(cta.get_attribute('href')=='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',name+' canonical editorial destination')
  check(page.locator('[data-fv-atlas] [hidden]').count()==(1 if nojs else 0),name+' expected hidden controls state')
  check(page.locator('[data-fv-atlas] a[href^="http"]').count()>=7,name+' source and CTA links')
  if not nojs and name!='320-root4x':
   sel=page.locator('[data-fv-atlas-filter]')
   sel.select_option('response')
   check(page.locator('[data-fv-atlas-plate]:visible').count()==1,name+' filter response')
   check(page.locator('[data-fv-atlas-phase]:visible').count()==1,name+' hide irrelevant phases')
   check('1 reviewed source record shown' in page.locator('[data-fv-atlas-status]').inner_text(),name+' live status')
   page.locator('[data-fv-atlas-reset]').click()
   check(page.locator('[data-fv-atlas-plate]:visible').count()==6,name+' reset all records')
   check(sel.evaluate('(e)=>e===document.activeElement'),name+' reset focus returns to select')
   sel.select_option('record')
   check(page.locator('[data-fv-atlas-plate]:visible').count()==2,name+' exact two document records')
   sel.select_option('all')
  if name=='390-touch':
   drawer=page.locator('summary').first
   drawer.tap()
   check(page.locator('details').first.evaluate('(d)=>d.open'),name+' touch opens native drawer')
  if name=='1440-desktop':
   page.locator('.fv-a381__rail a').first.focus()
   page.keyboard.press('Tab')
   check(page.evaluate('document.activeElement.tagName')=='A',name+' keyboard jump traversal')
   page.locator('summary').first.focus()
   page.keyboard.press('Enter')
   check(page.locator('details').first.evaluate('(d)=>d.open'),name+' keyboard native disclosure')
  page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
  vitals=page.evaluate('window.__fvVitals || null') if not nojs else None
  report['contexts'].append({'name':name,'viewport':w,'checks':'PASS','observed_fixture_lcp_ms':None if not vitals else round(vitals.get('lcp') or 0,1),'observed_fixture_cls':None if not vitals else round(vitals.get('cls') or 0,5)})
  if name=='1440-desktop':
   page.locator('[data-fv-atlas-filter]').select_option('response')
   page.pdf(path=str(QA/'Apollo_R381_Print_Source_Dossier.pdf'),format='A4',print_background=False,prefer_css_page_size=False)
  ctx.close()
 browser.close()
pdftext=subprocess.check_output(['pdftotext',str(QA/'Apollo_R381_Print_Source_Dossier.pdf'),'-'],text=True)
check('Source custody and limitations' not in pdftext,'drawer excluded from print')
check(pdftext.count('Print source:') == 6,'all six source citations restored in print even after filter')
check('50 Years Ago' not in pdftext,'no invented title in print')
check('Apollo 1' in pdftext and 'December 1967' in pdftext,'historical and later time boundaries printed')
report['status']='LOCAL_CHROMIUM_FIXTURE_PASS_NOT_STAGING'; report['num_contexts']=len(report['contexts'])
(QA/'browser-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':report['status'],'contexts':report['num_contexts'],'assertions':report['assertions'],'LCP_CLS':'local fixture observations only','axe':'NOT RUN'},indent=2))
