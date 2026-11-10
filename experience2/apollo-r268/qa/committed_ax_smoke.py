#!/usr/bin/env python3
"""R268 committed Chromium CDP accessibility/custody smoke; NOT axe or live WP."""
import hashlib, json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
f,o,s,r,m=map(lambda x:Path(x).resolve(),sys.argv[1:6])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(f/'manifest.json')=='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
for path,expected in json.loads((f/'manifest.json').read_text())['files'].items():assert sha(f/path)==expected,path
run=lambda *x:subprocess.check_output(['php',*map(str,x)],text=True)
p=json.loads(run(m,f/'fv-ex2-apollo-r224.php',o/'fv-apollo-staging-overlay.php','direct'))
assert p['atlas_present'] and not p['fallback'] and p['html']==(f/'templates/atlas-fragment.html').read_text()
assert all(json.loads(run(s/'qa/cli-preview.php','states')).values())
card=run(s/'qa/cli-preview.php','good')
assert 'data-release="REVIEW-ONLY"' in card
hold=json.loads((Path(__file__).parent/'conversion-hold.json').read_text())
assert hold['approval_state']=='HARD_HOLD_NOT_LIVE' and hold['staging_only'] is True
for key,value in hold.items():
 if key.endswith('_verified') or key.startswith('approved_') or key.startswith('founder_') or key.endswith('_computable'):
  assert value is False,(key,value)
css=''.join((x.read_text() for x in [f/'assets/atlas-scoped.css',o/'assets/apollo-overlays.css',s/'assets/postscript.css',r/'assets/postscript-reflow.css']))
html='<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style>'+p['html']+card+'</html>'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);count=0
 for width in (320,390,768,1440,1920):
  for js in (False,True):
   c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390)
   page=c.new_page();requests=[];page.on('request',lambda req:requests.append(req.url))
   page.set_content(html)
   if js:page.add_script_tag(content=(o/'assets/source-drawer-focus.js').read_text())
   assert not requests
   assert page.locator('.fv-apollo-atlas a[href^="https://www.nasa.gov/"]').count()==55
   assert page.locator('.fv-apollo-atlas a[href^="#"]').count()==31
   assert page.locator('.fv-apollo-postscript a').count()==1
   assert page.locator('.fv-apollo-postscript a').get_attribute('href')==hold['preview_guide_destination']
   assert 'Affiliate disclosure:' in page.locator('.fv-apollo-postscript').inner_text()
   assert page.locator('.fv-apollo-atlas a[href*="the-hatch-opened-inward"]').count()==1
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   ax=c.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
   unnamed=[n for n in ax if not n.get('ignored') and n.get('role',{}).get('value') in ('link','button','textField','searchBox') and not (n.get('name',{}).get('value') or '').strip()]
   assert not unnamed,unnamed[:3]
   summary=page.locator('.fv-apollo-source-drawer summary')
   if js:
    link=page.locator('a[href="#fv-apollo-source-drawer"]').first;link.focus();link.press('Enter')
    page.wait_for_function("document.activeElement===document.querySelector('.fv-apollo-source-drawer summary')",timeout=1200)
   else:
    summary.focus();summary.press('Enter')
   assert page.locator('.fv-apollo-source-drawer').get_attribute('open') is not None
   page.evaluate('document.documentElement.style.fontSize="400%"')
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   page.emulate_media(media='print')
   assert page.locator('.fv-apollo-postscript').evaluate('(x)=>getComputedStyle(x).display')=='none'
   count+=1;c.close()
 b.close()
print(json.dumps({'contexts_passed':count,'mode':'LOCAL_SOURCE_MATCHED_CDP_AX_NOT_AXE','status':'HARD_HOLD'},sort_keys=True))
