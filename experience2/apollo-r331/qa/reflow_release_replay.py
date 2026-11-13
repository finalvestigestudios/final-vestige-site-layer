#!/usr/bin/env python3
"""R331 replay: real, offline Chromium; not genuine axe, HTTP, or WordPress QA."""
import hashlib,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
H=R/'apollo-r320/qa/wp_late_shortcodes.php'
PINS={P:'f59a083de8d0774ed7210bfe4e18726feea73f76',C:'577a5d33518baec6e1beff1517779264d342bc50',J:'f85617e5f12ba747908ac507261f69c377369de7'}
WIDTHS=[320,360,390,768,1024,1440,1920]
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def inspect(page,w):
 return page.locator('.fv-r281').first.evaluate('''(root)=>{
 const sources=[...root.querySelectorAll('.fv-r281__authority-ledger a[data-fv-link-purpose],.fv-r281__reconciliation-list a[data-fv-link-purpose]')];
 const positions=sources.map(a=>{let r=a.getBoundingClientRect();return [r.width,r.height,r.left,r.right]});
 return {positions,overflow:document.documentElement.scrollWidth-innerWidth,
  docs:[...root.querySelectorAll('.fv-r281__source-list>li')].map(x=>x.dataset.fvEvidenceRole),
  media:[...root.querySelectorAll('[data-fv-media-record]')].map(x=>x.dataset.fvImageRights),
  links:[...root.querySelectorAll('a[data-fv-link-purpose]')].map(x=>x.href),
  cta:[...root.querySelectorAll('a[data-fv-cta]')].map(x=>x.href),
  geo:!!root.querySelector('img,iframe,[data-map-pin],[data-geo-edge],[data-lat],[data-lng]')};}''')
def run():
 for p,s in PINS.items():assert blob(p)==s,(p,blob(p))
 subprocess.run(['php','-l',str(P)],check=True,capture_output=True)
 subprocess.run(['node','--check',str(J)],check=True,capture_output=True)
 html=subprocess.check_output(['php',str(H),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
 css=C.read_text();js=J.read_text();mark='/* R331: nested custody cards must retain a nonzero content box'
 assert css.count(mark)==1
 count=0
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   bad=browser.new_page(viewport={'width':320,'height':850},java_script_enabled=False)
   bad.set_content(html.replace('</head>','<style>'+css.split(mark)[0]+'</style></head>'))
   bad.evaluate('document.documentElement.style.fontSize="64px"')
   bad.locator('details').evaluate_all('els=>els.forEach(e=>e.open=true)')
   assert sum(x[0]<1 for x in inspect(bad,320)['positions'])==7
   bad.close()
   for enabled in (True,False):
    for w in WIDTHS:
     for font in (16,32,64):
      page=browser.new_page(viewport={'width':w,'height':850},java_script_enabled=enabled,
        reduced_motion='reduce',has_touch=w<=390,forced_colors='active' if w==390 and font==32 else 'none')
      requests=[];page.on('request',lambda r:requests.append(r.url))
      page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
      if enabled:page.add_script_tag(content=js)
      page.evaluate('(f)=>document.documentElement.style.fontSize=f+"px"',font)
      page.locator('details').evaluate_all('els=>els.forEach(e=>e.open=true)')
      s=inspect(page,w)
      assert len(s['positions'])==7 and all(x>=24 and y>=40 and z>=-1 and q<=w+1 for x,y,z,q in s['positions']),s['positions']
      assert s['overflow']<=1 and s['docs']==['documented-textual-claim']*3
      assert s['media']==['not-cleared-for-reuse']*4 and len(s['links'])==17
      assert all(link.startswith(('https://www.nasa.gov/','https://sma.nasa.gov/')) for link in s['links'])
      assert s['cta']==[FREE] and not s['geo'] and not requests
      count+=1;page.close()
  finally:browser.close()
 report={'sprint':'R331','contextsPassed':count,'negativeControlZeroWidth':7,'sourceBlobs':{str(k.relative_to(R)):v for k,v in PINS.items()},'installedWordPress':False,'axeExecuted':False,'productionLCP':None,'productionCLS':None,'release':'HARD HOLD'}
 out=R/'apollo-r331/QA';out.mkdir(exist_ok=True,parents=True)
 (out/'r331-committed-replay.json').write_text(json.dumps(report,indent=2)+'\n')
 print('R331 COMMITTED REPLAY PASS:',count,'real Chromium contexts, seven baseline collapsed links reproduced')
if __name__=='__main__':run()
