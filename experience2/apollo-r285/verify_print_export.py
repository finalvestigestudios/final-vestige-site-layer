#!/usr/bin/env python3
"""Offline Chromium PDF receipt: links + legibility (not WP, axe or field CWV)."""
import hashlib,json,subprocess,sys
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]/'apollo-r281'
out=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/fv-r285-pdf')
out.mkdir(parents=True,exist_ok=True)
php='''define('ABSPATH','/offline/');function add_action($a,$b,$c=10){}function add_shortcode($a,$b){}function plugins_url($p,$f){return '/offline/'.$p;}function wp_style_is($h,$s){return true;}require 'apollo-source-experience.php';echo fv_r281_render();'''
render=subprocess.run(['php','-r',php],cwd=root,text=True,capture_output=True,check=True)
css=(root/'assets/apollo-source-experience.css').read_text()
html='<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+render.stdout+'</body></html>'
sources=['https://www.nasa.gov/mission/apollo-1/',
'https://www.nasa.gov/history/Apollo204/proceed.html',
'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/']
receipt={'test':'R285 chromium printed evidence PDF with closed native details','pdfs':{},'source_links':sources}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in [390,1440]:
  ctx=browser.new_context(java_script_enabled=False,viewport={'width':width,'height':900},reduced_motion='reduce')
  page=ctx.new_page(); requests=[];page.on('request',lambda req:requests.append(req.url));page.set_content(html)
  assert page.locator('details[open]').count()==0,'must test closed drawer'
  assert not requests,'unexpected network request'
  page.emulate_media(media='print')
  raw=fitz.open(stream=page.pdf(print_background=True),filetype='pdf')
  meta=raw.metadata;meta.update({'creationDate':'','modDate':'','creator':'FV offline QA','producer':'FV offline QA'});raw.set_metadata(meta)
  path=out/f'apollo-{width}-print.pdf';raw.save(path,garbage=4,deflate=True,no_new_id=True);raw.close()
  pdf=fitz.open(path);txt='\n'.join(p.get_text() for p in pdf)
  links=[a.get('uri','') for p in pdf for a in p.get_links()]
  for src in sources: assert src in txt and src in links,(width,src)
  assert 'Editorial review: Pending' in txt and 'Source relationship:' in txt
  receipt['pdfs'][str(width)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(pdf),'source_urls':4}
  pdf.close();ctx.close()
 browser.close()
(out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print('Chrome print PDF: 2/2 PASS, 8/8 source links PASS, receipt SHA256',hashlib.sha256((out/'receipt.json').read_bytes()).hexdigest())
