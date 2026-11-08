#!/usr/bin/env python3
"""Apollo R203: actual PHP-rendered fixture, Chromium interactions, and commerce-boundary controls.

Does not claim installed WordPress, live CWV, hosted CI, axe-core or paid conversions.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r203 import build,sha
CASES=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),
       ('1024',1024,{}),('1440',1440,{}),('1920',1920,{}),
       ('390-nojs',390,{'java_script_enabled':False}),
       ('390-reduced',390,{'reduced_motion':'reduce'}),
       ('390-forced',390,{'forced_colors':'active'}),
       ('390-touch',390,{'is_mobile':True,'has_touch':True}),
       ('320-zoom200',320,{'zoom':2})]
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def render(dist,mode='normal'):
    return json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r203.php'),str(dist/'fv-ex2-apollo-r203.php'),mode],text=True))

def custody(html):
    d=BeautifulSoup(html,'html.parser')
    atlas=d.select_one('.fv-apollo-atlas'); assert atlas is not None
    assert len(d.select('.fv-apollo-atlas .rail > li'))==4
    assert len(d.select('.fv-apollo-atlas details'))==8
    assert len(d.select('.fv-apollo-atlas a.cta'))==1
    assert d.select_one('a.cta')['href']==DEST
    assert len(d.select('.fv-apollo-atlas .fv-apollo-educator-note'))==1
    assert len(d.select('.fv-apollo-citation-route'))==1
    assert len(d.select('.fv-apollo-citation-route a'))==2
    assert 'the precise initiating spark' in d.select_one('.fv-apollo-citation-route').get_text(' ',strip=True)
    assert not any(x in atlas.get_text(' ',strip=True) for x in ('ChronologyRail','EvidencePlate','SourceDrawer','Research Desk / Try the source test'))
    lab=d.select_one('.fv-apollo-reading-lab');assert lab and len(lab.select('ol > li'))==3
    assert [a.get('href') for a in lab.select('a')]==['https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/','https://www.nasa.gov/image-detail/amf-s67-21294/']
    assert 'For educators and researchers:' in atlas.get_text(' ',strip=True)
    assert 'NASA does not endorse Final Vestige' in atlas.get_text(' ',strip=True)
    assert not any(word in atlas.get_text(' ',strip=True).lower() for word in
      ('research prototype','unpublished prototype','proposed product','affiliate conversion','conversion is claimed','confirmed sales','checkout now','limited-time','pay $'))
    assert not d.select('form,iframe,[data-geo],[data-lat],[data-purchase],[data-affiliate]')
    ids=[e['id'] for e in d.select('[id]')];assert len(ids)==len(set(ids))
    sources=[a['href'] for a in d.select('a[href^="https://www.nasa.gov/"]')]
    assert len(sources)>=8 and all(u.startswith('https://www.nasa.gov/') for u in sources)
    assert sources.count('https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/')>=4
    return True

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    for p,d in manifest['files'].items():assert sha((dist/p).read_bytes())==d,p
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r203.php')],check=True,capture_output=True)
    normal=render(dist);assert not normal['fallback'] and normal['details']==8
    assert not render(dist,'printed')['fallback']
    assert render(dist,'late')['fallback']
    html=normal['html'];custody(html)
    originals={'old_prototype_phrase':html.replace('These links open NASA', 'This unpublished prototype links open NASA',1),
      'fake_product':html.replace('free of charge','pay $29 for access',1),
      'fake_sales':html.replace('NASA does not endorse Final Vestige','Confirmed affiliate conversion occurred',1),
      'extra_cta':html.replace('class="cta"','class="cta" data-purchase="paid"',1),
      'missing_educator_note':html.replace('fv-apollo-educator-note','not-an-educator-note',1),
      'broken_cta':html.replace(DEST,'https://example.invalid/buy',1),
      'missing_review_board':html.replace('https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/', 'https://example.invalid/source'),
      'duplicate_id':html.replace('id="fv-apollo-rail-reading-key"','id="fv-apollo-main"',1),
      'missing_lab':html.replace('class="fv-apollo-reading-lab"','class="bad-lab"',1),
      'public_component_jargon':html.replace('03 / NASA photographic records','03 / SourceDrawer',1),
      'missing_citation_route':html.replace('class="fv-apollo-citation-route"','class="hidden-citation"',1)}
    rejected=[]
    for name,mutant in originals.items():
        try:custody(mutant)
        except AssertionError:rejected.append(name)
    assert len(rejected)==len(originals),set(originals)-set(rejected)
    css=(dist/'assets/atlas-scoped.css').read_text('utf-8')
    js=(dist/'assets/campaign-handoff.js').read_text('utf-8')
    wrapper=lambda code='': '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'<script>'+code+'</script></body></html>'
    receipt={'release':'R203','source_hashes':manifest['files'],'scope':'PHP-generated fixture; real local Chromium, not installed WordPress',
             'negative_controls_rejected':rejected,'case_results':[], 'utm_policy':{},
             'blocked':['Genuine axe-core, NVDA/VoiceOver and installed WordPress unavailable',
                        'Real host navigation/CDN/CSP and exact-head hosted CI not verified',
                        'No verified Apollo paid SKU, checkout or fulfillment',
                        'No published Grok Apollo asset_id, qualified human denominator, independently verified orders or realized net revenue']}
    with sync_playwright() as pw:
      browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
      receipt['browser_version']=browser.version
      for label,width,options in CASES:
        options=dict(options);zoom=options.pop('zoom',None)
        ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**options)
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(wrapper(),wait_until='load')
        if zoom:page.locator('.fv-apollo-atlas').evaluate('(e,z)=>e.style.zoom=z',zoom)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'),(label,'overflow')
        assert page.get_by_role('link',name='Read original investigation →').count()==1
        ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        links=[n.get('name',{}).get('value','') for n in ax if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
        assert any('Read original investigation' in n for n in links),label
        for li in page.locator('.fv-apollo-atlas .rail > li').all():
          a=li.get_by_role('link');target=a.get_attribute('href')[1:]
          a.focus();assert a.evaluate('(e)=>document.activeElement===e')
          if options.get('has_touch'):a.tap()
          else:a.press('Enter')
          assert page.evaluate('document.activeElement.id')==target,(label,target)
        summary=page.locator('.fv-apollo-atlas details').first.locator('summary')
        summary.focus();summary.press('Enter')
        assert page.locator('.fv-apollo-atlas details').first.evaluate('(e)=>e.open')
        summary.press('Enter')
        assert not page.locator('.fv-apollo-atlas details').first.evaluate('(e)=>e.open')
        page.evaluate("() => {location.hash='';document.activeElement.blur();window.scrollTo(0,0);document.querySelectorAll('details[open]').forEach(e=>e.removeAttribute('open'))}")
        page.wait_for_timeout(120)
        png=out/(label+'.png');page.screenshot(path=str(png),full_page=True,animations='disabled')
        metric=page.evaluate('''async()=>{let lcp=null,cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){};await new Promise(r=>setTimeout(r,80));return {lcp_ms:lcp,cls}}''') if options.get('java_script_enabled',True) else {'lcp_ms':None,'cls':None}
        assert not errors,(label,errors)
        receipt['case_results'].append({'case':label,'width':width,'rail_navigation':4,'disclosure_toggles':2,
          'lab_vitals':metric,'no_horizontal_overflow':True,'screenshot_sha256':sha(png.read_bytes())})
        ctx.close()
      # Campaign passthrough is tested as link decoration ONLY, never an attributed sale.
      for name,url,expected in [
          ('valid','http://127.0.0.1:29765/?utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_asset_01',True),
          ('duplicate','http://127.0.0.1:29765/?utm_source=youtube&utm_source=tiktok&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_asset_01',False),
          ('invalid_asset','http://127.0.0.1:29765/?utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=%3Cscript%3E',False),
          ('none','http://127.0.0.1:29765/',False)]:
        ctx=browser.new_context();page=ctx.new_page()
        page.set_content(wrapper(),wait_until='load')
        query=url.partition('?')[2]
        page.evaluate('(q)=>history.replaceState({},"","about:blank"+(q?"?"+q:""))',query)
        page.evaluate(js);page.wait_for_timeout(40)
        href=page.locator('.fv-apollo-atlas .cta').get_attribute('href')
        assert ('utm_campaign=' in href)==expected,(name,href)
        assert href.startswith(DEST)
        receipt['utm_policy'][name]={'expected_pass':expected,'actual_pass':'utm_campaign=' in href,'is_sale':False}
        ctx.close()
      browser.close()
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','contexts':len(CASES),'rail_journeys':len(CASES)*4,
       'native_disclosure_toggles':len(CASES)*2,'negative_controls':len(rejected),
       'utm_tests':len(receipt['utm_policy']),'chromium':receipt['browser_version']}))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r203-evidence'))
