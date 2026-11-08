#!/usr/bin/env python3
"""Actual Chromium + PHP shortcode regression for R205, local fixture only.

No claim to genuine axe-core, installed WordPress, production LCP or paid sales.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r205 import build,sha,RECORDS
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CASES=[('320',320,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),
       ('390-nojs',390,{'java_script_enabled':False}),('390-reduced',390,{'reduced_motion':'reduce'}),
       ('390-touch',390,{'has_touch':True,'is_mobile':True}),('390-forced',390,{'forced_colors':'active'}),
       ('320-csszoom200',320,{'zoom':2})]
def source_gate(html):
    dom=BeautifulSoup(html,'html.parser')
    atlas=dom.select_one('.fv-apollo-atlas');assert atlas
    rail=atlas.select('#fv-apollo-chronology .rail > li');assert len(rail)==4
    for li, rec in zip(rail,RECORDS):
        kind,date,ref,url,label,boundary=rec
        assert li.get('data-evidence-kind')==kind
        assert li.select_one('time')['datetime']==date
        a=li.select_one('a.fv-apollo-rail-source');assert a
        assert a.get('href')==url and a.get('data-source-id')==ref and a.get_text(strip=True)==label
        note=li.select_one('small');assert note and note.get('id')==a.get('aria-describedby')
        assert 'noopener' in a.get('rel',[]) and 'noreferrer' in a.get('rel',[])
    assert len(atlas.select('a.fv-apollo-rail-source'))==4
    assert len(atlas.select('a.cta'))==1 and atlas.select_one('a.cta')['href']==DEST
    assert len(atlas.select('details'))==8
    assert len(atlas.select('.fv-apollo-trace-grid > li'))==4
    assert not atlas.select('form,[data-purchase],[data-affiliate],[data-geo],[data-lat]')
    ids=[x.get('id') for x in atlas.select('[id]')];assert len(ids)==len(set(ids))
    return {'chronology':4,'record_specific_sources':4,'disclosures':8,'paid_ctas':0,'editorial_ctas':1}

def run(out):
    out.mkdir(exist_ok=True,parents=True)
    manifest=build();dist=ROOT/'dist';assert manifest['source_chain_verified'] is False
    for p,d in manifest['files'].items():assert sha((dist/p).read_bytes())==d
    php=str(dist/'fv-ex2-apollo-r205.php');shim=str(dist/'wp-render-shim-r205.php')
    subprocess.run(['php','-l',php],capture_output=True,check=True)
    def render(mode):return json.loads(subprocess.check_output(['php',shim,php,mode],text=True))
    normal=render('normal');assert not normal['fallback']
    assert not render('printed')['fallback']
    assert render('late')['fallback']
    html=normal['html'];counts=source_gate(html)
    mutations={
      'missing_original_link':html.replace('class="cta"','class="not-a-cta"',1),
      'replaced_photo_authority':html.replace('href="https://www.nasa.gov/image-detail/amf-s67-21294/" aria-describedby="fv-apollo-rail-note-aftermath-photo"','href="https://example.net/fake" aria-describedby="fv-apollo-rail-note-aftermath-photo"',1),
      'hidden_source':html.replace('class="fv-apollo-rail-source"','class="hidden-rail-source"',1),
      'source_id_forgery':html.replace('data-source-id="S66-58038"','data-source-id="invented"',1),
      'description_id_mismatch':html.replace('aria-describedby="fv-apollo-rail-note-archival-photo"','aria-describedby="missing-note"',1),
      'commercial_injection':html.replace('class="cta"','class="cta" data-purchase="true"',1),
      'duplicate_id':html.replace('id="fv-apollo-rail-note-photo-and-history"','id="fv-apollo-rail-note-archival-photo"',1),
      'date_forgery':html.replace('datetime="1967-01-03"','datetime="1967-02-03"',1),
    }
    rejected=[]
    for k,m in mutations.items():
        try:source_gate(m)
        except (AssertionError,AttributeError,KeyError):rejected.append(k)
    assert sorted(rejected)==sorted(mutations),rejected
    css=(dist/'assets/atlas-scoped.css').read_text('utf8')
    js=(dist/'assets/campaign-handoff.js').read_text('utf8')
    doc='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'<script>'+js+'</script></body></html>'
    outcomes=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        browser_version=b.version
        for name,width,options in CASES:
            opts=dict(options);zoom=opts.pop('zoom',None)
            ctx=b.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**opts)
            page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(doc,wait_until='load')
            if opts.get('java_script_enabled',True):
                page.evaluate('''() => {window.__perf={lcp:null,cls:0};try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__perf.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__perf.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){}}''')
            if zoom:page.locator('.fv-apollo-atlas').evaluate('(el,z)=>{el.style.zoom=z}',zoom)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),name+' overflow'
            for kind,date,ref,url,label,limitation in RECORDS:
                link=page.get_by_role('link',name=label)
                assert link.count()==1,(name,label)
                assert link.get_attribute('href')==url
                link.focus();assert link.evaluate('(el)=>document.activeElement===el')
                description=page.evaluate('''label=>{let a=[...document.querySelectorAll('a.fv-apollo-rail-source')].find(e=>e.textContent===label);return a&&document.getElementById(a.getAttribute('aria-describedby'))?.textContent}''',label)
                assert description and description.strip(),name+' a11y description missing'
            ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
            for r in RECORDS:assert any(r[4] in str(n.get('name',{}).get('value','')) for n in ax),name+' AX missing '+r[2]
            rail_link=page.locator('#fv-apollo-chronology .rail li > a[href^="#"]').first
            rail_link.focus()
            if opts.get('has_touch'):rail_link.tap()
            else:rail_link.press('Enter')
            assert page.evaluate('document.activeElement.id')=='fv-apollo-photo-1966',name+' history focus'
            summ=page.locator('details summary').first;summ.focus();summ.press('Enter')
            assert page.locator('details').first.evaluate('(e)=>e.open'),name+' details'
            summ.press('Enter');assert not page.locator('details').first.evaluate('(e)=>e.open')
            page.evaluate("() => {location.hash='';document.activeElement.blur();window.scrollTo(0,0);document.querySelectorAll('details[open]').forEach(e=>e.removeAttribute('open'))}")
            page.wait_for_timeout(160)
            image=out/(name+'.png');page.screenshot(path=str(image),animations='disabled',full_page=True)
            assert not errors,(name,errors)
            outcomes.append({'case':name,'width':width,'screenshot_sha256':sha(image.read_bytes()),
                 'lab_performance_observer':page.evaluate('window.__perf') if opts.get('java_script_enabled',True) else None,
                 'source_links_accessible':4,'overflow':False})
            ctx.close()
        b.close()
    receipt={'release':'r205','test_environment':'LOCAL generated PHP fixture, real Chromium, not WordPress staging',
      'browser_version':browser_version,'source_file_sha256':manifest['files'],'source_counts':counts,
      'negative_mutations_rejected':rejected,'contexts':outcomes,'passed':True,
      'genuine_axe_core_executed':False,'installed_wordpress_staging_executed':False,
      'source_chain_verified':False,'merchant_confirmed_sales':None,
      'release_blockers':['R198 canonical GitHub source builder mismatches supplied local chain',
       'axe-core, NVDA/VoiceOver, real browser zoom and actual WP staging still pending',
       'hosted exact-head CI and independent release QA missing',
       'no approved rights-cleared matching product, checkout, paid conversion or net-revenue evidence']}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'PASS':True,'chromium':browser_version,'contexts':len(outcomes),'mutations_rejected':len(rejected)}))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r205'))
