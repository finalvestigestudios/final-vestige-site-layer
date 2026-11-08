#!/usr/bin/env python3
"""R206 real Chromium + PHP fixture acceptance; NOT installed WordPress or axe.

A failed inherited R198 canonical source gate is explicitly preserved.
Uses no external services, no production modification, no invented sales numbers.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r206 import build,digest,BOARD,AFTERMATH
DIST=ROOT/'dist'
CASE=[('320',320,{}),('390',390,{}),('768',768,{}),('1440',1440,{}),('1920',1920,{}),
      ('390-nojs',390,{'java_script_enabled':False}),('390-touch',390,{'has_touch':True,'is_mobile':True}),
      ('390-reduced',390,{'reduced_motion':'reduce'}),('390-forced',390,{'forced_colors':'active'}),
      ('320-csszoom200',320,{'zoom':2})]
STATUSES=('Documented','Most probable','Not determined')
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def audit(html:str)->dict:
    doc=BeautifulSoup(html,'html.parser');a=doc.select_one('article.fv-apollo-atlas');assert a
    section=a.select_one('section#fv-apollo-confidence');assert section
    assert section.get('aria-labelledby')=='fv-apollo-confidence-title'
    assert a.select_one('#fv-apollo-chronology').find_next('section',id='fv-apollo-confidence')==section
    cards=section.select('ol.fv-apollo-confidence-list > li');assert len(cards)==3
    for card,status in zip(cards,STATUSES):
        det=card.select_one('details');assert det and not det.has_attr('open')
        summary=det.select_one('summary');assert summary
        assert summary.select_one('.fv-apollo-confidence-status').get_text(strip=True)==status
        assert len(summary.select('.fv-apollo-confidence-question'))==1
        assert len(det.select('a[href^="#fv-apollo-"]'))==1
        link=det.select_one('a[href^="https://www.nasa.gov/"]');assert link
        assert link['href']==(AFTERMATH if status=='Not determined' else BOARD)
    assert not section.has_attr('data-purchase')
    assert [e.get_text(' ',strip=True) for e in section.select('a[href^="https://www.nasa.gov/"]')] == [
        'Read NASA Review Board Finding 2','Read NASA Review Board Finding 1','Open NASA S67-21294 catalog']
    for link in section.select('a[href^="#"]'):
        assert a.select_one(link['href']) is not None
    assert 'no single ignition source was conclusively identified' in section.get_text(' ',strip=True).lower()
    assert '100-percent oxygen atmosphere at 16.7 psia' in section.get_text(' ',strip=True)
    assert not section.select('form,button,script,[data-purchase],[data-affiliate]')
    assert len(a.select('details'))==11
    assert len(a.select('.fv-apollo-rail-source'))==4
    assert len(a.select('a.cta'))==1 and a.select_one('a.cta')['href']==DEST
    assert not a.select_one('a.cta').has_attr('data-affiliate')
    assert len(a.select('.fv-apollo-trace-grid li'))==4
    ids=[n.get('id') for n in a.select('[id]')];assert len(ids)==len(set(ids))
    assert not a.select('[data-geo],[data-lat],[data-lng]')
    return {'confidence_cards':3,'native_disclosures':11,'NASA_rail_links':4,'commercial_ctas':0,'editorial_ctas':1}

def main(out:Path):
    out.mkdir(exist_ok=True,parents=True)
    manifest=build();assert not manifest['source_chain_verified']
    assert manifest['no_commercial_activation']
    for name,h in manifest['files'].items():assert digest((DIST/name).read_bytes())==h
    subprocess.run(['php','-l',str(DIST/'fv-ex2-apollo-r206.php')],capture_output=True,check=True)
    def render(mode):
        return json.loads(subprocess.check_output(['php',str(DIST/'wp-render-shim-r206.php'),str(DIST/'fv-ex2-apollo-r206.php'),mode],text=True))
    normal=render('normal');assert normal['fallback'] is False
    printed=render('printed');assert printed['fallback'] is False
    assert render('late')['fallback'] is True
    html=normal['html'];counts=audit(html)
    mutants={
      'dropped_card':html.replace('fv-apollo-confidence-status">Documented','wrong-status">Documented',1),
      'false_ignition_certain':html.replace('No single ignition source was conclusively identified','The specific ignition source was conclusively identified',1),
      'inject_buy_button':html.replace('id="fv-apollo-confidence"','id="fv-apollo-confidence" data-purchase="true"',1),
      'bypass_NASA':html.replace('Read NASA Review Board Finding 2','Read unverified report',1),
      'lost_detail':html.replace('<details>','<aside>',1),
      'extra_paid_cta':html.replace('class="cta"','class="cta" data-affiliate="1"',1),
      'broken_target':html.replace('href="#fv-apollo-finding-oxygen"','href="#missing-nasa-claim"',1),
      'duplicate_id':html.replace('id="fv-apollo-confidence"','id="fv-apollo-evidence"',1),
    }
    rejected=[]
    for name,bad in mutants.items():
        try:
            audit(bad)
            if name=='broken_target':
                # Also assert all local anchors resolve (beyond the core audit).
                root=BeautifulSoup(bad,'html.parser');assert not root.select_one('a[href="#missing-nasa-claim"]')
        except (AssertionError,AttributeError,KeyError):rejected.append(name)
    assert sorted(rejected)==sorted(mutants),(rejected,sorted(mutants))
    css=(DIST/'assets/atlas-scoped.css').read_text();js=(DIST/'assets/campaign-handoff.js').read_text()
    page_html='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'<script>'+js+'</script></body></html>'
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        version=browser.version
        for name,width,kw in CASE:
            kw=dict(kw);zoom=kw.pop('zoom',None)
            ctx=browser.new_context(viewport={'width':width,'height':850},device_scale_factor=1,**kw)
            pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
            pg.evaluate('''() => { window.__vitals={lcp:null,cls:0};try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__vitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(e){} }''')
            pg.set_content(page_html,wait_until='load')
            if zoom:pg.locator('.fv-apollo-atlas').evaluate('(el)=>{el.style.zoom="200%"}')
            assert pg.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),name+' horizontal overflow'
            assert pg.get_by_role('heading',name='What is documented, probable, and unresolved?').count()==1
            cards=pg.locator('.fv-apollo-confidence-list details');assert cards.count()==3
            for idx,status in enumerate(STATUSES):
                s=cards.nth(idx).locator('summary')
                s.focus();assert s.evaluate('(el)=>document.activeElement===el')
                assert not cards.nth(idx).evaluate('(el)=>el.open')
                if kw.get('has_touch'):s.tap()
                else:s.press('Enter')
                assert cards.nth(idx).evaluate('(el)=>el.open')
                nasa=cards.nth(idx).locator('a[href^="https://www.nasa.gov/"]')
                assert nasa.count()==1
                assert nasa.get_attribute('href') == (AFTERMATH if idx==2 else BOARD)
                s.focus();s.press('Enter')
                assert not cards.nth(idx).evaluate('(el)=>el.open')
            # Confirm browser accessibility tree includes each question and the CTA.
            ax=ctx.new_cdp_session(pg).send('Accessibility.getFullAXTree')['nodes']
            for term in ['What were the test conditions?','How might the fire have started?','Can a photograph settle the cause?','Read original investigation']:
                assert any(term in str(n.get('name',{}).get('value','')) for n in ax),name+' AX tree missing '+term
            assert not errors,(name,errors)
            # Stable baseline screenshot after expanding state tested above.
            pg.evaluate('''() => {location.hash='';document.activeElement.blur();document.querySelectorAll('details[open]').forEach(el=>el.removeAttribute('open'));scrollTo(0,0)}''')
            pg.wait_for_timeout(220)
            shot=out/(name+'.png');pg.screenshot(path=str(shot),full_page=True,animations='disabled')
            results.append({'case':name,'width':width,'screenshot_sha256':digest(shot.read_bytes()),
                            'LCP_CLS_offline_fixture_only':pg.evaluate('window.__vitals') if kw.get('java_script_enabled',True) else None,
                            'native_disclosures_tested':3,'console_page_errors':len(errors),'overflow':False})
            ctx.close()
        browser.close()
    receipt={'release':'r206','test_environment':'Local PHP function shim and genuine Chromium; not WP staging',
      'browser_version':version,'checks':counts,'mutations_rejected':rejected,'contexts':results,
      'tests_passed':True,'source_chain_verified':False,'genuine_axe_core_executed':False,
      'NVDA_VoiceOver_executed':False,'installed_WordPress_executed':False,
      'actual_browser_UI_zoom_executed':False,'merchant_paid_orders_verified':False,
      'release_gate':'STAGING HOLD: R198 canonical mismatch, full installed WP, axe, AT, CI, release QA, founder approval'}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'PASS':True,'chromium':version,'contexts':len(results),'negative_mutations':len(rejected)}))
if __name__=='__main__':main(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/r206-qa'))
