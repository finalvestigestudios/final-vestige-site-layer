#!/usr/bin/env python3
"""R272 exact-source offline Chromium acceptance after PHP asset-preflight simulation.
Neither a WordPress installation nor axe-core. No network, no product activation.
"""
import hashlib, json, pathlib, subprocess, sys
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[2]
R271=ROOT/'apollo-r271'
R272=ROOT/'apollo-r272'
SOURCE=R271/'fixtures/research-desk'
SHAS={'templates/ledger.html':'403d128c57b9bc82dac7c619651689070edef86c',
      'assets/source-ledger.css':'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
      'assets/source-ledger.js':'32e757cc4dc8708397ff65ac21e89dd319781d78',
      'final-vestige-ex2-research-desk.php':'d1879a90101b5475990132369178f42743f4b57c'}
def sha_git(file):
 raw=file.read_bytes();return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
def assert_true(value,reason):
 if not value:raise AssertionError(reason)
def main(out):
 out.mkdir(parents=True,exist_ok=True)
 for path,sha in SHAS.items():assert_true(sha_git(SOURCE/path)==sha,'source drift '+path)
 assert_true(sha_git(R271/'fixtures/rd-instance-scope.php')=='a3d470c8867ec4111bcdbbc956ee952a866ac8e7','R270 drift')
 gate=subprocess.run(['php',str(R272/'qa/preflight_gate.php')],check=True,capture_output=True,text=True)
 assert_true('20/20' in gate.stdout,'WP preflight PHP gate failed')
 html=subprocess.run(['php',str(R271/'qa/source_gate.php')],check=True,capture_output=True,text=True).stdout
 css=(SOURCE/'assets/source-ledger.css').read_text()
 js=(SOURCE/'assets/source-ledger.js').read_text()
 page_html=html.replace('</head>', '<style>html{background:#090a0a}body{margin:0}</style><style>'+css+'</style></head>')
 cases=[];screens={};lab=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in (320,390,768,1440,1920):
   for enabled in (False,True):
    context=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=enabled,reduced_motion='reduce',has_touch=width<=390,is_mobile=width<=390)
    tab=context.new_page();requests=[]
    tab.on('request',lambda r:requests.append(r.url))
    tab.set_content(page_html.replace('</body>',('<script>'+js+'</script>' if enabled else '')+'</body>'))
    roots=tab.locator('[data-fvx-ledger]');assert_true(roots.count()==3,'3 original desks')
    ids=tab.locator('[id]').evaluate_all('(els)=>els.map(el=>el.id)') 
    assert_true(len(ids)==27 and len(set(ids))==27,'IDREF uniqueness')
    assert_true(tab.locator('a[href^="https://www.nasa.gov/"]').count()==39,'NASA 39 links')
    assert_true(tab.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count()==3,'original CTA unchanged')
    assert_true(tab.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'no overflow')
    assert_true(len(requests)==0,'unexpected network')
    ax=tab.context.new_cdp_session(tab).send('Accessibility.getFullAXTree')
    nodes=[n for n in ax['nodes'] if not n.get('ignored') and n.get('role',{}).get('value') in ('link','searchbox','button')]
    unnamed=[n.get('nodeId') for n in nodes if not n.get('name',{}).get('value','').strip()]
    assert_true(not unnamed,'unnamed AX interactive nodes: '+str(unnamed))
    if enabled:
     searches=tab.locator('input[data-fvx-search]');assert_true(searches.count()==3,'JS search count')
     searches.nth(2).fill('S67-21294');assert_true(roots.nth(2).locator('article:visible').count()==1,'filtered record')
     assert_true(roots.nth(1).locator('article:visible').count()==6,'search isolation')
     searches.nth(2).fill('')
    else:
     assert_true(roots.nth(0).locator('[data-fvx-tools]').is_hidden(),'no-JS tools hidden')
     summary=roots.nth(0).locator('summary').first;summary.focus();tab.keyboard.press('Enter')
     assert_true(roots.nth(0).locator('details').first.get_attribute('open') is not None,'native keyboard')
    if width in (390,1440):
     file=f'{width}-'+('js' if enabled else 'nojs')+'.png'
     tab.screenshot(path=str(out/file),animations='disabled')
     screens[file]=hashlib.sha256((out/file).read_bytes()).hexdigest()
    cases.append({'width':width,'js':enabled,'status':'PASS','AX_controls':len(nodes)})
    context.close()
  browser.close()
 receipt={'gate':gate.stdout.strip(),'sources':SHAS,'cases':cases,'screenshots':screens,
          'limits':['offline Playwright set_content','simulated WordPress API only','not axe-core','no installed WP or HTTP/CSP','no real browser zoom','no field LCP/CLS','no rights or merchant clearance']}
 file=out/'receipt.json';file.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print('R272',len(cases),'Chromium PASS; 20/20 PHP; receipt SHA256',hashlib.sha256(file.read_bytes()).hexdigest())
if __name__=='__main__':main(pathlib.Path(sys.argv[1]))
