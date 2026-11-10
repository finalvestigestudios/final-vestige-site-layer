#!/usr/bin/env python3
"""Browser QA with EXACT PR #158 PHP, HTML, CSS, JS + R270 PHP filter.
Offline Playwright set_content: NOT installed WordPress, true zoom, axe or HTTP.
"""
import hashlib,json,pathlib,subprocess,sys
from playwright.sync_api import sync_playwright
BASE=pathlib.Path(__file__).resolve().parents[1]
SRC=BASE/'fixtures/research-desk'
BLOBS={'templates/ledger.html':'403d128c57b9bc82dac7c619651689070edef86c','assets/source-ledger.css':'b8cf00afeceba115a9e9d19044fc11dcf2890cbe','assets/source-ledger.js':'32e757cc4dc8708397ff65ac21e89dd319781d78','final-vestige-ex2-research-desk.php':'d1879a90101b5475990132369178f42743f4b57c'}
def gh_blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def check(p,m):
 if not p:raise AssertionError(m)
def main(out):
 out.mkdir(parents=True,exist_ok=True)
 for path,expected in BLOBS.items():check(gh_blob(SRC/path)==expected,'original source drift '+path)
 check(gh_blob(BASE/'fixtures/rd-instance-scope.php')=='a3d470c8867ec4111bcdbbc956ee952a866ac8e7','R270 source drift')
 doc=subprocess.run(['php',str(BASE/'qa/source_gate.php')],capture_output=True,check=True).stdout.decode()
 css=(SRC/'assets/source-ledger.css').read_text();js=(SRC/'assets/source-ledger.js').read_text()
 records=[];images={}
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for w in (320,390,768,1440,1920):
   for enabled in (False,True):
    context=browser.new_context(viewport={'width':w,'height':900},java_script_enabled=enabled,has_touch=w<=390,is_mobile=w<=390,reduced_motion='reduce')
    page=context.new_page();network=[]
    page.on('request',lambda r:network.append(r.url))
    html=doc.replace('</head>','<style>body{margin:0;background:#090a0a}</style><style>'+css+'</style></head>').replace('</body>',('<script>'+js+'</script>' if enabled else '')+'</body>')
    page.set_content(html)
    ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
    check(len(ids)==27 and len(ids)==len(set(ids)),'duplicate IDs')
    roots=page.locator('[data-fvx-ledger]');check(roots.count()==3,'missing Research Desks')
    for root in roots.all():
     check(root.locator('[data-fvx-record]').count()==6,'record lost')
     check(root.locator('a[href^="https://www.nasa.gov/"]').count()==13,'NASA source lost')
     check(root.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count()==1,'free investigation lost')
     for element in root.locator('[for],[aria-labelledby],[aria-controls]').all():
      for attribute in ('for','aria-labelledby','aria-controls'):
       target=element.get_attribute(attribute)
       if target:check(root.locator('[id="'+target+'"]').count()==1,'bad IDREF '+target)
    check(not network,'unexpected network')
    check(page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),'horizontal overflow')
    if enabled:
     search=page.locator('input[data-fvx-search]');check(search.count()==3,'search lost')
     search.nth(1).fill('S67-21294')
     check(roots.nth(1).locator('article:visible').count()==1,'search failed')
     check(roots.nth(0).locator('article:visible').count()==6,'cross-instance leak')
     search.nth(1).fill('')
    else:
     check(roots.nth(1).locator('[data-fvx-tools]').is_hidden(),'no-JS not fail open')
     summary=roots.nth(1).locator('summary').first;summary.focus();page.keyboard.press('Enter')
     check(roots.nth(1).locator('details').first.get_attribute('open') is not None,'native disclosure broken')
    if w in (390,1440):
     name=str(w)+('-js' if enabled else '-nojs')+'.png'
     page.screenshot(path=str(out/name),animations='disabled')
     images[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    records.append({'width':w,'javascript':enabled,'result':'PASS'})
    context.close()
  browser.close()
 receipt={'sources':BLOBS,'cases':records,'screenshots':images,'limitations':['offline set_content','no installed WordPress/HTTP','no genuine axe or screenreader','no native zoom or field LCP/CLS']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print('R271',len(records),'PASS','receipt',hashlib.sha256((out/'receipt.json').read_bytes()).hexdigest())
if __name__=='__main__':main(pathlib.Path(sys.argv[1]))
