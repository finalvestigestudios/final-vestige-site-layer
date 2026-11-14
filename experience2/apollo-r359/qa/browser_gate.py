#!/usr/bin/env python3
"""R359 independent Chromium regression of inherited R357 rendered contract. Not axe-core, live WordPress, or production CWV."""
import json, subprocess
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
EX=ROOT/'experience2'
OUT=EX/'apollo-r359/QA'
OUT.mkdir(parents=True,exist_ok=True)
BRIDGE=EX/'apollo-r359/resolved-block-template-prehead.php'
def render(fn):
    code='define("ABSPATH", true); require '+json.dumps(str(BRIDGE))+'; echo '+fn+'();'
    return subprocess.check_output(['php','-r',code],text=True)
html_full=render('fv_apollo_r357_full');html_note=render('fv_apollo_r357_note')
note_css='\n'.join((EX/x).read_text() for x in ('apollo-r355/postfire-ledger.css','apollo-r356/assets/print-proof.css'))
full_css='\n'.join((EX/x).read_text() for x in (
'apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css',
'apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css',
'apollo-r348/assets/source-custody.css','apollo-r355/postfire-ledger.css',
'apollo-r356/assets/print-proof.css'))
script=(EX/'apollo-r347/assets/source-index.js').read_text()
def document(html,css):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<style>html,body{margin:0}'+css+'</style></head><body>'+html+'</body></html>')
cases=[('full-320-nojs','full',320,False,False,16,'reduce','none'),
 ('full-320-400pct','full',320,True,False,64,'reduce','none'),
 ('note-390-keyboard','note',390,True,False,16,'no-preference','none'),
 ('note-390-nojs','note',390,False,False,16,'reduce','none'),
 ('full-768-touch','full',768,True,True,16,'reduce','none'),
 ('full-1440-keyboard','full',1440,True,False,16,'no-preference','none'),
 ('full-1920-forced','full',1920,True,False,16,'reduce','active')]
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for label,mode,width,js,touch,font,motion,forced in cases:
        ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                                has_touch=touch,reduced_motion=motion,forced_colors=forced)
        page=ctx.new_page()
        page.set_content(document(html_full if mode=='full' else html_note,full_css if mode=='full' else note_css),wait_until='load')
        if js:
            page.evaluate("""() => {window.__qa={lcp:[],cls:0};
              try{new PerformanceObserver(l=>l.getEntries().forEach(x=>window.__qa.lcp.push(x.startTime))).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}
              try{new PerformanceObserver(l=>l.getEntries().forEach(x=>{if(!x.hadRecentInput)window.__qa.cls+=x.value})).observe({type:'layout-shift',buffered:true})}catch(e){}}""")
            if mode=='full':page.add_script_tag(content=script)
        if font!=16:page.evaluate('(f)=>document.documentElement.style.fontSize=f+"px"',font)
        assert page.locator('[data-fv-apollo-postfire]').count()==1,label
        assert page.locator('[data-fv-r355-reviewed-source]').count()==1,label
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+1'),label
        assert page.locator('img, iframe, script[src]').count()==0,label
        ids=page.eval_on_selector_all('[id]','els=>els.map(x=>x.id)');assert len(ids)==len(set(ids)),label
        for s in page.locator('details > summary').all():assert s.inner_text().strip(),label
        later=page.locator('.fv-apollo-r355__source summary');later.focus();page.keyboard.press('Enter')
        assert later.evaluate('(el)=>el.parentNode.open'),label
        assert later.evaluate('(el)=>getComputedStyle(el).cursor')=='pointer',label
        if mode=='full':
            assert page.locator('[data-fv-apollo-entry]').count()==13,label
            assert page.locator('[data-fv-r339-cta="editorial"]').count()==1,label
            assert page.locator('[data-fv-custody-source]').count()==8,label
            if js:
                btns=page.locator('[data-fv-apollo-filters] button');assert btns.count()==5,label
                if touch:btns.nth(4).tap()
                else:btns.nth(4).click()
                assert page.locator('[data-fv-apollo-entry]:visible').count()==4,label
                assert btns.nth(4).get_attribute('aria-pressed')=='true',label
                btns.nth(0).click();assert page.locator('[data-fv-apollo-entry]:visible').count()==13,label
            else:
                assert page.locator('[data-fv-apollo-entry]:visible').count()==13,label
        else:
            assert page.locator('[data-fv-apollo-entry],[data-fv-r339-cta="editorial"]').count()==0,label
        # Native Chromium accessibility tree, not axe. Every accessible link has a nonempty name.
        session=ctx.new_cdp_session(page)
        tree=session.send('Accessibility.getFullAXTree')
        links=[n for n in tree['nodes'] if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
        assert links and all(n.get('name',{}).get('value','').strip() for n in links),label
        page.screenshot(path=str(OUT/(label+'.png')),full_page=False)
        page.wait_for_timeout(160)
        perf=page.evaluate('window.__qa||null') if js else None
        results.append({'case':label,'mode':mode,'viewport_width':width,'javascript':js,'touch':touch,
                        'font_px':font,'reduced_motion':motion,'forced_colors':forced,
                        'named_accessibility_tree_links':len(links),'horizontal_overflow':False,
                        'lcp_ms_local_fixture':round(max(perf['lcp']),1) if perf and perf['lcp'] else None,
                        'cls_observed_local_fixture':perf['cls'] if perf else None,'pass':True})
        ctx.close()
    ctx=browser.new_context(viewport={'width':390,'height':900})
    page=ctx.new_page();page.set_content(document(html_full,full_css))
    page.add_script_tag(content=script)
    page.get_by_role('button',name='Photographs').click()
    page.emulate_media(media='print')
    pdf=OUT/'full-custody-print.pdf';pdf.write_bytes(page.pdf(print_background=True,format='A4'))
    ctx.close();browser.close()
doc=fitz.open(pdf);text='\n'.join(pg.get_text() for pg in doc)
assert '102 deliberate ignitions' in text
assert 'Evidence boundary' in text
assert '2018 flammability-test history' in text
assert any('50-years-ago-apollo-flammability-tests' in (link.get('uri') or '') for pg in doc for link in pg.get_links())
report={'scope':'Real local Playwright Chromium with PHP-rendered content, NOT installed WP or axe-core/screen-reader, production CWV or hosted HTTP/CSP',
        'cases':results,'print':{'pages':len(doc),'nasa_link_annotation':True,'later_evidence_printed':True},'pass':True}
(OUT/'browser-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':len(results),'pdf_pages':len(doc),'measured_local_lcp_ms':[r['lcp_ms_local_fixture'] for r in results]},indent=2))
