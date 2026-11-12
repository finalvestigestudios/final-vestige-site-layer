#!/usr/bin/env python3
"""R317 locked Graph/asset campaign compatibility; Chromium offline, no sales claims."""
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import subprocess, json, hashlib
R=Path(__file__).resolve().parents[2]
PHP=R/'apollo-r281/apollo-source-experience.php'
JS=R/'apollo-r281/assets/apollo-cache-continuation.js'
CSS=R/'apollo-r281/assets/apollo-source-experience.css'
FIX=R/'apollo-r301/qa/local_http_fixture.php'
OLD=Path(__file__).with_name('r316_prior.js')
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
H='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
def render(q):return subprocess.check_output(['php','-r','parse_str($argv[2],$_GET);include $argv[1];',str(FIX),'instances=2&queue=0&'+q],text=True)
def blob(s):
 b=s.encode();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def labels(url):return dict(parse_qsl(urlsplit(url).query))
subprocess.run(['php','-l',str(PHP)],capture_output=True,check=True)
subprocess.run(['node','--check',str(JS)],check=True)
assert blob(OLD.read_text())=='d3fa14ad005077495401b1315482486956b23575'
assert 'r317-history-crosswalk-20261112' in PHP.read_text()
html=render(H)
for q in ('',H,'utm_campaign=mind_pilot_2026_11'):
 assert html==render(q),'Cache variant HTML changed'
soup=BeautifulSoup(html,'lxml')
assert len(soup.select('li[data-fv-evidence-role="documented-textual-claim"]'))==6
assert len(soup.select('li[data-fv-evidence-role="contextual-media-only"]'))==8
assert all(x.get('href')==FREE for x in soup.select('a[data-fv-cta]'))
js,css,old=JS.read_text(),CSS.read_text(),OLD.read_text()
for blocked in ('fetch(', 'sendBeacon','document.cookie','localStorage','sessionStorage','navigator.clipboard','innerHTML'):
 assert blocked not in js,blocked
cases=[];errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 def setup(width=390,q=H,enabled=True,source=js,css_on=True):
  ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,has_touch=width<=390,reduced_motion='reduce',forced_colors='active' if width==768 else 'none',service_workers='block')
  page=ctx.new_page()
  page.on('pageerror',lambda x:errors.append(str(x)))
  page.goto('about:blank?'+q)
  page.set_content(html.replace('</head>','<style>'+(css if css_on else '')+'</style></head>'))
  if enabled:page.add_script_tag(content=source)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),width
  return ctx,page
 def keyboard(page):
  link=page.locator('section.fv-r281 a[data-fv-cta]').first
  link.focus();page.keyboard.press('Shift+F10');return link.get_attribute('href')
 for width in (320,360,390,768,1024,1440,1920):
  for enabled in (True,False):
   ctx,page=setup(width,enabled=enabled)
   assert (labels(keyboard(page))==labels('?'+H)) if enabled else (keyboard(page)==FREE)
   assert page.locator('section.fv-r281 a[data-fv-cta]').nth(1).get_attribute('href')==FREE
   cases.append({'width':width,'javascript':enabled,'pass':True});ctx.close()
 for plat,code in [('youtube','yt'),('tiktok','tt'),('instagram','ig'),('facebook','fb')]:
  q=f'utm_source={plat}&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_{code}_assetx007'
  ctx,page=setup(q=q);assert labels(keyboard(page))==labels('?'+q);ctx.close();cases.append({'platform':plat,'pass':True})
 for q in (H.replace('apollo1_yt','history_yt'),H.replace('2026_11','2026_12'),H.replace('history_pilot','mind_pilot'),H.replace('youtube','tiktok'),H+'&utm_campaign=history_pilot_2026_11',H.replace('longform001','person%40example.com')):
  ctx,page=setup(q=q);assert keyboard(page)==FREE;ctx.close();cases.append({'reject':q,'pass':True})
 ctx,page=setup(source=old);assert keyboard(page)==FREE;ctx.close();cases.append({'old_version_negative_control':True,'pass':True})
 ctx,page=setup(enabled=False,css_on=False);assert keyboard(page)==FREE;ctx.close();cases.append({'noJS_noCSS':True,'pass':True})
 browser.close()
assert not errors,errors
print('R317 source-controlled Chromium gate PASS',len(cases),'cases; OLD R316 negative control confirmed')
