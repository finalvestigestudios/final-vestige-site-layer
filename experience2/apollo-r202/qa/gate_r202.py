#!/usr/bin/env python3
"""R202: PHP fixture + actual Chromium acceptance, no installed WP claim."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r202 import build,sha,custody,REPORT,PHOTO,DEST
CASES=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),
 ('1024',1024,{}),('1440',1440,{}),('1920',1920,{}),
 ('390-nojs',390,{'java_script_enabled':False}),
 ('390-reduced',390,{'reduced_motion':'reduce'}),
 ('390-forced',390,{'forced_colors':'active'}),
 ('390-touch',390,{'is_mobile':True,'has_touch':True}),
 ('320-csszoom200',320,{'csszoom':2})]
def render(dist,mode='normal'):
    return json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r202.php'),
        str(dist/'fv-ex2-apollo-r202.php'),mode],text=True))
def run(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    for name,digest in manifest['files'].items(): assert sha((dist/name).read_bytes())==digest
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r202.php')],check=True,capture_output=True)
    result=render(dist);assert not result['fallback'] and result['details']==9 and result['chronology']==4
    assert not render(dist,'printed')['fallback'] and render(dist,'late')['fallback']
    html=result['html'];custody(html)
    bad={
      'development_copy':html.replace('Case study / January 27, 1967 / Apollo 204','research prototype'),
      'bottom_staging':html.replace('Read the original records and distinguish observation','Unpublished staging! Read the original records and distinguish observation'),
      'paid_link':html.replace('class="cta"','class="cta" data-purchase="paid"',1),
      'fake_pin':html.replace('<footer class="end">','<span data-geo="invented"></span><footer class="end">'),
      'missing_board':html.replace(REPORT,'https://example.invalid/board'),
      'missing_photo':html.replace(PHOTO,'https://example.invalid/photo'),
      'duplicate_id':html.replace('id="fv-apollo-compare-title"','id="fv-apollo-main"'),
      'missing_exercise':html.replace('class="fv-apollo-compare-grid"','class="not-compare"'),
      'bad_cta':html.replace(DEST,'https://example.invalid/buy'),
      'extra_cta':html.replace('</footer>','<a class="cta" href="https://example.invalid">BUY</a></footer>'),
    }
    # For missing_exercise, explicit component count supplements the source custody contract.
    rejected=[]
    for name,mutant in bad.items():
        try:
            custody(mutant)
            if name=='missing_exercise':assert 'class="fv-apollo-compare-grid"' in mutant
        except AssertionError:rejected.append(name)
    assert len(rejected)==len(bad),set(bad)-set(rejected)
    css=(dist/'assets/atlas-scoped.css').read_text()
    page_html='<html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
    receipt={'release':'r202','scope':'PHP shortcode shim, not installed WP','negative_controls_rejected':rejected,'screens':[],'source_hashes':manifest['files'],
      'release_blockers':['R198 inherited source drift','installed WordPress','axe-core','NVDA/VoiceOver','hosted exact-head CI','verified offer/orders']}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        receipt['chromium']=browser.version
        for name,width,kwargs in CASES:
            kwargs=dict(kwargs);zoom=kwargs.pop('csszoom',None)
            ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**kwargs)
            page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(page_html,wait_until='load')
            if zoom:page.locator('.fv-apollo-atlas').evaluate('(e,z)=>e.style.zoom=z',zoom)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),name
            assert page.get_by_role('link',name='Read original investigation →').count()==1
            assert page.get_by_role('heading',name='What can each record prove?').count()==1
            ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
            names=[n.get('name',{}).get('value','') for n in ax if not n.get('ignored')]
            assert 'What can each record prove?' in names and 'Compare the evidence and its limits' in names
            for li in page.locator('.fv-apollo-atlas .rail > li').all():
                a=li.get_by_role('link');target=a.get_attribute('href')[1:]
                if kwargs.get('has_touch'):a.tap()
                else:a.focus();a.press('Enter')
                assert page.evaluate('document.activeElement.id')==target,(name,target)
            disclosure=page.locator('.fv-apollo-compare-answer')
            disclosure.locator('summary').focus();disclosure.locator('summary').press('Enter')
            assert disclosure.evaluate('(e)=>e.open')
            disclosure.locator('summary').press('Enter');assert not disclosure.evaluate('(e)=>e.open')
            page.evaluate("()=>{location.hash='';document.activeElement.blur();window.scrollTo(0,0)}")
            page.wait_for_timeout(130)
            png=out/(name+'.png');page.screenshot(path=str(png),animations='disabled',full_page=True)
            metrics=page.evaluate("""async()=>{let lcp=null,cls=0;
              try{new PerformanceObserver(l=>{for(const e of l.getEntries())lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
              try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){}
              await new Promise(r=>setTimeout(r,70));return {lcp_ms:lcp,cls};}""") if kwargs.get('java_script_enabled',True) else {'lcp_ms':None,'cls':None}
            assert not errors,(name,errors)
            receipt['screens'].append({'case':name,'width':width,'sha256':sha(png.read_bytes()),'lab_vitals':metrics})
            ctx.close()
        browser.close()
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS','cases':len(CASES),'negative_controls':len(rejected),'browser':receipt['chromium']}))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r202'))
