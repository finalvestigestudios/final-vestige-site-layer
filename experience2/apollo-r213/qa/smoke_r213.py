#!/usr/bin/env python3
"""Committed independent Apollo R213 PHP/Chromium fixture regression. Not WordPress or axe."""
import hashlib,json,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parents[1]/'dist'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def check(ok,why):
 if not ok:raise AssertionError(why)
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(folder):
 folder.mkdir(parents=True,exist_ok=True)
 m=json.loads((D/'manifest.json').read_text())
 check(m['release']=='r213' and not m['approved_purchase_offer'] and not m['upstream_R198_reconciled'],'Unsafe release flag')
 for f,d in m['files'].items():check(hashfile(D/f)==d,'Tampered '+f)
 check(subprocess.run(['php','-l',str(D/'fv-ex2-apollo-r213.php')],capture_output=True).returncode==0,'PHP syntax')
 def render(mode):return json.loads(subprocess.check_output(['php',str(D/'wp-render-shim-r213.php'),str(D/'fv-ex2-apollo-r213.php'),mode],text=True))
 normal,late,printed=[render(x) for x in ('normal','late','printed')]
 check(normal['css']=='enqueued' and not normal['fallback'],'Normal rendering')
 check(late['fallback'] and FREE in late['html'],'Late fail-open')
 check(printed['css']=='done' and not printed['fallback'],'Printed rendering')
 h=normal['html'];check(h.count('class="cta"')==1 and h.count('href="#fv-apollo-reading-bridge"')==2,'Navigation-to-one-action')
 css=(D/'assets/atlas-scoped.css').read_text();page='<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style><body>'+h+'</body>'
 cases=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),('no-js',390,{'java_script_enabled':False}),('touch',390,{'is_mobile':True,'has_touch':True}),('reduced',390,{'reduced_motion':'reduce'}),('forced',390,{'forced_colors':'active'})]
 receipts=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for name,w,opts in cases:
   c=browser.new_context(viewport={'width':w,'height':900},**opts);p=c.new_page();p.set_content(page)
   p.screenshot(path=str(folder/(name+'.png')),full_page=True,animations='disabled')
   nav=p.locator('.mast a[href="#fv-apollo-reading-bridge"]');check(nav.count()==1,'Missing nav')
   nav.focus();p.keyboard.press('Enter');check(p.evaluate('location.hash')=='#fv-apollo-reading-bridge','Keyboard jump')
   check(p.locator('.fv-apollo-reading-bridge .cta').count()==1,'Duplicate CTA')
   check(p.locator('.fv-apollo-reading-bridge .cta').get_attribute('href')==FREE,'Unapproved destination')
   check(p.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'),'Horizontal overflow '+name)
   if opts.get('has_touch'):nav.tap();check(p.evaluate('location.hash')=='#fv-apollo-reading-bridge','Touch jump')
   receipts.append({'context':name,'sha256':hashfile(folder/(name+'.png'))});c.close()
  c=browser.new_context();p=c.new_page();p.set_content(page);p.emulate_media(media='print')
  check(p.locator('.fv-apollo-lesson-key>div p').first.is_visible(),'Answer guide hidden in print')
  c.close();browser.close()
 (folder/'receipt.json').write_text(json.dumps({'status':'LOCAL_FIXTURE_PASS','screenshots':receipts,'axe':'NOT_EXECUTED','WP':'NOT_TESTED','revenue':'UNVERIFIED'},sort_keys=True,indent=2)+'\n')
 print('R213 PHP/Chromium fixture: PASS',len(receipts),'contexts')
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r213-smoke'))
