#!/usr/bin/env python3
"""R327 committed, reproducible Chromium reader-to-source-to-CTA gate (offline)."""
import hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
H=R/'apollo-r320/qa/wp_late_shortcodes.php'
O=R/'apollo-r327/QA';O.mkdir(parents=True,exist_ok=True)
PINS=[(P,'91745c286b2f23fb8a93058afb58905a2756714e'),(C,'550e1dc6ac869ebbda1b371343a6cdd91f8608f4'),(J,'f85617e5f12ba747908ac507261f69c377369de7')]
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SOURCES=['https://www.nasa.gov/mission/apollo-1/','https://www.nasa.gov/history/Apollo204/proceed.html','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/']
def sha_blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def audit(pg):
 d=pg.locator('section.fv-r281').evaluate('''r=>({
  status:r.dataset.fvEvidenceStatus,
  docs:[...r.querySelectorAll('.fv-r281__source-list>li')].map(e=>({id:e.dataset.fvSourceId,role:e.dataset.fvEvidenceRole,url:e.querySelector('a[data-fv-link-purpose]')?.href})),
  photos:[...r.querySelectorAll('[data-fv-media-record]')].map(e=>({rights:e.dataset.fvImageRights,proof:e.dataset.fvClaimProof})),
  ctas:[...r.querySelectorAll('a[data-fv-cta]')].map(e=>({url:e.href,kind:e.dataset.fvConversionKind})),
  links:[...r.querySelectorAll('a[href^="https://"]')].map(e=>({url:e.href,height:e.getBoundingClientRect().height})),
  geo:!!r.querySelector('[data-lat],[data-lng],[data-geo-edge],iframe'),
  rights:r.textContent.includes('NASA does not endorse this website.')})''')
 assert d['status']=='editorial-review-pending' and d['rights'] and not d['geo']
 assert len(d['docs'])==3 and [x['url'] for x in d['docs']]==SOURCES
 assert all(x['role']=='documented-textual-claim' for x in d['docs'])
 assert len(d['photos'])==4 and all(x=={'rights':'not-cleared-for-reuse','proof':'no'} for x in d['photos'])
 assert d['ctas']==[{'url':FREE,'kind':'editorial-continuation'}]
 assert len(d['links'])==18 and all(x['height']>=40 for x in d['links'])
 assert all(x['url']==FREE or x['url'].startswith(('https://www.nasa.gov/','https://sma.nasa.gov/')) for x in d['links'])
def main():
 for path,expected in PINS:assert sha_blob(path.read_bytes())==expected,str(path)
 subprocess.run(['php','-l',str(P)],check=True,capture_output=True)
 subprocess.run(['node','--check',str(J)],check=True,capture_output=True)
 raw=subprocess.check_output(['php',str(H),'late-dynamic','1'],text=True)
 html,queue=raw.split('<!--R320_QUEUE:',1)
 assert json.loads(queue.split('-->')[0])['calls']==1
 assert 'history_pilot_2026_11' not in html
 css=C.read_text();js=J.read_text();results=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for w in (320,360,390,768,1024,1440,1920):
    for enabled in (False,True):
     pg=b.new_page(viewport={'width':w,'height':850},java_script_enabled=enabled,has_touch=w<=390,reduced_motion='reduce')
     pg.goto('about:blank')
     if enabled:pg.evaluate('''()=>{window.__fvPerf={lcp:[],cls:[]};new PerformanceObserver(o=>__fvPerf.lcp.push(...o.getEntries().map(x=>x.startTime))).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(o=>__fvPerf.cls.push(...o.getEntries().filter(x=>!x.hadRecentInput).map(x=>x.value))).observe({type:'layout-shift',buffered:true});}''')
     pg.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
     if enabled:pg.add_script_tag(content=js)
     pg.locator('section.fv-r281 details').evaluate_all('ds=>ds.forEach(d=>d.open=true)')
     pg.wait_for_timeout(90);audit(pg)
     assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
     (pg.locator('.fv-r281__source-jump a').first.tap() if w<=390 else pg.locator('.fv-r281__source-jump a').first.click())
     assert pg.evaluate('location.hash==="#fv-r281-1-source-1" && document.activeElement.id==="fv-r281-1-source-1"')
     pg.locator('.fv-r307__continue-return').first.click()
     assert pg.evaluate('location.hash==="#fv-r281-1-continue" && document.activeElement.id==="fv-r281-1-continue"')
     pg.locator('.fv-r281__authority-jump a').click()
     assert pg.evaluate('document.querySelector("details.fv-r291__authority-disclosure").open && document.activeElement.id==="fv-r281-1-authority-1"')
     pg.locator('.fv-r281__authority-return a').first.click()
     assert pg.evaluate('document.activeElement.id==="fv-r281-1-event-2"')
     audit(pg)
     if w in (390,1440):pg.screenshot(path=str(O/f'r327-{w}-{"js" if enabled else "nojs"}.png'),full_page=True)
     perf=pg.evaluate('window.__fvPerf') if enabled else None
     results.append({'width':w,'javascript':enabled,'readerJourney':'PASS','LCP_fixture_ms':round(max(perf['lcp']),1) if perf and perf['lcp'] else None,'CLS_fixture':round(sum(perf['cls']),5) if perf else None})
     pg.close()
   for w in (390,1440):
    pg=b.new_page(viewport={'width':w,'height':850},forced_colors='active',reduced_motion='reduce')
    pg.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
    pg.locator('section.fv-r281 summary').first.focus();pg.keyboard.press('Enter')
    assert pg.locator('section.fv-r281 details').first.evaluate('e=>e.open')
    assert pg.locator('section.fv-r281 summary').first.evaluate('e=>e.matches(":focus-visible")')
    pg.close()
   pg=b.new_page();pg.set_content(html)
   assert pg.locator('.fv-r281__source-list>li').count()==3
   assert pg.locator('a[data-fv-cta]').count()==1
   pg.close()
  finally:b.close()
 report={'R':'327','contexts':17,'responsiveCases':results,'forcedColorsKeyboardCases':2,'cssDisabledNoJSCase':1,'sourcePinSHAs':{str(x.relative_to(R)):v for x,v in PINS},'axe':'NOT_EXECUTED','nativeHTTP':'ADMIN_BLOCKED','WordPressInstalled':'NOT_VERIFIED','offer':'NOT_AUTHENTICATED','production':'NOT_RELEASED'}
 (O/'r327-gate-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 print('R327 committed replay PASS: 14 responsive, 2 forced-colors keyboard, 1 unstyled/no-JS')
if __name__=='__main__':main()
