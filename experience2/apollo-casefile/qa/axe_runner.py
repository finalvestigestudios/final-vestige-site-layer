#!/usr/bin/env python3
"""Real axe-core WCAG 2.2 AA in Chromium, only if a reviewed axe.min.js is available.

Use: AXE_JS_PATH=/path/to/pinned/axe.min.js python qa/axe_runner.py
An unavailable vendor JS asset fails explicitly; no fake axe result is emitted.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
path=os.environ.get('AXE_JS_PATH')
if not path or not Path(path).is_file():
    raise SystemExit('AXE_NOT_RUN: set AXE_JS_PATH to a verified local axe-core bundle')
script=Path(path).read_text(encoding='utf8')
html=(ROOT/'index.html').read_text(encoding='utf8')
reports=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in (390,1440):
        page=browser.new_page(viewport={'width':width,'height':900})
        page.set_content(html,wait_until='load')
        page.add_script_tag(content=script)
        data=page.evaluate("""async () => { const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),passes:r.passes.length,incomplete:r.incomplete.map(v=>v.id)}}""")
        data['width']=width
        reports.append(data)
        page.close()
    browser.close()
report={'tool':'axe-core actually executed locally','viewports':reports,'violations':sum(len(x['violations']) for x in reports)}
(ROOT/'qa'/'AXE_ACTUAL_RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
if report['violations']:
    raise SystemExit('AXE_FAIL: '+json.dumps(report['viewports']))
print('AXE_PASS',json.dumps(report))
