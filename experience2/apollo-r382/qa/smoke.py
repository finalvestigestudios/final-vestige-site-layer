#!/usr/bin/env python3
"""Real Chromium against a R377-custody-derived DOM contract; NOT installed WordPress."""
import hashlib, html, json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[3]
JS=BASE/'experience2/apollo-r381/assets/atlas.js'
SRC=BASE/'experience2/apollo-r377/custody.json'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f'
records=json.loads(SRC.read_text())['records']
assert len(records)==6
phases=[('ground',range(4)),('board',range(4,5)),('response',range(5,6))]
facets=['test','hazard','record','record','uncertainty','response']
e=lambda v:html.escape(str(v),quote=True)
parts=['<!doctype html><html lang="en"><head><meta charset="utf-8"><style>',
 'body{font:16px/1.5 system-ui;background:#161c20;color:white}.fv-a381{max-width:1100px;margin:auto;padding:1rem}',
 '.fv-a381__rail ol,.fv-a381__plates{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}',
 '.fv-a381__rail li[hidden],.fv-a381__phase[hidden],.fv-a381__plate[hidden],.fv-a381__enhance[hidden]{display:none}',
 'a{color:#ffe1a0}@media(max-width:700px){.fv-a381__rail ol,.fv-a381__plates{grid-template-columns:1fr}}',
 '</style></head><body><section class="fv-a381" data-fv-atlas><h1>Apollo 1: sourced evidence</h1>',
 '<nav class="fv-a381__rail"><ol>']
for key,_ in phases: parts.append(f'<li><a href="#phase-{key}">{key}</a></li>')
parts.append('</ol></nav><div class="fv-a381__enhance" data-fv-atlas-controls hidden><label for="facet">Source role</label><select id="facet" data-fv-atlas-filter>')
for v in ['all','test','hazard','record','uncertainty','response']: parts.append(f'<option value="{v}">{v}</option>')
parts.append('</select><button data-fv-atlas-reset type="button">Show all</button><p role="status" aria-live="polite" data-fv-atlas-status></p></div>')
for key,indices in phases:
 parts.append(f'<section id="phase-{key}" data-fv-atlas-phase><h2>{key}</h2><ol class="fv-a381__plates">')
 for i in indices:
  r=records[i]
  parts.append(f'<li data-fv-atlas-plate data-fv-atlas-facet="{facets[i]}"><h3>{e(r["heading"])}</h3>')
  parts.append(f'<p>{e(r["claim"])}</p><details><summary>Source</summary><a href="{e(r["evidence_url"])}">NASA</a></details></li>')
 parts.append('</ol></section>')
parts.append('</section></body></html>')
markup=''.join(parts)
checks=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in (320,390,768,1440,1920):
  ctx=browser.new_context(viewport={'width':width,'height':900})
  page=ctx.new_page();page.set_content(markup);page.add_script_tag(content=JS.read_text())
  assert page.locator('.fv-a381__rail a:visible').count()==3;checks+=1
  page.locator('[data-fv-atlas-filter]').select_option('response')
  assert page.locator('.fv-a381__rail a:visible').count()==1;checks+=1
  assert page.locator('.fv-a381__rail a:visible').get_attribute('href')=='#phase-response';checks+=1
  assert page.locator('[data-fv-atlas-phase]:visible').count()==1;checks+=1
  page.locator('[data-fv-atlas-reset]').click()
  assert page.locator('.fv-a381__rail a:visible').count()==3;checks+=1
  assert page.locator('[data-fv-atlas-plate]:visible').count()==6;checks+=1
  ctx.close()
 browser.close()
print(json.dumps({'status':'LOCAL_CHROMIUM_CONTRACT_PASS_NOT_STAGING','contexts':5,'checks':checks},indent=2))
