#!/usr/bin/env python3
"""Actual-PHP offline Chromium screenshots, print and evidence receipt. No HTTP/axe/CWV."""
import hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'QA';OUT.mkdir(parents=True,exist_ok=True)
css=(BASE/'apollo-r281/assets/apollo-source-experience.css').read_text()
html=subprocess.check_output(['php',str(BASE/'apollo-r294/qa/local_http_fixture.php')],text=True)
html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',html)
html=html.replace('</head>','<style>'+css+'</style></head>')
heights={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in (390,1440):
  page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=False,reduced_motion='reduce')
  page.set_content(html)
  assert page.locator('.fv-r296__date-disclosure').get_attribute('open') is None
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
  heights[str(width)]=round(page.locator('.fv-r281').bounding_box()['height'],2)
  page.screenshot(path=str(OUT/f'r296-{width}-compact-nojs.png'),full_page=True,animations='disabled')
  if width==390:
   page.emulate_media(media='print')
   page.pdf(path=str(OUT/'r296-390-print.pdf'),print_background=True)
  page.close()
 browser.close()
pdf=fitz.open(OUT/'r296-390-print.pdf')
body='\n'.join(pg.get_text() for pg in pdf)
for excerpt in ('Apollo 204 Review Board narrative','Later NASA Safety and Mission Assurance summary','NASA archive: memorandum for the Apollo 204 Review Board'):
 assert excerpt in body, f'printed source missing: {excerpt}'
links=[i['uri'] for pg in pdf for i in pg.get_links() if 'uri' in i]
for url in ('https://www.nasa.gov/history/Apollo204/narr.html','https://www.nasa.gov/history/Apollo204/15.html','https://sma.nasa.gov/sma-disciplines/accllp/apollo-1'):
 assert url in links, f'printed source link missing: {url}'
files=sorted([OUT/'r296-390-compact-nojs.png',OUT/'r296-1440-compact-nojs.png',OUT/'r296-390-print.pdf'])
receipt={'status':'LOCAL_OFFLINE_PASS','source':'actual staging PHP fixture with reviewed CSS',
 'component_heights_px':heights,'print_pages':len(pdf),'print_links':len(links),
 'artifacts_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
 'not_tested':['genuine axe-core','browser HTTP/CSP','installed WordPress/Assembler','production or field LCP/CLS','screen-reader acceptance','conversion metrics']}
(OUT/'r296-artifact-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('PASS 2 offline screenshots; 3 printed NASA sources + hyperlinks; '+str(len(pdf))+' PDF pages; HARD HOLD')
