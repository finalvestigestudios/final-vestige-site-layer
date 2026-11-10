#!/usr/bin/env python3
"""R267 committed source-matched Chromium smoke. Offline only; axe/WP/HTTP are held."""
import hashlib, json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
f,o,s,m,rule=map(lambda q:Path(q).resolve(),sys.argv[1:6])
hash256=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert hash256(f/'manifest.json')=='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
for k,v in json.loads((f/'manifest.json').read_text())['files'].items(): assert hash256(f/k)==v,k
run=lambda *a:subprocess.check_output(['php',*map(str,a)],text=True)
card=run(s/'qa/cli-preview.php','good')
assert all(json.loads(run(s/'qa/cli-preview.php','states')).values())
r=json.loads(run(m,f/'fv-ex2-apollo-r224.php',o/'fv-apollo-staging-overlay.php','direct'))
assert r['atlas_present'] and not r['fallback'] and r['html']==(f/'templates/atlas-fragment.html').read_text()
base=(f/'assets/atlas-scoped.css').read_text()+(o/'assets/apollo-overlays.css').read_text()+(s/'assets/postscript.css').read_text()
def doc(css):return '<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+base+css+'</style>'+r['html']+card+'</html>'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);n=0
 for w in (320,390,768,1440,1920):
  for pct in (100,200,400):
   for js in (False,True):
    c=b.new_context(viewport={'width':w,'height':900},java_script_enabled=js,has_touch=w<=390,is_mobile=w<=390,reduced_motion='reduce')
    page=c.new_page();req=[];page.on('request',lambda r:req.append(r.url));measure=lambda:page.locator('.fv-apollo-postscript__action').evaluate('(x)=>x.getBoundingClientRect().height')
    page.set_content(doc(''));page.evaluate('(v)=>document.documentElement.style.fontSize=v+"%"',pct);old=measure()
    page.set_content(doc(rule.read_text()));page.evaluate('(v)=>document.documentElement.style.fontSize=v+"%"',pct);new=measure()
    assert not req and page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert new>=44 and (new<=old+.6 if w<=390 else abs(new-old)<.6)
    if w==320 and pct==400: assert old>2500 and new<900
    if w==390 and pct==400: assert old>2500 and new<700
    assert page.locator('.fv-apollo-atlas a[href^="https://www.nasa.gov/"]').count()==55
    assert page.locator('.fv-apollo-atlas a[href^="#"]').count()==31
    assert page.locator('.fv-apollo-postscript a').count()==1
    assert page.locator('.fv-apollo-postscript__action').get_attribute('href')=='https://finalvestige.com/mini-museum-history-collectibles/'
    assert 'Affiliate disclosure:' in page.locator('.fv-apollo-postscript').inner_text()
    n+=1;c.close()
 b.close()
print(json.dumps({'pass':True,'contexts':n,'r267_css_git_test_sha256':hash256(rule),'axe':'NOT EXECUTED','wordpress':'NOT TESTED'}))
