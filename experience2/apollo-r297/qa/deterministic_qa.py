#!/usr/bin/env python3
"""R297 reproducible two-shortcode screenshots/PDF plus fixture metrics (NOT field CWV)."""
import hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
root=Path(__file__).resolve().parents[2]
out=root/'QA';out.mkdir(exist_ok=True)
html=subprocess.check_output(['php','-r','parse_str("instances=2", $_GET); include $argv[1];',str(root/'apollo-r294/qa/local_http_fixture.php')],text=True)
css=(root/'apollo-r281/assets/apollo-source-experience.css').read_text()
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',html).replace('</head>','<style>'+css+'</style></head>')
metrics={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (390,1440):
  page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=False,reduced_motion='reduce')
  page.set_content(html)
  assert page.locator('.fv-r281').count()==2
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
  names=page.locator('nav.fv-r281__rail').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("aria-label"))')
  assert names==['Apollo 1 chronology — atlas instance 1','Apollo 1 chronology — atlas instance 2']
  page.screenshot(path=str(out/f'r297-{width}-double-nojs.png'),full_page=True,animations='disabled')
  if width==390:
   page.emulate_media(media='print')
   page.pdf(path=str(out/'r297-390-double-print.pdf'),print_background=True)
  page.close()
  # Separate JS-enabled fixture view for genuine browser PerformanceObservers.
  perf=browser.new_page(viewport={'width':width,'height':900})
  perf.evaluate("""() => {window.fvPerf={lcp:[],cls:0};new PerformanceObserver(x=>x.getEntries().forEach(e=>fvPerf.lcp.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(x=>x.getEntries().forEach(e=>{if(!e.hadRecentInput)fvPerf.cls+=e.value})).observe({type:'layout-shift',buffered:true});}""")
  perf.set_content(html);perf.wait_for_timeout(180)
  metrics[str(width)]=perf.evaluate('({local_observed_lcp_ms:fvPerf.lcp.length?Math.round(Math.max(...fvPerf.lcp)):null,local_observed_cls:fvPerf.cls})')
  perf.close()
 browser.close()
pdf=fitz.open(out/'r297-390-double-print.pdf')
body='\n'.join(page.get_text() for page in pdf)
assert body.count('NASA archive: memorandum for the Apollo 204 Review Board')==2
links=[link['uri'] for page in pdf for link in page.get_links() if 'uri' in link]
assert links.count('https://www.nasa.gov/history/Apollo204/15.html')>=2
artifacts=[out/'r297-390-double-nojs.png',out/'r297-1440-double-nojs.png',out/'r297-390-double-print.pdf']
receipt={'status':'LOCAL_OFFLINE_ONLY','fixture_performance_not_field_cwv':metrics,
 'pdf_pages':len(pdf),'pdf_links':len(links),
 'artifact_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in artifacts},
 'not_tested':['genuine axe','installed WordPress','real browser HTTP/CSP','field LCP/CLS/INP','commercial conversion']}
(out/'r297-deterministic-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('PASS deterministic staging screenshot/PDF source custody; field release remains HOLD')
