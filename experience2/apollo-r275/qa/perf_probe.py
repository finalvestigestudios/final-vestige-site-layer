#!/usr/bin/env python3
"""Offline lab-only Chromium LCP/CLS observations; never field Core Web Vitals."""
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
html = subprocess.check_output(['php', str(root/'apollo-r274/qa/multi-render.php')]).decode()
observations = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    for width in (320, 390, 768, 1440, 1920):
        page = browser.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=1)
        page.evaluate('''() => {
            window.__fvVitals = {lcp: [], shifts: []};
            new PerformanceObserver(list => window.__fvVitals.lcp.push(...list.getEntries().map(e => e.startTime))).observe({type:'largest-contentful-paint',buffered:true});
            new PerformanceObserver(list => window.__fvVitals.shifts.push(...list.getEntries().map(e => ({value:e.value,hadRecentInput:e.hadRecentInput})))).observe({type:'layout-shift',buffered:true});
        }''')
        page.set_content(html, wait_until='load')
        page.wait_for_timeout(350)
        vitals = page.evaluate('window.__fvVitals')
        lcp = round(vitals['lcp'][-1], 1) if vitals['lcp'] else None
        cls = round(sum(s['value'] for s in vitals['shifts'] if not s['hadRecentInput']), 5)
        observations.append({'width':width,'lcp_ms_lab':lcp,'cls_lab':cls,'instrumentation':'PerformanceObserver; offline set_content; no external assets'})
        page.close()
    browser.close()
report={'scope':'LAB_ONLY_NOT_FIELD','axe_core':'NOT_EXECUTED','installed_wordpress':'NOT_TESTED','real_http':'BLOCKED_BY_ADMINISTRATOR','measurements':observations}
if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report, indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2))
