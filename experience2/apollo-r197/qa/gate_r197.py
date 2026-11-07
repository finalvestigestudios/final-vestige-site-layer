#!/usr/bin/env python3
"""Deterministic R197 PHP-output + real Chromium interaction custody gate.
Not a substitute for installed WordPress, axe-core or assistive technology.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r197 import build, sha
TARGETS={
  'Oxygen atmosphere':'fv-apollo-finding-oxygen',
  'Ignition uncertainty':'fv-apollo-finding-fire',
  'Hatch and escape':'fv-apollo-finding-hatch',
  'Cabin pressure':'fv-apollo-finding-chronology',
}
CASES=[(str(w),w,False,False,False,False) for w in (320,360,390,768,1440,1920)] + [
 ('390-nojs',390,True,False,False,False),('390-reduced',390,False,True,False,False),
 ('390-forced',390,False,False,True,False),('390-touch',390,False,False,False,True),
 ('320-zoom200',320,False,False,False,False),('390-zoom200',390,False,False,False,False)]

def render(dist,mode):
    return json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r197.php'),str(dist/'fv-ex2-apollo-r197.php'),mode],text=True))

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    for name,digest in manifest['files'].items(): assert sha((dist/name).read_bytes())==digest
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r197.php')],check=True,capture_output=True)
    raw=render(dist,'normal');assert not raw['fallback'] and raw['details']==8 and raw['chronology']==4
    assert not render(dist,'printed')['fallback'] and render(dist,'late')['fallback']
    html=raw['html']; css=(dist/'assets/atlas-scoped.css').read_text()
    assert html.count('class="cta"')==1 and html.count('class="fv-apollo-claim-nav"')==1
    assert 'did not conclusively identify' in html.lower()
    for target in TARGETS.values(): assert html.count('id="'+target+'"')==1
    receipt={'release':'r197','source':'actual PHP shortcode via WordPress-function harness',
      'parent_head':manifest['parent_head'],'source_sha256':manifest['files'],
      'status':'LOCAL_BROWSER_ONLY; NOT_INSTALLED_WORDPRESS',
      'cases':[],'limits':['page.set_content only; navigation to real domain blocked',
        'no genuine axe-core or NVDA/VoiceOver run','offline lab LCP/CLS is not field CWV',
        'no verified sellable Apollo SKU, leads, paid orders or net revenue']}
    with sync_playwright() as pw:
      b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
      for name,width,nojs,reduced,forced,touch in CASES:
        ctx=b.new_context(viewport={'width':width,'height':880},device_scale_factor=1,
          java_script_enabled=not nojs,has_touch=touch,is_mobile=touch,
          reduced_motion='reduce' if reduced else 'no-preference',
          forced_colors='active' if forced else 'none')
        page=ctx.new_page();page_errors=[];page.on('pageerror',lambda e:page_errors.append(str(e)))
        page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
        if 'zoom200' in name:page.evaluate("document.querySelector('.fv-apollo-atlas').style.zoom='2'")
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),name+' overflow'
        nav=page.get_by_role('navigation',name='Check the four findings');assert nav.count()==1
        assert nav.get_by_role('link').count()==4
        ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        visible=[(n.get('role',{}).get('value'),n.get('name',{}).get('value')) for n in ax if not n.get('ignored')]
        for label,target in TARGETS.items():
          assert ('link',label) in visible,(name,label,'missing in AX tree')
          link=nav.get_by_role('link',name=label)
          assert link.get_attribute('href')=='#'+target
          if touch:link.tap()
          else:link.focus();page.keyboard.press('Enter')
          assert page.evaluate('location.hash')=='#'+target,(name,label,'hash')
          assert page.evaluate('document.activeElement.id')==target,(name,label,'focus')
          assert page.locator('#'+target).evaluate('e=>e.matches(":target")'),(name,label,'target highlight')
        assert page.get_by_role('link',name='Read original investigation →').count()==1
        details=page.locator('.fv-apollo-atlas details').first
        details.locator('summary').focus();page.keyboard.press('Enter')
        assert details.get_attribute('open') is not None
        details.locator('summary').click();assert details.get_attribute('open') is None
        # Reset all interaction state before reproducible screenshot.
        page.evaluate("""() => {location.hash='';
          document.querySelectorAll('details[open]').forEach(d=>d.removeAttribute('open'));
          document.activeElement?.blur(); scrollTo(0,0)}""")
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(100)
        performance=page.evaluate("""async () => {
          const lcp=performance.getEntriesByType('largest-contentful-paint').at(-1)?.startTime??null;
          let cls=0;try {new PerformanceObserver(list => {for(const e of list.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){};
          await new Promise(r=>setTimeout(r,30));return {lcp_ms:lcp,cls}; }""") if not nojs else {'lcp_ms':None,'cls':None}
        assert not page_errors,page_errors
        path=out/(name+'.png');page.screenshot(path=str(path),full_page=True,animations='disabled')
        receipt['cases'].append({'context':name,'width':width,'nojs':nojs,'touch':touch,
          'native_navigation_targets':len(TARGETS),'keyboard_focus':True,'source_disclosures':8,
          'no_horizontal_overflow':True,'performance_fixture':performance,
          'screenshot_sha256':sha(path.read_bytes())})
        ctx.close()
      b.close()
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(CASES),'claim_journeys':len(CASES)*len(TARGETS),
      'receipt_sha256':sha((out/'receipt.json').read_bytes())}))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r197-evidence'))
