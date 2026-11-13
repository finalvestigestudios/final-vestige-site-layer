#!/usr/bin/env python3
"""R337 Playwright Chromium LCP/CLS observer, OFFLINE PHP/CSS fixture only.
Measurements are NOT field CWV, installed WordPress, HTTP navigation, or 75th percentiles.
"""
from __future__ import annotations
import hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
STUB=ROOT/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=ROOT/'apollo-r337/QA/r337-offline-performance.json'
PINS={PHP:'fd9e384d26d3aee8e17bef17105fad9672136b0f',
      CSS:'2bf6b75cf59db310158212d0ed9b1b6e3f1a3b04',
      STUB:'f8987327fd6b49afcf8996c695100e3e7471c831'}

def blob(p):
    b=p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def fixture():
    html=subprocess.check_output(['php',str(STUB),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
    html=re.sub(r'<link rel="stylesheet" href="/assets/apollo-source-experience.css[^\"]*">','',html)
    return html.replace('</head>','<style>'+CSS.read_text()+'</style></head>')

def main():
    assert all(blob(p)==digest for p,digest in PINS.items()),'review source drift before measuring'
    rows=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in [320,360,390,768,1024,1440,1920]:
            page=browser.new_page(viewport={'width':width,'height':900})
            requests=[]
            page.on('request',lambda req:requests.append(req.url))
            page.goto('about:blank')
            page.evaluate('''() => {
              window.__fvPerf={lcp:[],shifts:[]};
              new PerformanceObserver(list=>list.getEntries().forEach(e=>window.__fvPerf.lcp.push(e.startTime)))
                .observe({type:'largest-contentful-paint',buffered:true});
              new PerformanceObserver(list=>list.getEntries().forEach(e=>{
                if(!e.hadRecentInput)window.__fvPerf.shifts.push(e.value);
              })).observe({type:'layout-shift',buffered:true});
            }''')
            page.set_content(fixture(),wait_until='domcontentloaded')
            page.wait_for_timeout(160)
            vals=page.evaluate('''() => ({lcp:window.__fvPerf.lcp,shifts:window.__fvPerf.shifts,
               width:document.documentElement.scrollWidth,viewport:innerWidth})''')
            assert vals['lcp'],('no LCP observer events',width)
            assert vals['width']<=vals['viewport']+1,('horizontal overflow',width)
            assert not requests,('unexpected resource fetches',requests)
            rows.append({'viewport':width,'lcpMs':round(vals['lcp'][-1],1),
               'observedClsSum':round(sum(vals['shifts']),5),
               'eventCount':len(vals['shifts']),'qualifiedAsFieldCWV':False})
            page.close()
        browser.close()
    result={'classification':'OFFLINE CHROMIUM FIXTURE ONLY / NOT LIVE FIELD CWV',
      'engine':'system Chromium Playwright PerformanceObserver buffered LCP and layout-shift',
      'sourceBlobs':{str(p.relative_to(ROOT)):h for p,h in PINS.items()},'rows':rows,
      'limits':'Neither installed WordPress nor real HTTP/CSP, CDN, real-device network, INP, axe-core or 75th-percentile field data verified'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('R337 PASS: 7 genuine offline Chromium LCP/CLS observations; not production metrics')

if __name__=='__main__': main()
