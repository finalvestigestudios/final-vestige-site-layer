#!/usr/bin/env python3
"""R330 offline Chromium CSP failure-path acceptance. NOT WordPress or HTTP/CSP."""
import hashlib, json, subprocess
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader
from playwright.sync_api import Error, sync_playwright

R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
H=R/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=R/'apollo-r330/QA'; OUT.mkdir(parents=True,exist_ok=True)
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PINS={P:'0048781b3dbea5f1fa44b688d9ca5053313fbf01',C:'b9441b73ba810af23e59e72f862f2e1f7ea81ccc',J:'f85617e5f12ba747908ac507261f69c377369de7'}
WIDTHS=[320,360,390,768,1024,1440,1920]
POLICIES={
 'allowed':"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'",
 'blocked-script':"default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; base-uri 'none'",
 'blocked-css-script':"default-src 'none'; script-src 'none'; style-src 'none'; base-uri 'none'",
 'disabled-javascript':"default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; base-uri 'none'"}

def blob(p):
 b=p.read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def fixture(html,css,policy):
 return html.replace('</head>','<meta http-equiv="Content-Security-Policy" content="'+POLICIES[policy]+'"><style>'+css+'</style><script>window.__unsafe=true</script></head>')

def evidence(page,unstyled=False):
 a=page.locator('section.fv-r281').first.evaluate('''r=>({
  d:[...r.querySelectorAll('.fv-r281__source-list>li')].map(e=>e.dataset.fvEvidenceRole),
  m:[...r.querySelectorAll('[data-fv-media-record]')].map(e=>[e.dataset.fvImageRights,e.dataset.fvClaimProof]),
  src:[...r.querySelectorAll('a[data-fv-link-purpose]')].map(e=>e.href),
  cta:[...r.querySelectorAll('a[data-fv-cta]')].map(e=>e.href),
  invented:r.hasAttribute('data-map-pin')||!!r.querySelector('[data-map-pin],[data-geo-edge],[data-lat],img,iframe,video'),
  overflow:document.documentElement.scrollWidth-innerWidth,
  links:[...r.querySelectorAll('.fv-r306__source-receipt a')].map(e=>{let b=e.getBoundingClientRect();return [b.left,b.right,b.height]})
 })''')
 assert a['d']==['documented-textual-claim']*3
 assert a['m']==[['not-cleared-for-reuse','no']]*4
 assert len(a['src'])==17 and all(u.startswith(('https://www.nasa.gov/','https://sma.nasa.gov/')) for u in a['src'])
 assert a['cta']==[FREE] and not a['invented'] and len(a['links'])==3
 if not unstyled:
  assert a['overflow']<=1
  assert all(x>=-1 and y<=page.viewport_size['width']+1 and h>=40 for x,y,h in a['links'])
 return a

def main():
 for p,s in PINS.items():assert blob(p)==s,(p,blob(p))
 subprocess.run(['php','-l',str(P)],check=True,capture_output=True)
 subprocess.run(['node','--check',str(J)],check=True,capture_output=True)
 html=subprocess.check_output(['php',str(H),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
 css=C.read_text();js=J.read_text();tested=0
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for policy in POLICIES:
    for w in WIDTHS:
     pg=b.new_page(viewport={'width':w,'height':850},java_script_enabled=policy!='disabled-javascript',reduced_motion='reduce',has_touch=w<=390)
     req=[];pg.on('request',lambda r:req.append(r.url))
     pg.set_content(fixture(html,css,policy))
     if policy in ('blocked-script','blocked-css-script'):
      try:pg.add_script_tag(content=js)
      except Error as ex:assert 'Content Security Policy' in str(ex)
      else:raise AssertionError('script-src none did not block Apollo JS')
      assert pg.evaluate('typeof window.__unsafe')=='undefined'
     if policy=='allowed':
      pg.add_script_tag(content=js)
      assert pg.evaluate('window.__unsafe===true')
     pg.locator('html').evaluate('(e,n)=>e.style.fontSize=n+"px"',16 if policy=='blocked-css-script' else 64)
     pg.locator('.fv-r306__source-receipt').evaluate('e=>e.open=true')
     evidence(pg,policy=='blocked-css-script')
     assert not req,req
     if policy=='blocked-script' and w==390:
      pg.locator('.fv-r281__rail a').first.focus();pg.keyboard.press('Enter')
      assert pg.evaluate('location.hash.endsWith("-event-1")')
      pg.locator('.fv-r281__source-jump a').first.click()
      assert pg.evaluate('location.hash.endsWith("-source-1")')
      pg.locator('.fv-r281__source-return a').first.click()
      assert pg.evaluate('location.hash.endsWith("-event-1")')
     if policy=='allowed' and w==390:
      pdf=pg.pdf(print_background=True)
      links=[]
      for sheet in PdfReader(BytesIO(pdf)).pages:
       for x in sheet.get('/Annots',[]):
        action=x.get_object().get('/A')
        if action and action.get('/URI'):links.append(str(action.get('/URI')))
      assert FREE in links and not any('utm_' in u or 'payhip' in u for u in links)
     tested+=1;pg.close()
   mutations=[('data-fv-experience="apollo-1"','data-fv-experience="apollo-1" data-map-pin="invented"'),
    ('href="'+FREE+'" data-fv-cta','href="https://payhip.com/unapproved" data-fv-cta'),
    ('data-fv-image-rights="not-cleared-for-reuse"','data-fv-image-rights="cleared"'),
    ('data-fv-evidence-role="documented-textual-claim"','data-fv-evidence-role="contextual-media-only"')]
   for original,bad in mutations:
    assert original in html
    pg=b.new_page(viewport={'width':390,'height':850})
    pg.set_content(fixture(html.replace(original,bad,1),css,'blocked-script'))
    pg.locator('.fv-r306__source-receipt').evaluate('e=>e.open=true')
    try:evidence(pg)
    except AssertionError:pass
    else:raise AssertionError('Unsafe mutation incorrectly accepted: '+bad)
    pg.close()
  finally:b.close()
 report={'stage':'R330','chromiumCspContexts':tested,'unsafeMutationsRejected':len(mutations),
  'widths':WIDTHS,'modes':list(POLICIES),'realCSPHeader':False,'realHTTP':False,
  'axeCoreExecuted':False,'installedWordPress':False,'actualGrokAssetVerified':False,
  'verifiedSale':False,'release':'HARD HOLD'}
 (OUT/'r330-committed-replay.json').write_text(json.dumps(report,indent=2)+'\n')
 print('R330 replay PASS:',tested,'Chromium CSP fixture contexts;',len(mutations),'negative controls')
if __name__=='__main__':main()
