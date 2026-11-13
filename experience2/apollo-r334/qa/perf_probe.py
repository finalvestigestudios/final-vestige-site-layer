#!/usr/bin/env python3
"""R334 Chromium offline fixture LCP/CLS observer; no production inference.

Run: python experience2/apollo-r334/qa/perf_probe.py
This is a test-only script: no site analytics/tracking code shipped.
Separates initial first-paint CLS from a *synthetic* details opening performed
without a user input. The latter should NOT be reported as normal page-load CLS.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from commit_gate import fixture, OUT, CSS

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
SCRIPT = '''<script>
window.__fvVitals={lcpMs:null,cls:0,layoutShifts:0};
try {new PerformanceObserver(list=>{for(const e of list.getEntries()) window.__fvVitals.lcpMs=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
try {new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput){window.__fvVitals.cls+=e.value;window.__fvVitals.layoutShifts++;}}}).observe({type:'layout-shift',buffered:true});}catch(e){}
</script>'''

def main():
    OUT.mkdir(exist_ok=True)
    cases=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                for fontsize in ((16,64) if width==320 else (16,)):
                    page=browser.new_page(viewport={'width':width,'height':900},reduced_motion='reduce')
                    try:
                        html=fixture().replace('</head>',f'<style>html{{font-size:{fontsize}px}}</style>'+SCRIPT+'</head>')
                        page.set_content(html, wait_until='load')
                        page.wait_for_timeout(100)
                        initial=page.evaluate('window.__fvVitals')
                        assert isinstance(initial['lcpMs'],(int,float)) and initial['lcpMs']>=0
                        assert initial['cls']==0, ('unexpected initial load shift',width,initial)
                        # This is deliberately NOT a user interaction. It should
                        # be reported independently, not called page-load CLS.
                        page.locator('details').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=true)')
                        page.wait_for_timeout(100)
                        after=page.evaluate('window.__fvVitals')
                        assert after['cls']>=initial['cls']>=0
                        cases.append({'viewportPx':width,'rootFontPx':fontsize,'initialLcpMs':initial['lcpMs'],
                            'initialCls':initial['cls'],'clsAfterSyntheticDisclosureExpansion':after['cls'],
                            'lcpAfterSyntheticDisclosureExpansionMs':after['lcpMs'],
                            'lcpMeasurement':'PerformanceObserver largest-contentful-paint on offline Chromium fixture',
                            'clsMeasurement':'PerformanceObserver layout-shift, excludes hadRecentInput'})
                    finally:page.close()
        finally:browser.close()
    payload={'sprint':'R334','cases':cases,'caseCount':len(cases),
      'scope':'OFFLINE PHP WordPress stub, not installed site or production field data',
      'doNotCompareToCrUX':True,
      'syntheticDisclosureWarning':'Synthetic details.open changes after first paint can produce artificial layout shift; do not report these as normal initial-load CLS.',
      'productionLcpP75':None,'productionClsP75':None,'axeCore':'NOT EXECUTED'}
    (OUT/'r334-fixture-vitals.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print('PASS fixture PerformanceObserver cases',len(cases),'LCP-ms', [x['initialLcpMs'] for x in cases],
          'initial CLS',[x['initialCls'] for x in cases],
          'synthetic-reveal CLS',[round(x['clsAfterSyntheticDisclosureExpansion'],5) for x in cases])

if __name__=='__main__': main()
