#!/usr/bin/env python3
"""R329 offline Chromium release replay; NOT installed WordPress or HTTP/CSP."""
import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import urlencode
from io import BytesIO
from pypdf import PdfReader
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
H=R/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=R/'apollo-r329/QA';OUT.mkdir(parents=True,exist_ok=True)
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PINS={P:'0048781b3dbea5f1fa44b688d9ca5053313fbf01',C:'b9441b73ba810af23e59e72f862f2e1f7ea81ccc',J:'f85617e5f12ba747908ac507261f69c377369de7'}

def blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def audit(page):
 return page.locator('section.fv-r281').first.evaluate('''r=>({
 docs:[...r.querySelectorAll('.fv-r281__source-list>li')].map(e=>e.dataset.fvEvidenceRole),
 media:[...r.querySelectorAll('[data-fv-media-record]')].map(e=>[e.dataset.fvImageRights,e.dataset.fvClaimProof]),
 links:[...r.querySelectorAll('a[data-fv-link-purpose]')].map(e=>e.href),
 cta:[...r.querySelectorAll('a[data-fv-cta]')].map(e=>e.href),
 overflow:document.documentElement.scrollWidth-innerWidth,
 receipt:[...r.querySelectorAll('.fv-r306__source-receipt a')].map(e=>[e.getBoundingClientRect().left,e.getBoundingClientRect().right,e.getBoundingClientRect().height]),
 invented:!!r.querySelector('[data-map-pin],[data-geo-edge],[data-lat],iframe,img,video')||r.hasAttribute('data-map-pin')})''')

def clean(a,w):
 assert a['docs']==['documented-textual-claim']*3
 assert a['media']==[['not-cleared-for-reuse','no']]*4
 assert len(a['links'])==17 and all(u.startswith(('https://www.nasa.gov/','https://sma.nasa.gov/')) for u in a['links'])
 assert a['cta']==[FREE] and not a['invented'] and a['overflow']<=1
 assert len(a['receipt'])==3 and all(x>=-1 and y<=w+1 and h>=40 for x,y,h in a['receipt'])

def fixture(page,html,css,js,query=''):
 page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
 page.add_script_tag(content=js)
 if query:page.evaluate('(q)=>history.replaceState(null,"","about:blank?"+q)',query)

def main():
 for p,sha in PINS.items():assert blob(p)==sha,(p,blob(p))
 assert 'r328-'+hashlib.sha256(C.read_bytes()).hexdigest()[:12] in P.read_text()
 subprocess.run(['php','-l',str(P)],check=True,capture_output=True)
 subprocess.run(['node','--check',str(J)],check=True,capture_output=True)
 html=subprocess.check_output(['php',str(H),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
 css=C.read_text();js=J.read_text();checks=0
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for w in [320,360,390,768,1024,1440,1920]:
    for enabled in [False,True]:
     page=browser.new_page(viewport={'width':w,'height':840},java_script_enabled=enabled,has_touch=w<=390,reduced_motion='reduce')
     page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
     if enabled:page.add_script_tag(content=js)
     page.locator('html').evaluate('(e)=>e.style.fontSize="64px"')
     page.locator('.fv-r306__source-receipt').evaluate('e=>e.open=true')
     clean(audit(page),w)
     if (w,enabled) in [(390,True),(1440,False)]:page.screenshot(path=str(OUT/f'r329-replay-{w}-{enabled}.png'),full_page=False)
     checks+=1;page.close()
   labels={'utm_source':'youtube','utm_medium':'organic_social','utm_campaign':'history_pilot_2026_11','utm_content':'apollo1_yt_valid2026'}
   scenarios=[(urlencode(labels),True),(urlencode(dict(labels,utm_campaign='apollo1_longform_2026_11')),True),
    (urlencode(dict(labels,utm_source='tiktok')),False),(urlencode(dict(labels,utm_campaign='history_pilot_2026_12')),False),
    (urlencode(dict(labels,utm_content='not_an_asset')),False),(urlencode(labels)+'&utm_source=youtube',False)]
   printed=[]
   for i,(q,valid) in enumerate(scenarios):
    page=browser.new_page(viewport={'width':390,'height':840})
    fixture(page,html,css,js,q)
    page.evaluate('''() => document.addEventListener('click',e=>{if(e.target.closest('a[data-fv-cta]'))e.preventDefault()})''')
    a=page.locator('a[data-fv-cta]');a.click()
    assert ('utm_source=' in a.get_attribute('href'))==valid
    if i==0:
     pdf=page.pdf(print_background=True)
     (OUT/'r329-replay-safe-print.pdf').write_bytes(pdf)
     for sheet in PdfReader(BytesIO(pdf)).pages:
      for ref in sheet.get('/Annots',[]):
       action=ref.get_object().get('/A');url=str(action.get('/URI')) if action and action.get('/URI') else ''
       if url:printed.append(url)
     assert FREE in printed and not any('utm_' in u or 'payhip' in u for u in printed)
     assert a.get_attribute('href')==FREE
    checks+=1;page.close()
  finally:browser.close()
 result={'stage':'R329','responsiveContexts':14,'trustedActivationCases':6,'pdfUriCount':len(printed),
         'pdfCampaignLeaks':0,'browser':'offline Chromium','realHTTP':False,'axeCoreExecuted':False,
         'installedWP':False,'productionCWV':False,'commercialSalesVerified':False,'checks':checks}
 (OUT/'r329-replay-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
 print('R329 committed replay PASS',checks,'contexts/scenarios; print annotations',len(printed))
if __name__=='__main__':main()
