#!/usr/bin/env python3
"""Real Chromium layout and interaction on PHP-rendered HTML; NOT actual HTTP navigation or WordPress."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SHOTS=ROOT/'QA/screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
HTML=subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],capture_output=True,text=True,check=True,timeout=15).stdout
REPORT={'render':'original pinned R411+R414 PHP and actual R415 PHP','runtime':'offline page.set_content Chromium NOT HTTP WordPress','axe_core':'NOT_EXECUTED','navigated_lcp_cls':'NOT_MEASURED','production_p75_cwv':'NOT_MEASURED','passed':[],'screenshots':[],'responsive':[]}

def run():
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  def page(width=390,height=900,**kwargs):
   context=b.new_context(viewport={'width':width,'height':height},**kwargs)
   p=context.new_page();p.set_content(HTML,wait_until='load');return context,p
  def check(name,f):
   try:f();REPORT['passed'].append(name)
   except Exception as e:REPORT['failure']={'test':name,'error':str(e)};raise
  def structural():
   c,p=page()
   assert p.locator('[data-fv-r415-journey]').count()==2
   assert p.locator('.fv-r415__rail li').count()==6
   assert p.locator('.fv-r414__card').count()==12
   assert p.get_by_role('link',name='Continue to the free Apollo 1 investigation').count()==2
   ids=p.locator('[id]').evaluate_all('(arr)=>arr.map(el=>el.id)')
   assert len(ids)==len(set(ids)),[x for x in ids if ids.count(x)>1]
   assert p.locator('script,img,iframe,audio,video,form').count()==0
   assert p.locator('a[href^="https://"]').evaluate_all('(a)=>a.filter(x=>x.hostname!=="www.nasa.gov" && x.hostname!=="finalvestige.com").length')==0
   for sel in p.locator('.fv-r415__rail a[href^="#"]').all():
    fragment=sel.get_attribute('href')[1:]
    assert p.locator('[id="'+fragment+'"]').count()==1,fragment
   c.close()
  check('integrated-source-identity-and-links',structural)
  def responsive():
   for width in (320,360,390,768,1024,1440,1920):
    c,p=page(width)
    metrics=p.evaluate('''() => ({w:innerWidth,doc:document.documentElement.scrollWidth,
      cols:getComputedStyle(document.querySelector('.fv-r415__rail')).gridTemplateColumns.split(' ').length,
      cards:[...document.querySelectorAll('.fv-r414__card')].map(e=>Math.round(e.getBoundingClientRect().width))})''')
    assert metrics['doc']<=width+1,metrics
    assert min(metrics['cards'])>=160,metrics
    assert metrics['cols']==(1 if width<=780 else 3),metrics
    REPORT['responsive'].append(metrics)
    p.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
    REPORT['screenshots'].append(f'{width}.png')
    c.close()
  check('responsive-320-through-1920-and-card-minimum',responsive)
  def native_nojs():
   c,p=page(390,900,java_script_enabled=False)
   first=p.locator('.fv-r414 details').first
   assert first.locator('summary').is_visible()
   first.locator('summary').focus();p.keyboard.press('Enter')
   assert first.evaluate('(e)=>e.open')
   first.locator('summary').focus();p.keyboard.press('Space')
   assert not first.evaluate('(e)=>e.open')
   p.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True);REPORT['screenshots'].append('390-nojs.png')
   c.close()
  check('native-nojs-keyboard-disclosure',native_nojs)
  def touch_reduced():
   c,p=page(390,844,has_touch=True,is_mobile=True,reduced_motion='reduce')
   d=p.locator('.fv-r414 details').first;d.locator('summary').tap();assert d.evaluate('(e)=>e.open')
   assert p.locator('.fv-r415').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
   p.screenshot(path=str(SHOTS/'390-touch-reduced.png'),full_page=True);REPORT['screenshots'].append('390-touch-reduced.png')
   c.close()
  check('touch-reduced-motion',touch_reduced)
  def enlarged_forced():
   c,p=page(320,900,forced_colors='active')
   p.evaluate('document.documentElement.style.fontSize="64px"')
   metrics=p.evaluate('''()=>({documentWidth:document.documentElement.scrollWidth,width:innerWidth})''')
   assert metrics['documentWidth']<=metrics['width']+1,metrics
   p.screenshot(path=str(SHOTS/'320-4x-forced-colors.png'),full_page=True);REPORT['screenshots'].append('320-4x-forced-colors.png')
   c.close()
  check('enlarged-root-font-forced-colors',enlarged_forced)
  def link_flow():
   c,p=page(390)
   anchor=p.locator('.fv-r415__rail a[href^="#"]').first
   anchor.click()
   assert p.evaluate('location.hash')=='#fv-r414-gallery-1-05'
   assert p.locator('#fv-r414-gallery-1-05').count()==1
   assert p.get_by_role('link',name='Continue to the free Apollo 1 investigation').first.get_attribute('href').endswith('/the-hatch-opened-inward-apollo-1/')
   c.close()
  check('timeline-to-source-to-one-free-cta',link_flow)
  b.close()
 (ROOT/'QA/browser_results.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 print('PASS',len(REPORT['passed']),'browser methods; captures',len(REPORT['screenshots']))

if __name__=='__main__':
 try:run()
 except Exception:
  (ROOT/'QA/browser_results.json').write_text(json.dumps(REPORT,indent=2,sort_keys=True)+'\n')
  raise
