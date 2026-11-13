#!/usr/bin/env python3
"""R326 read-only NASA source classification and Chromium release gate."""
import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2]
P=R/'apollo-r281/apollo-source-experience.php'
C=R/'apollo-r281/assets/apollo-source-experience.css'
J=R/'apollo-r281/assets/apollo-cache-continuation.js'
O=R/'apollo-r326/QA';O.mkdir(exist_ok=True,parents=True)
PIN=[('php',P,'91745c286b2f23fb8a93058afb58905a2756714e'),
     ('css',C,'550e1dc6ac869ebbda1b371343a6cdd91f8608f4'),
     ('js',J,'f85617e5f12ba747908ac507261f69c377369de7')]
DOCS={'nasa_mission':'https://www.nasa.gov/mission/apollo-1/',
      'nasa_proceedings':'https://www.nasa.gov/history/Apollo204/proceed.html',
      'nasa_board':'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
W=(320,360,390,768,1024,1440,1920)
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def snapshot_review():
 s=json.loads((R/'apollo-r326/qa/pr158_custody_snapshot.json').read_text())
 assert (s['researchDeskPR'],s['headSHA'],s['ledgerBlobSHA'],len(s['cards']))==(158,'250d7f05a4de037e73826dcf0cfaef0ec4c29383','403d128c57b9bc82dac7c619651689070edef86c',6)
 flagged=[]
 for card in s['cards']:
  assert len(card['urls'])==2 and all(urlsplit(u).hostname=='www.nasa.gov' for u in card['urls'])
  if card['kind'] in ('PRIMARY REVIEW BOARD RECORD','INSTRUMENT CHRONOLOGY') and '/image-detail/' in card['urls'][0]:
   flagged.append({'record':card['id'],'kind':card['kind'],'firstURL':card['urls'][0],
                   'secondURL':card['urls'][1],'issue':'Photo accession must not be presented as primary Board or instrument evidence; second linked Board report can support textual findings.'})
 assert len(flagged)==2,'Review snapshot changed: do not silently pass an unreviewed Research Desk update'
 return s,flagged
def capture(pg):
 return pg.locator('section.fv-r281').evaluate('''r=>({status:r.dataset.fvEvidenceStatus,
 docs:[...r.querySelectorAll('.fv-r281__source-list>li')].map(e=>({id:e.dataset.fvSourceId,role:e.dataset.fvEvidenceRole,claim:e.dataset.fvCitesClaim,href:e.querySelector('a[data-fv-link-purpose="official-evidence-source"]')?.href})),
 photos:[...r.querySelectorAll('[data-fv-media-record]')].map(e=>({rights:e.dataset.fvImageRights,role:e.dataset.fvEvidenceRole,proof:e.dataset.fvClaimProof,href:e.querySelector('a[data-fv-link-purpose="contextual-media-source"]')?.href})),
 ctas:[...r.querySelectorAll('a[data-fv-cta]')].map(e=>e.href),
 noGeo:!r.querySelector('[data-lat],[data-lng],[data-geo-edge]'),
 noEmbeddedMedia:!r.querySelector('img,video,iframe'),
 noEndorsement:r.textContent.includes('NASA does not endorse this website.')})''')
def safe(d):
 assert d['status']=='editorial-review-pending'
 assert len(d['docs'])==3 and len(d['photos'])==4 and d['ctas']==[FREE]
 for i,(key,url) in enumerate(DOCS.items(),1):
  a=d['docs'][i-1];assert a=={'id':key,'role':'documented-textual-claim','claim':f'apollo-1-claim-{i}','href':url}
 for a in d['photos']:
  assert a['rights']=='not-cleared-for-reuse' and a['role']=='contextual-media-only' and a['proof']=='no'
  assert urlsplit(a['href']).hostname=='www.nasa.gov' and urlsplit(a['href']).path.startswith('/image-detail/')
 assert d['noGeo'] and d['noEmbeddedMedia'] and d['noEndorsement']
def main():
 for k,p,sha in PIN:
  assert blob(p.read_bytes())==sha,k+' changed since review'
 subprocess.run(['php','-l',str(P)],check=True,capture_output=True)
 subprocess.run(['node','--check',str(J)],check=True,capture_output=True)
 s,flagged=snapshot_review()
 raw=subprocess.check_output(['php',str(R/'apollo-r320/qa/wp_late_shortcodes.php'),'late-dynamic','1'],text=True)
 html,queue=raw.split('<!--R320_QUEUE:',1)
 assert json.loads(queue.split('-->')[0])['calls']==1
 css=C.read_text();js=J.read_text();receipt=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for w in W:
    for enabled in (False,True):
     pg=browser.new_page(viewport={'width':w,'height':850},java_script_enabled=enabled,
                         has_touch=w<=390,reduced_motion='reduce')
     pg.goto('about:blank')
     if enabled: pg.evaluate('''() => {window.__perf={lcp:[],cls:[]};
       new PerformanceObserver(x=>__perf.lcp.push(...x.getEntries().map(y=>y.startTime))).observe({type:'largest-contentful-paint',buffered:true});
       new PerformanceObserver(x=>__perf.cls.push(...x.getEntries().filter(y=>!y.hadRecentInput).map(y=>y.value))).observe({type:'layout-shift',buffered:true});}''')
     pg.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
     if enabled:pg.add_script_tag(content=js)
     pg.wait_for_timeout(120)
     safe(capture(pg));assert pg.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
     for selector in ('.fv-r281__source-jump a','.fv-r281__source-return a','.fv-r307__continue-return'):
      pg.locator(selector).first.click()
      assert pg.evaluate('document.activeElement.id===location.hash.slice(1)'),selector
     safe(capture(pg))
     perf=pg.evaluate('window.__perf||null') if enabled else None
     if enabled and w in (390,1440):pg.screenshot(path=str(O/f'r326-{w}-custody.png'))
     receipt.append({'width':w,'js':enabled,'documents':3,'contextualPhotos':4,
                     'navigationFocus':'PASS','offlineLCPms':max(perf['lcp']) if perf and perf['lcp'] else None,
                     'offlineCLS':round(sum(perf['cls']),5) if perf else None})
     pg.close()
   pg=browser.new_page();pg.set_content(html)
   mutations={'photo_as_report':"e=>e.querySelector('.fv-r281__source-list li a').href='https://www.nasa.gov/image-detail/amf-s67-21294/'",
              'photo_as_proof':"e=>e.querySelector('[data-fv-media-record]').dataset.fvClaimProof='yes'",
              'merchant_redirect':"e=>e.querySelector('a[data-fv-cta]').href='https://payhip.com/unknown'",
              'invented_pin':"e=>e.querySelector('.fv-r281__source-list li').dataset.lat='28.6083'",
              'imaginary_rights':"e=>e.querySelector('[data-fv-media-record]').dataset.fvImageRights='cleared'"}
   for name,mutation in mutations.items():
    pg.locator('section.fv-r281').evaluate(mutation)
    try:safe(capture(pg))
    except AssertionError:pass
    else:raise AssertionError('Undetected unsafe mutation '+name)
    pg.set_content(html)
   pg.close()
  finally:browser.close()
 result={'version':'R326','sourceGitBlobs':{k:v for k,_,v in PIN},'browserContexts':receipt,
         'unsafeMutationsDetected':list(mutations),'researchDeskHead':s['headSHA'],
         'researchDeskLedgerBlob':s['ledgerBlobSHA'],'researchDeskHOLD':flagged,
         'axe':'NOT EXECUTED','nativeBrowserHttp':'BLOCKED_BY_ADMINISTRATOR',
         'WordPressCDN':'NOT VERIFIED','salesAndRevenue':'NOT COMPUTABLE'}
 (O/'r326-source-custody-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
 print('R326: PASS',len(receipt),'Chromium contexts;',len(mutations),'mutants detected;',len(flagged),'Research Desk release holds')
if __name__=='__main__':main()
