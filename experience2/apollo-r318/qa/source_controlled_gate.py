#!/usr/bin/env python3
"""R318 offline Chromium release-readiness gate; deliberately NOT axe/WordPress acceptance."""
import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import parse_qsl,urlsplit
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
PHP=R/'apollo-r281/apollo-source-experience.php'
JS=R/'apollo-r281/assets/apollo-cache-continuation.js'
CSS=R/'apollo-r281/assets/apollo-source-experience.css'
FIX=R/'apollo-r301/qa/local_http_fixture.php'
OLD=R/'apollo-r317/qa/r316_prior.js'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
Q='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def render(q):return subprocess.check_output(['php','-r','parse_str($argv[2],$_GET);include $argv[1];',str(FIX),'instances=2&queue=0&'+q],text=True)
assert blob(PHP.read_bytes())=='9ff32d45b7e957e1d25724ab5fc55c467aaa55e2'
assert blob(JS.read_bytes())=='a3c858b51005495ebebb326086badc155c1b7e5a'
subprocess.run(['php','-l',str(PHP)],capture_output=True,check=True)
subprocess.run(['node','--check',str(JS)],check=True)
html=render(Q)
assert html==render('')==render('utm_campaign=mind_pilot_2026_11'),'Cached HTML varies by visitor'
s=BeautifulSoup(html,'html.parser');sections=s.select('section.fv-r281[data-fv-experience="apollo-1"]')
assert len(sections)==2
for section in sections:
 assert len(section.select('li[data-fv-evidence-role="documented-textual-claim"]'))==3
 assert len(section.select('li[data-fv-evidence-role="contextual-media-only"]'))==4
 assert len(section.select('a[data-fv-cta]'))==1
 assert section.select_one('a[data-fv-cta]')['href']==FREE
 assert not section.select('img,iframe,video,canvas,[data-lat],[data-lon]')
 for a in section.select('a[data-fv-link-purpose="official-evidence-source"],a[data-fv-link-purpose="contextual-media-source"]'):
  assert urlsplit(a['href']).hostname.endswith('nasa.gov')
ids=[x['id'] for x in s.select('section.fv-r281 [id]')]
assert len(ids)==len(set(ids)),'Duplicate IDs'
css=CSS.read_text();js=JS.read_text();cases=[];perf=[];errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (320,360,390,768,1024,1440,1920):
  for mode in ('js','nojs','nocss','forced'):
   enabled=mode in ('js','forced')
   ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
     has_touch=width<=390,reduced_motion='reduce',forced_colors='active' if mode=='forced' else 'none')
   page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto('about:blank?'+Q)
   page.set_content(html.replace('</head>','<style>'+(css if mode!='nocss' else '')+'</style></head>'))
   if enabled:page.add_script_tag(content=js)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,mode,'overflow')
   a=page.locator('section.fv-r281 a[data-fv-cta]').first
   a.focus();page.keyboard.press('Shift+F10')
   target=a.get_attribute('href')
   assert (dict(parse_qsl(urlsplit(target).query))==dict(parse_qsl(Q))) if enabled else (target==FREE)
   assert page.locator('section.fv-r281 a[data-fv-cta]').nth(1).get_attribute('href')==FREE
   source=page.locator('section.fv-r281 .fv-r281__source-jump a').first
   source.click();assert page.evaluate('location.hash').endswith('-source-1')
   source.focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
   if mode in ('js','nojs'):
    outline=page.evaluate("getComputedStyle(document.querySelector('.fv-r281__source-jump a')).outlineWidth")
    assert float(outline.replace('px',''))>=2,(width,mode,'keyboard focus not visible')
   if mode=='js' and width<=390:
    summary=page.locator('section.fv-r281 .fv-r281__drawer summary').first
    summary.tap();assert page.locator('section.fv-r281 .fv-r281__drawer').first.get_attribute('open') is not None
   if mode=='js':
    page.evaluate('''() => {window.fvcls=0;window.fvlcp=null;
      new PerformanceObserver(l=>{for(let e of l.getEntries())if(!e.hadRecentInput)fvcls+=e.value}).observe({type:'layout-shift',buffered:true});
      new PerformanceObserver(l=>{for(let e of l.getEntries())fvlcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});}''')
    page.wait_for_timeout(100)
    m=page.evaluate("({lcp:window.fvlcp,cls:window.fvcls,resources:performance.getEntriesByType('resource').length})")
    assert m['cls']<=.1 and m['resources']==0,(width,m)
    perf.append({'width':width,**m})
   cases.append([width,mode]);ctx.close()
 # R316 is a real semantic negative control: the same valid history campaign fails.
 ctx=b.new_context();page=ctx.new_page();page.goto('about:blank?'+Q)
 page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
 page.add_script_tag(content=OLD.read_text())
 a=page.locator('section.fv-r281 a[data-fv-cta]').first
 a.focus();page.keyboard.press('Shift+F10');assert a.get_attribute('href')==FREE
 ctx.close()
 # Closed on screen, documentary custody still visible in print with JS off.
 ctx=b.new_context(java_script_enabled=False);page=ctx.new_page()
 page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
 page.emulate_media(media='print')
 for sel in ('.fv-r281__drawer-body','.fv-r309__media-list','.fv-r291__disclosure-intro','.fv-r296__date-guide'):
  assert page.locator(sel).first.is_visible(),(sel,'print source hidden')
 ctx.close();b.close()
assert not errors,errors
print('R318 independently committed Chromium gate: PASS',len(cases),'contexts + R316 negative control + print custody; fixture only')
print(json.dumps({'fixture_performance':perf,'axe_core':'NOT RUN','installed_WordPress':'NOT VERIFIED'}))
