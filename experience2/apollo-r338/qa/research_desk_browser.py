#!/usr/bin/env python3
"""R338 real Chromium acceptance on exact PHP-emitted six-record Research Desk.
Run from checkout: python experience2/apollo-r338/qa/research_desk_browser.py
Results describe offline fixture, NEVER installed WordPress or field CWV.
"""
import hashlib, json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[2]
SOURCES={
 BASE/'research-desk/final-vestige-ex2-research-desk.php':'fa7e8b0d9535bd2e87d46d484d9ff481b2e1e148',
 BASE/'research-desk/assets/source-ledger.css':'0ae12d1bb9e0e10cb8ce6286e205b500f7b8f304',
 BASE/'research-desk/assets/source-ledger.js':'32e757cc4dc8708397ff65ac21e89dd319781d78',
 BASE/'research-desk/templates/ledger.html':'d773d0de24d9eb0eaf073e007b135034c214fb51',
}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
OUT=Path(os.environ.get('FV_R338_OUT','/tmp/fv-apollo-r338'))
OUT.mkdir(parents=True,exist_ok=True)
for path,digest in SOURCES.items():
 b=path.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==digest, ('SOURCE DRIFT',str(path))
script=Path(__file__).with_name('research_desk_instances.php')
subprocess.run(['php',str(script)],check=True,capture_output=True)
html=subprocess.check_output(['php',str(script),'--emit-fixture'],text=True)
cases=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
 try:
  for width,js,font,forced,reduce in ([(w,True,16,False,False) for w in (320,360,390,768,1024,1440,1920)]+[(w,False,16,False,False) for w in (320,390,1440)]+[(320,True,64,False,False),(390,True,16,True,True)]):
   page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=width<=390,forced_colors='active' if forced else 'none',reduced_motion='reduce' if reduce else 'no-preference')
   try:
    page.set_content(html)
    if font!=16:page.add_style_tag(content='html{font-size:'+str(font)+'px!important}')
    d=page.evaluate("""() => {const roots=[...document.querySelectorAll('[data-fvx-ledger]')],ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
     return {roots:roots.length,ids,missing:[...document.querySelectorAll('[for],[aria-controls],[aria-labelledby]')].filter(e=>['for','aria-controls','aria-labelledby'].some(a=>e.getAttribute(a)?.split(' ').some(id=>!document.getElementById(id)))).length,overflow:document.documentElement.scrollWidth-innerWidth,geo:document.querySelectorAll('[data-geo-pin],[data-map-edge]').length,
      records:roots.map(r=>r.querySelectorAll('[data-fvx-record]').length),sources:roots.map(r=>r.querySelectorAll('[data-fvx-source-role=documentary-support]').length),
      photos:roots.map(r=>[...r.querySelectorAll('[data-fvx-source-role=contextual-photo-only]')].every(a=>a.dataset.fvxReuseReview==='required'&&a.dataset.fvxClaimProof==='no')),cta:roots.map(r=>[...r.querySelectorAll('footer a')].filter(a=>a.href.includes('finalvestige.com/')).map(a=>a.href)),
      targets:[...document.querySelectorAll('.fv-ex2-ledger__recordlinks a,.fv-ex2-ledger__footer a')].map(a=>{let b=a.getBoundingClientRect();return {h:b.height,l:b.left,r:b.right}})};}""")
    assert d['roots']==2 and d['records']==[6,6] and d['sources']==[6,6] and d['photos']==[True,True]
    assert len(d['ids'])==len(set(d['ids'])) and d['missing']==0
    assert d['geo']==0 and d['overflow']<=1 and d['cta']==[[FREE],[FREE]]
    assert all(t['h']>=43.9 and t['l']>=-1 and t['r']<=width+1 for t in d['targets'])
    first,second=page.locator('[data-fvx-ledger]').nth(0),page.locator('[data-fvx-ledger]').nth(1)
    summary=first.locator('details summary').first
    summary.focus();page.keyboard.press('Enter')
    assert first.locator('details').first.evaluate('(x)=>x.open')
    if js:
     first.locator('input[data-fvx-search]').fill('not a historical record')
     assert first.locator('[data-fvx-record]:visible').count()==0 and second.locator('[data-fvx-record]:visible').count()==6
     first.locator('input[data-fvx-search]').fill('')
     assert first.locator('[data-fvx-record]:visible').count()==6
    else:
     assert first.locator('[data-fvx-record]:visible').count()==6 and first.locator('[data-fvx-tools]').is_hidden()
    if width in (320,390,1440) and not forced:
     page.evaluate('scrollTo(0,0)')
     page.screenshot(path=str(OUT/f'r338-{width}-'+('js' if js else 'nojs')+'.png'),full_page=False)
    cases.append({'width':width,'javascript':js,'rootFontPx':font,'forcedColors':forced,'reducedMotion':reduce,'status':'PASS','overflow':d['overflow']})
    print('PASS',width,js,font,forced,flush=True)
   finally:page.close()
 finally:browser.close()
(OUT/'r338-browser-receipt.json').write_text(json.dumps({'classification':'OFFLINE PHP+Chromium only, NOT installed WP, axe or production','results':cases,'passed':len(cases),'release':'HARD HOLD'},indent=2)+'\n')
print('R338 PASS',len(cases),'offline Chromium contexts. Production remains blocked.')
