#!/usr/bin/env python3
"""Real Chromium local PHP fixture QA. NOT installed WordPress, NOT production CWV or axe."""
import json, pathlib, subprocess
import fitz
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
QA=ROOT/'QA'; QA.mkdir(exist_ok=True)
subprocess.check_call(['php',str(ROOT/'qa/contract.php')])
fixture=QA/'local-php-fixture.html'
source=fixture.read_text(encoding='utf8')
assert 'data-fv-r384-gallery' in source
CONTEXTS=[('320-mobile',320,780,True,False,False,False),('390-mobile',390,850,True,False,False,False),('768-tablet',768,900,False,False,False,False),('1440-desktop',1440,900,False,False,False,False),('1920-wide',1920,1080,False,False,False,False),('320-nojs',320,780,True,True,False,False),('390-touch',390,850,True,False,False,True),('390-reduced',390,850,True,False,False,False),('320-forced',320,830,True,False,True,False),('320-root4x',320,900,True,False,False,False)]
report={'status':'LOCAL_CHROMIUM_PHP_FIXTURE_PASS_NOT_STAGING','contexts':[],'assertions':0,'axe_core':'NOT RUN: genuine axe-core unavailable','installed_wordpress':'NOT TESTED','https_csp':'NOT TESTED','core_web_vitals':'NOT MEASURED: fixture-only browser observations'}
def check(value, label):
 report['assertions']+=1
 if not value: raise AssertionError(label)
observer="""window.__apolloVitals={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__apolloVitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__apolloVitals.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){window.__apolloVitals.observerError=String(e)}"""
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name,w,h,mobile,nojs,forced,touch in CONTEXTS:
  ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=touch or mobile,java_script_enabled=not nojs,reduced_motion='reduce' if name=='390-reduced' else 'no-preference',forced_colors='active' if forced else 'none')
  page=ctx.new_page()
  page.set_content(source.replace('</head>',('<script>'+observer+'</script></head>') if not nojs else '</head>',1),wait_until='load')
  if name=='320-root4x': page.add_style_tag(content='html{font-size:400%!important}')
  page.wait_for_timeout(120)
  cards=page.locator('[data-fv-r384-record]')
  check(cards.count()==6,name+' six sources')
  check(page.locator('.fv-r384__phase').count()==3,name+' three phases')
  check(page.locator('[data-fv-r384-nasa]').count()==6,name+' six primary links')
  check(page.locator('[data-fv-free-cta]').count()==1,name+' one noncommercial CTA')
  check(page.locator('details').count()==6,name+' native drawers')
  check(page.locator('summary').count()==6,name+' accessible native summaries')
  check(page.locator('img,canvas,iframe,video').count()==0,name+' no imagery or remote media')
  check(page.locator('[data-fv-free-cta]').get_attribute('href')=='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',name+' correct free destination')
  check(page.locator('[data-fv-r384-nasa]').nth(5).get_attribute('href')=='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',name+' later testing separated')
  check(page.locator('[data-fv-r384-nasa]').nth(4).get_attribute('href')=='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',name+' Board uncertainty source')
  check(page.locator('.fv-r384__rights').count()==1,name+' rights statement')
  check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),name+' no horizontal overflow')
  check(page.locator('.fv-r384__phase').first.is_visible(),name+' complete no JS meaning')
  if name=='1440-desktop':
   page.locator('summary').first.focus();page.keyboard.press('Enter')
   check(page.locator('details').first.evaluate('(el)=>el.open'),name+' keyboard opens detail')
   cdp=ctx.new_cdp_session(page); ax=cdp.send('Accessibility.getFullAXTree')['nodes']
   roles=[n.get('role',{}).get('value') for n in ax if not n.get('ignored')]
   check('link' in roles and 'heading' in roles,name+' real Chromium AX tree exposes links and headings')
   page.pdf(path=str(QA/'Apollo_R384_Document_Print.pdf'),format='A4',print_background=True)
  if name=='390-touch':
   page.locator('summary').first.tap()
   check(page.locator('details').first.evaluate('(el)=>el.open'),name+' native touch opens detail')
  if name=='320-nojs':
   check(page.locator('details').first.is_visible(),name+' native details exist with JS disabled')
   page.locator('summary').first.tap()
   check(page.locator('details').first.evaluate('(el)=>el.open'),name+' noJS native touch disclosure')
  if name=='320-forced': check(page.locator('.fv-r384__card').first.is_visible(),name+' forced-color card readable')
  page.screenshot(path=str(QA/(name+'.png')),full_page=True,animations='disabled')
  metrics=None if nojs else page.evaluate('window.__apolloVitals')
  report['contexts'].append({'context':name,'width':w,'result':'PASS','local_lcp_observed_ms':None if not metrics else metrics['lcp'],'local_cls_observed':None if not metrics else metrics['cls']})
  ctx.close()
 browser.close()
pdf=fitz.open(str(QA/'Apollo_R384_Document_Print.pdf'))
text='\n'.join(p.get_text() for p in pdf)
links=[x.get('uri') for p in pdf for x in p.get_links() if x.get('uri')]
check(len(pdf)>=1,'print pages created')
check('Document supports' in text and 'Does not establish' in text,'print source and limits')
check(any('report-of-the-apollo-204-review-board' in x for x in links),'print Board hyperlink')
check(any('apollo-flammability-tests' in x for x in links),'print testing hyperlink')
check(any('the-hatch-opened-inward-apollo-1' in x for x in links),'print free CTA hyperlink')
report['print_pdf']={'pages':len(pdf),'links':len(links),'distinct_urls':len(set(links))}
(QA/'browser-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'contexts':len(report['contexts']),'assertions':report['assertions'],'print_pages':len(pdf)},indent=2))
