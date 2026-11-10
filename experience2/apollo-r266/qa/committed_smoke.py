#!/usr/bin/env python3
"""R266 exact-source Chromium smoke, CLI-only preview, not WordPress/axe acceptance."""
import hashlib, json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
f,over,source,mock=map(lambda v:Path(v).resolve(),sys.argv[1:5])
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((f/'manifest.json').read_bytes())=='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
for name,digest in json.loads((f/'manifest.json').read_text())['files'].items():assert sha((f/name).read_bytes())==digest,name
php=source/'qa/cli-preview.php'
run=lambda mode:subprocess.check_output(['php',str(php),mode],text=True)
assert all(run(k)=='' for k in ['missing','false','string'])
assert all(json.loads(run('states')).values())
card=run('good')
r=json.loads(subprocess.check_output(['php',str(mock),str(f/'fv-ex2-apollo-r224.php'),str(over/'fv-apollo-staging-overlay.php'),'direct'],text=True))
assert r['atlas_present'] and not r['fallback']
assert r['html']==(f/'templates/atlas-fragment.html').read_text()
html='<!doctype html><html lang="en"><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+(f/'assets/atlas-scoped.css').read_text()+(over/'assets/apollo-overlays.css').read_text()+(source/'assets/postscript.css').read_text()+'</style>'+r['html']+card+'</html>'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);count=0
 for width in [320,390,768,1440,1920]:
  for js in [False,True]:
   ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=width<=390,is_mobile=width<=390,reduced_motion='reduce')
   page=ctx.new_page();req=[];page.on('request',lambda r:req.append(r.url));page.set_content(html)
   assert not req and page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
   assert page.locator('.fv-apollo-atlas a[href^="https://www.nasa.gov/"]').count()==55
   assert page.locator('.fv-apollo-atlas a[href^="#"]').count()==31
   assert page.locator('.fv-apollo-atlas a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==1
   assert page.locator('.fv-apollo-postscript a[href]').count()==1
   assert page.locator('.fv-apollo-postscript__action').get_attribute('href')=='https://finalvestige.com/mini-museum-history-collectibles/'
   aria=page.locator('.fv-apollo-postscript').aria_snapshot()
   assert 'complementary "A different kind of evidence"' in aria and 'link "Read the Mini Museum buying guide"' in aria
   assert 'Affiliate disclosure:' in page.locator('.fv-apollo-postscript').inner_text()
   assert page.locator('.fv-apollo-postscript__action').evaluate('(e)=>e.getBoundingClientRect().height')>=44
   count+=1;ctx.close()
 b.close()
print(json.dumps({'passed':True,'contexts':count,'source_sha256':sha(card.encode()),'axe':'NOT EXECUTED','wordpress':'NOT TESTED'}))
