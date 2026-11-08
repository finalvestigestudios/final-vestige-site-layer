#!/usr/bin/env python3
"""Real localhost HTTP Chromium + PHP shortcode fixture; no installed WP or axe claim."""
from __future__ import annotations
import json,subprocess,sys,hashlib,threading,contextlib,urllib.parse,urllib.request,http.server,socketserver
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r208 import build,digest,RECORDS,BOARD,RIGHTS
DIST=ROOT/'dist'
CASES=[('320',320,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),('390-nojs',390,{'java_script_enabled':False}),('390-touch',390,{'is_mobile':True,'has_touch':True}),('390-reduced',390,{'reduced_motion':'reduce'}),('390-forced',390,{'forced_colors':'active'}),('320-csszoom200',320,{'zoom':2})]

def audit(html):
 soup=BeautifulSoup(html,'html.parser');root=soup.select_one('article.fv-apollo-atlas');assert root
 capsule=root.select_one('section#fv-apollo-custody');assert capsule and capsule.get('aria-labelledby')=='fv-apollo-custody-title'
 assert capsule.find_previous('section',id='fv-apollo-gallery') and capsule.find_next('section',class_='fv-apollo-reading-lab')
 assert capsule.select_one('#fv-apollo-custody-title')
 assert len(capsule.select('ol.fv-apollo-custody-list > li'))==4
 report_card=capsule.select_one('li[data-source-record="Apollo 204 Review Board"]')
 assert report_card
 assert [(x.get('datetime'),x.get_text(' ',strip=True)) for x in report_card.select('time')]==[('1967-01-27','27 January 1967'),('1967-04','April 1967')]
 assert report_card.select_one('a[href="https://www.nasa.gov/apollo-1-resources/"]')
 assert 'retrospective' in report_card.get_text(' ',strip=True)
 assert 'Photograph dates and the accident date are not report publication dates.' in capsule.get_text(' ',strip=True)
 for n,(li,rec) in enumerate(zip(capsule.select('ol.fv-apollo-custody-list > li'),RECORDS),1):
  assert li['data-source-record']==rec['id'] and li['data-evidence-type']==rec['type']
  assert li.select_one('a[href="#'+rec['target']+'"]')
  assert root.select_one('#'+rec['target'])
  external=li.select_one('a[href="'+rec['url']+'"]')
  assert external and external.get('aria-describedby')=='fv-apollo-custody-limit-'+str(n)
  assert li.select_one('#fv-apollo-custody-limit-'+str(n))
  assert rec['does_not_support'] in li.get_text(' ',strip=True)
 assert capsule.select_one('a[href="'+RIGHTS+'"]')
 assert len(root.select('a.cta'))==1
 assert len(root.select('.fv-apollo-rail-source'))==4
 assert len(root.select('details'))==11
 assert not root.select('[data-geo],[data-lat],[data-lng],form[data-purchase],a[data-affiliate]')
 ids=[e['id'] for e in root.select('[id]')];assert len(ids)==len(set(ids))
 assert all(a['href'][1:] in ids for a in root.select('a[href^="#"]'))
 assert len(root.select('.fv-apollo-custody img'))==0
 return {'source_records':4,'NASA_direct_links':4,'verified_anchor_targets':4,'editorial_ctas':1,'paid_ctas':0,'native_disclosures':11}

def main(out):
 out.mkdir(parents=True,exist_ok=True)
 manifest=build();assert not manifest['source_chain_verified']
 for f,h in manifest['files'].items():assert digest((DIST/f).read_bytes())==h
 assert digest((DIST/'custody-ledger.json').read_bytes())==manifest['custody_ledger_sha256']
 ledger=json.loads((DIST/'custody-ledger.json').read_text())
 assert ledger['records']==list(RECORDS) and ledger['geo_pins']==[] and not ledger['commercial_photo_rights_cleared']
 contract=ledger['chronology_date_contract']
 assert contract['accident_event_date']=='1967-01-27' and contract['board_report_completed_month']=='1967-04'
 assert contract['report_date_precision']=='month' and contract['rights_not_cleared'] is True
 subprocess.run(['php','-l',str(DIST/'fv-ex2-apollo-r208.php')],check=True,capture_output=True)
 def render(variant):
  return json.loads(subprocess.check_output(['php',str(DIST/'wp-render-shim-r208.php'),str(DIST/'fv-ex2-apollo-r208.php'),variant],text=True))
 normal=render('normal');assert normal['fallback'] is False
 assert render('printed')['fallback'] is False
 assert render('late')['fallback'] is True
 html=normal['html'];checks=audit(html)
 mutations={
  'wrong_photo':html.replace('data-source-record="S67-21294"','data-source-record="S67-19766"',1),
  'remove_rights':html.replace('Read NASA advertising guidance','Generic marketing',1),
  'remove_record':html.replace('data-evidence-type="technical-report"','data-evidence-type="photo"',1),
  'inject_sales':html.replace('class="cta"','class="cta" data-affiliate="1"',1),
  'break_source':html.replace('href="https://www.nasa.gov/image-detail/amf-s67-15717/" aria-describedby="fv-apollo-custody-limit-2"','href="https://example.invalid/" aria-describedby="fv-apollo-custody-limit-2"',1),
  'break_anchor':html.replace('href="#fv-apollo-photo-1966"','href="#missing-evidence"',1),
  'duplicate_id':html.replace('id="fv-apollo-custody"','id="fv-apollo-gallery"',1),
  'remove_custody_heading':html.replace('id="fv-apollo-custody-title"','id="no-custody-heading"',1),
  'falsify_report_month':html.replace('datetime="1967-04"','datetime="1967-01-27"',1),
  'remove_report_timing_source':html.replace('href="https://www.nasa.gov/apollo-1-resources/"','href="https://example.invalid/report"',1),
 }
 rejected=[]
 for name,changed in mutations.items():
  try:
   if name=='remove_rights': assert 'Read NASA advertising guidance' in BeautifulSoup(changed,'html.parser').select_one('#fv-apollo-custody').get_text(' ',strip=True)
   audit(changed)
  except (AssertionError,AttributeError,KeyError):rejected.append(name)
 assert set(rejected)==set(mutations),(rejected,set(mutations))
 css=(DIST/'assets/atlas-scoped.css').read_text()
 js=(DIST/'assets/campaign-handoff.js').read_text()
 doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/atlas.css"></head><body>'+html+'<script defer src="/campaign.js"></script></body></html>'
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   path=urllib.parse.urlsplit(self.path).path
   if path in ('/','/index.html'):
    data=doc.encode('utf8');kind='text/html; charset=utf-8'
   elif path=='/atlas.css':data=css.encode('utf8');kind='text/css; charset=utf-8'
   elif path=='/campaign.js':data=js.encode('utf8');kind='text/javascript; charset=utf-8'
   elif path=='/original-investigation':data=b'Original investigation fixture';kind='text/plain'
   else:self.send_error(404);return
   self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 class Server(socketserver.ThreadingMixIn,http.server.HTTPServer):daemon_threads=True
 with Server(('127.0.0.1',0),Handler) as server:
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  url='http://127.0.0.1:'+str(server.server_port)+'/'
  assert urllib.request.urlopen(url,timeout=5).status==200
  assert urllib.request.urlopen(url+'atlas.css',timeout=5).status==200
  assert urllib.request.urlopen(url+'campaign.js',timeout=5).status==200
  fixture='https://apollo-local-fixture.test/'
  results=[]
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
   for name,width,opts in CASES:
    opts=dict(opts);zoom=opts.pop('zoom',None)
    ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**opts)
    page=ctx.new_page();errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
    page.set_content(doc.replace('<link rel="stylesheet" href="/atlas.css">','<style>'+css+'</style>').replace('<script defer src="/campaign.js"></script>','<script>'+js+'</script>'),wait_until='load')
    page.evaluate('''() => { window.__vitals={lcp:null,cls:0}; try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__vitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){};try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){}}''')
    if zoom:page.locator('.fv-apollo-atlas').evaluate('e=>e.style.zoom="200%"')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),name+' overflow'
    assert page.get_by_role('heading',name='Four records. Four limits on what we can conclude.').count()==1
    cards=page.locator('.fv-apollo-custody-list > li');assert cards.count()==4
    assert cards.nth(2).locator('time[datetime="1967-01-27"]').count()==1
    assert cards.nth(2).locator('time[datetime="1967-04"]').count()==1
    for i,rec in enumerate(RECORDS):
     card=cards.nth(i)
     a=card.get_by_role('link',name='Inspect original NASA record '+rec['id'])
     assert a.get_attribute('href')==rec['url']
     assert a.get_attribute('aria-describedby')=='fv-apollo-custody-limit-'+str(i+1)
     internal=card.get_by_role('link',name='Examine the record in this atlas')
     internal.focus();assert internal.evaluate('e=>document.activeElement===e')
     internal.press('Enter');assert page.evaluate('location.hash')=='#'+rec['target']
     assert page.locator('#'+rec['target']).count()==1
    if opts.get('has_touch'):
     cards.first.get_by_role('link',name='Examine the record in this atlas').tap()
     assert page.evaluate('location.hash')=='#'+RECORDS[0]['target']
    ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
    for term in ['Four records. Four limits','Inspect original NASA record S66-58038','Read original investigation']:
     assert any(term in str(n.get('name',{}).get('value','')) for n in ax),name+' accessibility-tree missing '+term
    # Ensure optional JS only enriches the existing editorial CTA, never NASA source links.
    assert page.locator('.fv-apollo-custody a[href*="utm_"]').count()==0
    if name=='390':
     page.emulate_media(media='print')
     assert page.locator('.fv-apollo-custody-list li').count()==4
     page.emulate_media(media='screen')
    assert not errors,(name,errors)
    page.evaluate('''() => {document.activeElement.blur();document.querySelectorAll('details[open]').forEach(e=>e.open=false);scrollTo(0,0)}''')
    page.wait_for_timeout(180)
    dest=out/(name+'.png');page.screenshot(path=str(dest),full_page=True,animations='disabled')
    results.append({'case':name,'width':width,'sha256':digest(dest.read_bytes()),'LCP_CLS_LOCALHTTP_only':page.evaluate('window.__vitals') if opts.get('java_script_enabled',True) else None,'overflow':False,'pageerrors':len(errors)})
    ctx.close()
   ver=browser.version;browser.close()
  server.shutdown()
 receipt={'release':'r208','QA':'Independent local HTTP responses validated via urllib; Chromium set_content fixture (browser navigation blocked by administrator), PHP shortcode shim, not installed WP','chrome_version':ver,'checks':checks,'negative_tests_rejected':rejected,'cases':results,'genuine_axe_core':False,'CI_exact_HEAD':False,'installed_WP':False,'confirmed_orders':False,'source_chain_verified':False,'commercial_rights_certified':False,'staging_hold':True}
 (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'PASS':True,'chromium':ver,'contexts':len(results),'negative_tests':len(rejected),'http_server_checked_by_urllib':True,'chromium_fixture_set_content':True}))
if __name__=='__main__':main(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/r208-qa'))
