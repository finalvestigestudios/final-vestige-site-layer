#!/usr/bin/env python3
"""Real Chromium local fixture acceptance for the PHP-rendered R200 Apollo Atlas.
No host navigation/installed WordPress claim. No axe-core claim.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r200 import CHRONOLOGY,build,sha
CASES=[('320',320,{}),('360',360,{}),('390',390,{}),('768',768,{}),
       ('1024',1024,{}),('1440',1440,{}),('1920',1920,{}),
       ('390-nojs',390,{'java_script_enabled':False}),
       ('390-reduced',390,{'reduced_motion':'reduce'}),
       ('390-forced',390,{'forced_colors':'active'}),
       ('390-touch',390,{'is_mobile':True,'has_touch':True}),
       ('320-zoom200',320,{'zoom':2})]

def render(dist,mode='normal'):
    return json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r200.php'),str(dist/'fv-ex2-apollo-r200.php'),mode],text=True))

def custody(html, ledger):
    doc=BeautifulSoup(html,'html.parser')
    rails=doc.select('.fv-apollo-atlas .rail > li')
    assert len(rails)==4
    assert len(doc.select('.fv-apollo-atlas .cta'))==1
    assert doc.select_one('.fv-apollo-atlas .cta')['href']=='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
    assert len(doc.select('.fv-apollo-atlas details'))==8
    assert len(doc.select('.fv-apollo-atlas [data-geo], .fv-apollo-atlas [data-lat],.fv-apollo-atlas iframe,.fv-apollo-atlas form'))==0
    ids=[e['id'] for e in doc.select('[id]')]
    assert len(ids)==len(set(ids)), 'duplicate IDs'
    assert len(ledger)==4
    for li,item in zip(rails,ledger):
        assert li['data-evidence-kind']==item['evidence_kind']
        assert li.select_one('time')['datetime']==item['date']
        assert li.select_one('.fv-apollo-rail-kind').get_text(' ',strip=True)==item['visible_label']
        assert li.select_one('a')['href']=='#'+item['target']
        assert doc.select_one('#'+item['target']) is not None
        assert item['official_source'].startswith('https://www.nasa.gov/')
        assert item['commercial_media_rights']=='not_certified'
    text=doc.get_text(' ',strip=True)
    assert 'photograph is not a sensor trace' in text
    assert 'not proof of a particular ignition mechanism' in text
    assert 'No purchase, signup or affiliate conversion is claimed' in text
    assert 'NASA does not endorse Final Vestige' in text
    return True

def run(root):
    root.mkdir(parents=True,exist_ok=True)
    manifest=build(); dist=ROOT/'dist'
    for name,digest in manifest['files'].items():assert sha((dist/name).read_bytes())==digest,name
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r200.php')],check=True,capture_output=True)
    live=render(dist); assert not live['fallback'] and live['chronology']==4 and live['details']==8
    assert not render(dist,'printed')['fallback']
    assert render(dist,'late')['fallback']
    css=(dist/'assets/atlas-scoped.css').read_text('utf-8');html=live['html']
    ledger=json.loads((dist/'chronology-source-ledger.json').read_text())
    assert sha((dist/'chronology-source-ledger.json').read_bytes())==manifest['chronology_source_ledger_sha256']
    custody(html,ledger)
    mutants={
      'misdated_event':html.replace('datetime="1967-01-27"','datetime="1967-02-27"',1),
      'photo_passed_off_as_review_board':html.replace('data-evidence-kind="aftermath-photo"','data-evidence-kind="technical-report"',1),
      'broken_source_target':html.replace('href="#fv-apollo-photo-1966"','href="#fake-photo"',1),
      'false_source_badge':html.replace('Catalog photograph · the following day','Verified ignition photo',1),
      'fake_ignition_certainty':html.replace('not proof of a particular ignition mechanism','proof of the exact ignition mechanism',1),
      'unreviewed_product':html.replace('class="cta"','class="cta" data-purchase="paid-dossier"',1),
      'duplicate_id':html.replace('id="fv-apollo-rail-reading-key"','id="fv-apollo-main"',1),
      'fake_sale':html.replace('No purchase, signup or affiliate conversion is claimed','Confirmed affiliate conversions occurred',1),
    }
    def strict(h):
        custody(h,ledger)
        d=BeautifulSoup(h,'html.parser')
        assert not d.select('[data-purchase]')
    rejected=[]
    for key,mutation in mutants.items():
        try:strict(mutation)
        except AssertionError:rejected.append(key)
    assert len(rejected)==len(mutants),(rejected,list(mutants))
    receipt={'release':'R200','environment':'actual PHP adapter output in a WordPress-function shim, real local Chromium set_content fixture',
             'source_hashes':manifest['files'],'browser_version':None,'cases':[], 'mutations_rejected':rejected,
             'blocked':['Installed WordPress and production CDN/CSP/nav not evaluated', 'Genuine axe-core and NVDA/VoiceOver unavailable',
                        'No attributable published Grok Apollo asset_id or verified sellable Apollo product',
                        'No qualified-session denominator, independently verified order/fees/refunds or net revenue',
                        'Offline fixture LCP/CLS is not production field performance or lighthouse']}
    with sync_playwright() as pw:
      browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
      receipt['browser_version']=browser.version
      for label,width,opts in CASES:
        opts=dict(opts); zoom=opts.pop('zoom',None)
        ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,**opts)
        page=ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
        if zoom:page.locator('.fv-apollo-atlas').evaluate('(e,z)=>e.style.zoom=z',zoom)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),label+' overflow'
        assert page.get_by_role('list').count()>=1
        items=page.locator('.fv-apollo-atlas .rail > li'); assert items.count()==4
        ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        names=[n.get('name',{}).get('value','') for n in ax if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
        for date,target,badge,kind,url in CHRONOLOGY:
          row=items.filter(has=page.locator('time[datetime="'+date+'"]'))
          assert row.count()==1
          assert row.locator('.fv-apollo-rail-kind').inner_text()==badge
          link=row.get_by_role('link')
          assert link.count()==1 and link.get_attribute('href')=='#'+target
          assert any(''!=n and link.inner_text() in n for n in names)
          link.focus()
          assert link.evaluate('(e)=>document.activeElement===e'),label+' link focus '+date
          assert page.locator('#'+target).count()==1
          if 'touch' not in label:
            link.press('Enter')
            assert page.evaluate('document.activeElement.id')==target,(label,target)
          else:
            link.tap()
            assert page.evaluate('document.activeElement.id')==target,(label,target)
          assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(label,'after link action')
        assert page.locator('.fv-apollo-atlas details').count()==8
        assert page.locator('.fv-apollo-atlas .cta').count()==1
        page.evaluate("() => {location.hash='';document.activeElement?.blur();window.scrollTo(0,0);document.querySelectorAll('details[open]').forEach(x=>x.removeAttribute('open'))}")
        page.wait_for_timeout(110)
        metrics=page.evaluate('''async()=>{let lcp=null,cls=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){};await new Promise(r=>setTimeout(r,70));return {lcp_ms:lcp,cls}}''') if opts.get('java_script_enabled',True) else {'lcp_ms':None,'cls':None}
        screenshot=root/(label+'.png');page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
        assert not errors,errors
        receipt['cases'].append({'case':label,'width':width,'source_roles':4,'navigation_checks':4,'no_horizontal_overflow':True,'lab_vitals':metrics,'screenshot_sha256':sha(screenshot.read_bytes())})
        ctx.close()
      browser.close()
    (root/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(CASES),'navigation_checks':len(CASES)*4,'negative_controls':len(rejected), 'chromium_version':receipt['browser_version'],'receipt_sha256':sha((root/'receipt.json').read_bytes())}))
if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r200-evidence'))
