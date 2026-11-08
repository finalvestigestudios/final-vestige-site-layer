#!/usr/bin/env python3
"""R204 isolated crosswalk-landmark integrity and real Chromium acceptance.

Fixtures run actual generated PHP shortcode, but are NOT installed WordPress QA.
Never implies genuine axe-core, NVDA/VoiceOver or live Core Web Vitals.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r204 import build,sha
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CASES=[('320',320,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),
       ('390-nojs',390,{'java_script_enabled':False}),('390-reduced',390,{'reduced_motion':'reduce'}),
       ('390-touch',390,{'has_touch':True,'is_mobile':True}),('390-forced',390,{'forced_colors':'active'}),
       ('320-csszoom200',320,{'zoom':2})]
def source_gate(html):
    dom=BeautifulSoup(html,'html.parser')
    atlas=dom.select_one('.fv-apollo-atlas');assert atlas
    trace=atlas.select_one('.fv-apollo-trace');assert trace
    method=atlas.select_one('.fv-apollo-method');assert method
    assert trace.parent==method.parent,'crosswalk incorrectly inside methodology aside'
    assert trace.find_previous_sibling()==method,'crosswalk not adjacent to its source explanation'
    assert trace.find_next_sibling().get('id')=='fv-apollo-chronology'
    assert len(trace.select('li[data-record-kind="review-board"]'))==4
    assert len(atlas.select('.rail > li'))==4 and len(atlas.select('details'))==8
    assert len(atlas.select('a.cta'))==1 and atlas.select_one('a.cta')['href']==DEST
    assert len(atlas.select('.fv-apollo-citation-route a'))==2
    assert len(atlas.select('.fv-apollo-reading-lab'))==1
    assert not atlas.select('form,[data-purchase],[data-affiliate],[data-lat],[data-geo]')
    ids=[a['id'] for a in atlas.select('[id]')]; assert len(ids)==len(set(ids))
    return {'rail':4,'disclosures':8,'technical_crosswalk':4,'commercial_ctas':0,'editorial_ctas':1}
def run(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    assert all(sha((dist/k).read_bytes())==v for k,v in manifest['files'].items())
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r204.php')],check=True,capture_output=True)
    payload=json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r204.php'),str(dist/'fv-ex2-apollo-r204.php'),'normal'],text=True))
    assert not payload['fallback']
    assert not json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r204.php'),str(dist/'fv-ex2-apollo-r204.php'),'printed'],text=True))['fallback']
    assert json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r204.php'),str(dist/'fv-ex2-apollo-r204.php'),'late'],text=True))['fallback']
    html=payload['html']; counts=source_gate(html)
    mutants={'trace_inside_aside':html.replace('<section class="fv-apollo-trace"','</aside><section class="fv-apollo-trace"',1),
             'missing_cta':html.replace('class="cta"','class="other"',1),
             'misleading_sale':html.replace('class="cta"','class="cta" data-purchase="true"',1),
             'missing_atlas_crosswalk':html.replace('class="fv-apollo-trace"','class="not-a-crosswalk"',1)}
    # check a valid but wrongly nested variant by moving the real crosswalk back inside the aside
    beginning=html.index('<section class="fv-apollo-trace"');ending=html.index('</section>',beginning)+len('</section>')
    fragment=html[beginning:ending]
    misplaced=html[:beginning]+html[ending:]
    misplaced=misplaced.replace('</aside>\n<section aria-labelledby="fv-apollo-chronology-title"',fragment+'\n</aside>\n<section aria-labelledby="fv-apollo-chronology-title"',1)
    mutants['regressed_parent_layout']=misplaced
    rejected=[]
    for name,variant in mutants.items():
        try:source_gate(variant)
        except (AssertionError,AttributeError):rejected.append(name)
    assert 'regressed_parent_layout' in rejected and len(rejected)>=4,rejected
    css=(dist/'assets/atlas-scoped.css').read_text('utf-8'); js=(dist/'assets/campaign-handoff.js').read_text('utf-8')
    document='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'<script>'+js+'</script></body></html>'
    results=[]
    with sync_playwright() as pw:
      browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
      version=browser.version
      for name,width,opts in CASES:
        opts=dict(opts);zoom=opts.pop('zoom',None)
        ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**opts)
        page=ctx.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content(document,wait_until='load')
        page.evaluate('''() => {window.__perf={lcp:null,cls:0};try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__perf.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__perf.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}}''')
        if zoom:page.locator('.fv-apollo-atlas').evaluate('(e,z)=>e.style.zoom=z',zoom)
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),(name,'overflow')
        assert page.locator('aside.fv-apollo-method .fv-apollo-trace').count()==0,name
        assert page.locator('.fv-apollo-content > .fv-apollo-trace').count()==1,name
        assert page.get_by_role('link',name='Read original investigation →').count()==1
        ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        assert any('Trace each finding' in str(n.get('name',{}).get('value','')) for n in ax),name
        a=page.locator('.fv-apollo-trace a[href^="#"]').first
        a.focus();assert a.evaluate('(e)=>e===document.activeElement')
        if opts.get('has_touch'):a.tap()
        else:a.press('Enter')
        assert page.evaluate('document.activeElement.id')=='fv-apollo-finding-oxygen',name
        summary=page.locator('details summary').first;summary.focus();summary.press('Enter')
        assert page.locator('details').first.evaluate('(e)=>e.open')
        summary.press('Enter');assert not page.locator('details').first.evaluate('(e)=>e.open')
        page.evaluate("() => {location.hash='';document.activeElement.blur();window.scrollTo(0,0);document.querySelectorAll('details[open]').forEach(e=>e.removeAttribute('open'))}")
        page.wait_for_timeout(110)
        shot=out/(name+'.png');page.screenshot(path=str(shot),full_page=True,animations='disabled')
        vitals=page.evaluate('window.__perf') if opts.get('java_script_enabled',True) else None
        assert not errs,(name,errs)
        results.append({'case':name,'width':width,'screenshot_sha256':sha(shot.read_bytes()),
                        'lab_performance_observer':vitals,'scroll_overflow':False,'keyboard_target':'fv-apollo-finding-oxygen'})
        ctx.close()
      browser.close()
    receipt={'release':'R204','scope':'offline real Chromium with generated PHP, not installed WP staging',
      'browser_version':version,'source_sha256':manifest['files'],'source_custody':counts,
      'negative_mutations_rejected':rejected,'case_results':results,
      'passed':True,'genuine_axe_core_executed':False,'canonical_r198_source_chain_verified':False,
      'commercial_product_verified':False,'merchant_confirmed_sales':None,
      'release_blockers':['canonical R198 builder differs from local ancestor; exact-GitHub ancestry unverified',
         'genuine axe-core and NVDA/VoiceOver tests not performed','installed WordPress/theme/CSP/CDN QA missing',
         'exact-head hosted CI and founder release approval missing','no seller-confirmed relevant SKU or net revenue']}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'result':'PASS','contexts':len(results),'mutations_rejected':rejected,'chromium':version}))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r204-qa'))
