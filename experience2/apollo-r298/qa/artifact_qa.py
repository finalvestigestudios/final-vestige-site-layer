#!/usr/bin/env python3
"""R298 source-controlled reproducible offline screenshots/PDF/fixture metrics."""
import hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
root=Path(__file__).resolve().parents[2]; out=root/'QA';out.mkdir(exist_ok=True)
html=subprocess.check_output(['php','-r','parse_str("instances=2", $_GET); include $argv[1];',str(root/'apollo-r294/qa/local_http_fixture.php')],text=True)
css=(root/'apollo-r281/assets/apollo-source-experience.css').read_text()
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',html).replace('</head>','<style>'+css+'</style></head>')
artifacts=[]; perf={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in [320,390,768,1440,1920]:
  page=browser.new_page(viewport={'width':w,'height':900},java_script_enabled=False,reduced_motion='reduce')
  page.set_content(html)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  path=out/f'r298-{w}-nojs.png';page.screenshot(path=str(path),full_page=True,animations='disabled');artifacts.append(path)
  if w==390:
   page.emulate_media(media='print');path=out/'r298-390-evidence-print.pdf'
   page.pdf(path=str(path),print_background=True);artifacts.append(path)
  page.close()
  page=browser.new_page(viewport={'width':w,'height':900})
  page.evaluate('''() => {window.fv={lcp:[],cls:0};new PerformanceObserver(x=>x.getEntries().forEach(e=>fv.lcp.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(x=>x.getEntries().forEach(e=>{if(!e.hadRecentInput)fv.cls+=e.value})).observe({type:'layout-shift',buffered:true});}''')
  page.set_content(html);page.wait_for_timeout(180)
  perf[str(w)]=page.evaluate('({offline_fixture_lcp_ms:fv.lcp.length?Math.round(Math.max(...fv.lcp)):null, offline_fixture_cls:fv.cls})')
  page.close()
 browser.close()
# Normalize Chromium's wall-clock Info timestamps for reproducible, rights-auditable PDF.
pdfpath=out/'r298-390-evidence-print.pdf'
with fitz.open(pdfpath) as printed:
 meta=printed.metadata
 meta['creationDate']="D:20261111000000+00'00'"
 meta['modDate']="D:20261111000000+00'00'"
 printed.set_metadata(meta)
 normalized=out/'.r298-normalized.pdf'
 printed.save(normalized,garbage=4,deflate=True,no_new_id=True)
normalized.replace(pdfpath)
pdf=fitz.open(pdfpath)
text='\n'.join(pg.get_text() for pg in pdf)
links=[x['uri'] for pg in pdf for x in pg.get_links() if 'uri' in x]
assert text.count('NASA archive: memorandum for the Apollo 204 Review Board')==2
assert links.count('https://www.nasa.gov/history/Apollo204/15.html')>=2
receipt={'scope':'OFFLINE FIXTURE ONLY — NOT AXE, WORDPRESS, OR FIELD CWV','pdf_pages':len(pdf),'pdf_nasa_memo_links':links.count('https://www.nasa.gov/history/Apollo204/15.html'),'pdf_clickable_links':len(links), 'fixture_performance':perf,'artifacts':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in artifacts}}
(out/'r298-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'PASS','screenshots':5,'pdf_pages':len(pdf),'links':len(links),'offline_only':True},sort_keys=True))
