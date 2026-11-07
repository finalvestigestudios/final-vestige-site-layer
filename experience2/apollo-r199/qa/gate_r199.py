#!/usr/bin/env python3
"""R199 actual PHP-output / Chromium source-custody acceptance, NOT live WordPress or axe-core."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r199 import build, sha, BOARD, CLAIMS
CASES=[('320',320,False,False,False,False),('360',360,False,False,False,False),
('390',390,False,False,False,False),('768',768,False,False,False,False),
('1440',1440,False,False,False,False),('1920',1920,False,False,False,False),
('390-nojs',390,True,False,False,False),('390-reduced',390,False,True,False,False),
('390-forced',390,False,False,True,False),('390-touch',390,False,False,False,True),
('320-zoom200',320,False,False,False,False),('390-zoom200',390,False,False,False,False)]

def render(dist, mode):
    return json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r199.php'),
         str(dist/'fv-ex2-apollo-r199.php'),mode],text=True))

def custody(html):
    doc=BeautifulSoup(html,'html.parser')
    assert len(doc.select('.fv-apollo-trace-grid > li'))==4
    assert len(doc.select('.fv-apollo-atlas .cta'))==1
    assert len(doc.select('.fv-apollo-atlas details'))==8
    assert len(doc.select('.fv-apollo-atlas .rail > li'))==4
    assert len(doc.select('.fv-apollo-trace [data-authority="nasa-apollo-204-board"]'))==4
    assert len(doc.select('[data-geo],[data-lat],[data-long],[data-purchase],iframe,form'))==0
    assert len(doc.select('script'))==0
    seen=set()
    for slug,subject in CLAIMS:
        row=doc.select_one('[data-finding="fv-apollo-finding-'+slug+'"]')
        assert row is not None
        link=row.find('a',string='Read NASA Review Board report about '+subject)
        assert link and link.get('href')==BOARD
        assert link.get('data-authority')=='nasa-apollo-204-board'
        boundary='fv-apollo-source-limit-'+slug
        assert link.get('aria-describedby')==boundary
        limits=doc.find_all(id=boundary)
        assert len(limits)==1 and limits[0].parent==row
        assert 'Boundary:' in limits[0].get_text(' ',strip=True)
        assert 'not' in limits[0].get_text(' ',strip=True).lower() or 'cannot' in limits[0].get_text(' ',strip=True).lower() or 'did not' in limits[0].get_text(' ',strip=True).lower()
        assert link.get_text(' ',strip=True) not in seen
        seen.add(link.get_text(' ',strip=True))
    assert 'complete NASA Review Board report' in doc.get_text(' ',strip=True)
    assert 'not commercial-use clearance' in doc.get_text(' ',strip=True)
    assert 'did not conclusively identify' in doc.get_text(' ',strip=True).lower()
    return True

def mutants(html):
    cases={
      'source-substitution': html.replace('href="'+BOARD+'" aria-describedby="fv-apollo-source-limit-oxygen"','href="https://example.invalid/fake-report" aria-describedby="fv-apollo-source-limit-oxygen"',1),
      'source-label-duplication': html.replace('Read NASA Review Board report about ignition uncertainty','Read NASA Review Board report about oxygen atmosphere',1),
      'limit-pointer-break': html.replace('aria-describedby="fv-apollo-source-limit-fire"','aria-describedby="missing-limit"',1),
      'limit-removal': html.replace('id="fv-apollo-source-limit-hatch"','id="missing-limit"',1),
      'false-rights': html.replace('not commercial-use clearance','certified for advertising',1),
      'spark-overclaim': html.replace('did not conclusively identify','did conclusively identify',1),
      'invented-geo': html.replace('class="fv-apollo-trace"','class="fv-apollo-trace" data-geo="moon"',1),
      'extra-commerce': html.replace('class="cta"','class="cta" data-purchase="unverified"',1),
    }
    rejected=[]
    for name,variant in cases.items():
        try:
            custody(variant)
        except AssertionError:
            rejected.append(name)
    assert len(rejected)==len(cases),(rejected,len(cases))
    return rejected

def execute(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    for name,digest in manifest['files'].items():assert sha((dist/name).read_bytes())==digest
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r199.php')],capture_output=True,check=True)
    raw=render(dist,'normal'); assert not raw['fallback'] and raw['details']==8 and raw['chronology']==4
    assert not render(dist,'printed')['fallback']
    assert render(dist,'late')['fallback']
    html=raw['html'];css=(dist/'assets/atlas-scoped.css').read_text('utf-8')
    custody(html);rejected=mutants(html)
    receipt={'release':'r199','kind':'PHP_short_code_in_WP_function_shim_plus_offline_real_Chromium',
      'parent':'R198 source archive; actual parent GitHub builder byte identity not verified',
      'source_sha256':manifest['files'],'mutation_rejections':rejected,
      'limits':['Browser navigation to localhost/data/file blocked by administrator',
       'No genuine axe-core, installed WordPress, NVDA/VoiceOver, CDN/CSP or exact-head hosted CI',
       'Fixture laboratory LCP/CLS not production Web Vitals',
       'No sellable Apollo product, verified paid order, lead, affiliate sale, fees or qualified human session denominator'],
      'cases':[]}
    with sync_playwright() as pw:
      browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
      for label,width,nojs,reduced,forced,touch in CASES:
        ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,
         java_script_enabled=not nojs,has_touch=touch,is_mobile=touch,
         reduced_motion='reduce' if reduced else 'no-preference',
         forced_colors='active' if forced else 'none')
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
        if 'zoom200' in label: page.evaluate("document.querySelector('.fv-apollo-atlas').style.zoom='2'")
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),label+' horizontal overflow'
        ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        axlinks=[n.get('name',{}).get('value','') for n in ax if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
        for slug,subject in CLAIMS:
          name='Read NASA Review Board report about '+subject
          assert axlinks.count(name)==1,(label,name,axlinks.count(name))
          row=page.locator('[data-finding="fv-apollo-finding-'+slug+'"]')
          source=row.get_by_role('link',name=name,exact=True)
          assert source.count()==1 and source.get_attribute('href')==BOARD
          described=source.get_attribute('aria-describedby')
          assert described=='fv-apollo-source-limit-'+slug
          assert row.locator('#'+described).count()==1
          source.focus()
          assert page.evaluate('document.activeElement.getAttribute("aria-describedby")')==described
          assert row.evaluate('e=>e.matches(":focus-within")'),(label,slug,'focus-visible row')
          assert row.locator('#'+described).is_visible()
        if touch:
          page.get_by_role('navigation',name='Check the four findings').get_by_role('link',name='Oxygen atmosphere').tap()
          assert page.evaluate('document.activeElement.id')=='fv-apollo-finding-oxygen'
        # One original free investigation CTA, no purchasable offer or pseudo-conversion.
        assert page.get_by_role('link',name='Read original investigation →').count()==1
        assert page.locator('.fv-apollo-atlas script,.fv-apollo-atlas form,.fv-apollo-atlas iframe').count()==0
        assert page.locator('.fv-apollo-atlas details').count()==8
        page.evaluate("""() => {location.hash='';document.querySelectorAll('details[open]').forEach(d=>d.removeAttribute('open'));document.activeElement?.blur();window.scrollTo(0,0)}""")
        page.evaluate('document.fonts.ready');page.wait_for_timeout(90)
        perf=page.evaluate("""async()=>{const x={lcp_ms:null,cls:0};try{new PerformanceObserver(ls=>{for(const e of ls.getEntries())x.lcp_ms=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(ls=>{for(const e of ls.getEntries())if(!e.hadRecentInput)x.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){};await new Promise(r=>setTimeout(r,70));return x;}""") if not nojs else {'lcp_ms':None,'cls':None}
        assert not errors,errors
        screenshot=out/(label+'.png');page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
        receipt['cases'].append({'context':label,'width':width,'no_js':nojs,'touch':touch,
         'unique_AX_links':4,'boundary_focus_pairs':4,'no_overflow':True,
         'offline_performance':perf,'png_sha256':sha(screenshot.read_bytes())})
        ctx.close()
      browser.close()
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(CASES),'focus_pairs':len(CASES)*len(CLAIMS),
      'mutations_rejected':len(rejected),'receipt_sha256':sha((out/'receipt.json').read_bytes())}))
if __name__=='__main__':execute(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r199-evidence'))
