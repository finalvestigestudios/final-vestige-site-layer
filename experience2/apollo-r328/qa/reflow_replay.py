#!/usr/bin/env python3
"""R328 source-controlled 320–1920px Chromium reflow replay; offline staging only."""
import hashlib, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
H=R/'apollo-r320/qa/wp_late_shortcodes.php'
PINS=[(P,'0048781b3dbea5f1fa44b688d9ca5053313fbf01'),(C,'b9441b73ba810af23e59e72f862f2e1f7ea81ccc'),(J,'f85617e5f12ba747908ac507261f69c377369de7')]
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def git_blob(path):
 b=path.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def audit(page):
 return page.locator('section.fv-r281').evaluate('''r=>({
 overflow:document.documentElement.scrollWidth-window.innerWidth,
 receipt:[...r.querySelectorAll('.fv-r306__source-receipt a')].map(a=>({x:a.getBoundingClientRect().right,h:a.getBoundingClientRect().height})),
 docs:[...r.querySelectorAll('.fv-r281__source-list>li')].map(x=>x.dataset.fvEvidenceRole),
 photos:[...r.querySelectorAll('[data-fv-media-record]')].map(x=>[x.dataset.fvClaimProof,x.dataset.fvImageRights]),
 cta:[...r.querySelectorAll('a[data-fv-cta]')].map(x=>x.href),
 external:[...r.querySelectorAll('a[href^="https://"]')].length,
 geo:!!r.querySelector('[data-map-pin],[data-geo-edge],[data-lat],iframe,img,video')})''')
def main():
 for f,sha in PINS: assert git_blob(f)==sha,(f,git_blob(f))
 css=C.read_text();js=J.read_text()
 assert 'r328-'+hashlib.sha256(C.read_bytes()).hexdigest()[:12] in P.read_text()
 subprocess.run(['php','-l',str(P)],check=True,capture_output=True)
 subprocess.run(['node','--check',str(J)],check=True,capture_output=True)
 body=subprocess.check_output(['php',str(H),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:')[0]
 count=0
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for w in [320,360,390,768,1024,1440,1920]:
    for enabled in [False,True]:
     page=browser.new_page(viewport={'width':w,'height':840},java_script_enabled=enabled,has_touch=w<=390,reduced_motion='reduce')
     page.set_content(body.replace('</head>','<style>'+css+'</style></head>'))
     if enabled:page.add_script_tag(content=js)
     page.locator('html').evaluate('(e)=>e.style.fontSize="64px"')
     page.locator('.fv-r306__source-receipt').evaluate('(e)=>e.open=true')
     a=audit(page)
     assert a['overflow']<=1 and len(a['receipt'])==3,(w,enabled,a)
     assert all(x['x']<=w+1 and x['h']>=40 for x in a['receipt'])
     assert a['docs']==['documented-textual-claim']*3
     assert a['photos']==[['no','not-cleared-for-reuse']]*4
     assert a['cta']==[FREE] and a['external']==18 and not a['geo']
     count+=1;page.close()
   # Destructive test: reconstruct pre-fix CTA styling and narrow padding.
   old=css.split('/* R328: 400%-text')[0].replace('.fv-r281__next a[data-fv-cta]{display:inline-flex','.fv-r281__next a{display:inline-flex')
   page=browser.new_page(viewport={'width':320,'height':840})
   page.set_content(body.replace('</head>','<style>'+old+'</style></head>'))
   page.locator('html').evaluate('(e)=>e.style.fontSize="64px"')
   page.locator('.fv-r306__source-receipt').evaluate('(e)=>e.open=true')
   assert audit(page)['overflow']>=40,'Previous source receipt overflow not detected'
   page.close()
  finally:browser.close()
 print('R328 committed Chromium replay PASS:',count,'responsive 400% contexts; old CSS negative control rejected')
if __name__=='__main__':main()
