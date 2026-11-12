#!/usr/bin/env python3
"""R316 source-controlled offline Chromium keyboard context-menu gate; not axe/WP/CSP/field CWV."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qsl
from subprocess import check_output,run
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import hashlib

R=Path(__file__).resolve().parents[2]
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
P=R/'apollo-r281/apollo-source-experience.php'
F=R/'apollo-r301/qa/local_http_fixture.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
OLD=Path(__file__).with_name('r315_prior.js')
U='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
Q='utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo1_pilot_2026_11&utm_content=apollo1_yt_alpha001'
render=lambda q:check_output(['php','-r','parse_str($argv[2],$_GET);include $argv[1];',str(F),'instances=2&queue=0&'+q],text=True)
run(['php','-l',str(P)],check=True,capture_output=True)
run(['node','--check',str(J)],check=True)
h=render(Q)
assert h==render(Q.replace('alpha001','person%40example.com'))
s=BeautifulSoup(h,'lxml')
assert len(s.select('li[data-fv-evidence-role="documented-textual-claim"]'))==6
assert len(s.select('li[data-fv-evidence-role="contextual-media-only"]'))==8
assert all(a.get('href')==U for a in s.select('a[data-fv-cta]'))
js=J.read_text();css=C.read_text();old=OLD.read_text()
b=old.encode()
assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()=='b51975a674dd08e4dbba90b5a33a3d0efac68cd6'
assert 'event.button === -1 && event.buttons === 0 && event.detail === 0' in js
n=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in (320,390,768,1440,1920):
  for enabled in (True,False):
   x=b.new_context(viewport={'width':w,'height':900},java_script_enabled=enabled,reduced_motion='reduce',forced_colors='active' if w==768 else 'none')
   t=x.new_page();t.goto('about:blank?'+Q)
   t.set_content(h.replace('</head>','<style>'+css+'</style></head>'))
   if enabled:t.add_script_tag(content=js)
   a=t.locator('a[data-fv-cta]').first;a.focus();t.keyboard.press('Shift+F10')
   dest=a.get_attribute('href')
   assert (dict(parse_qsl(urlsplit(dest).query))==dict(parse_qsl(Q))) if enabled else (dest==U)
   assert t.locator('a[data-fv-cta]').nth(1).get_attribute('href')==U
   assert t.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   x.close();n+=1
 for key in ('Shift+F10','ContextMenu'):
  for script,expected in ((old,False),(js,True)):
   x=b.new_context();t=x.new_page();t.goto('about:blank?'+Q);t.set_content(h);t.add_script_tag(content=script)
   a=t.locator('a[data-fv-cta]').first;a.focus();t.keyboard.press(key)
   assert bool(urlsplit(a.get_attribute('href')).query)==expected
   x.close();n+=1
 b.close()
print('PASS R316',n,'/',n,'offline Chromium contexts; genuine R315 negative control; no axe/WP/CSP/field data')
