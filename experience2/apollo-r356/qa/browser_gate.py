#!/usr/bin/env python3
"""Real Chromium fixture QA of R356 demand-scoped note/composite; not installed WordPress."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
ROOT=Path(__file__).resolve().parents[3]
EX=ROOT/'experience2'
OUT=EX/'apollo-r356/QA'
OUT.mkdir(parents=True,exist_ok=True)
BRIDGE=EX/'apollo-r356/asset-bridge.php'
def render(method):
    code='define("ABSPATH", true); require '+json.dumps(str(BRIDGE))+'; echo '+method+'();'
    return subprocess.check_output(['php','-r',code],text=True)
html_note=render('fv_apollo_r356_postfire')
html_full=render('fv_apollo_r356_experience')
styles_note=(EX/'apollo-r355/postfire-ledger.css').read_text()+'\n'+(EX/'apollo-r356/assets/print-proof.css').read_text()
full_css='\n'.join((EX/x).read_text() for x in (
'apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css',
'apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css',
'apollo-r348/assets/source-custody.css','apollo-r355/postfire-ledger.css','apollo-r356/assets/print-proof.css'))
js=(EX/'apollo-r347/assets/source-index.js').read_text()
def document(content,css):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+css+'</style></head><body>'+content+'</body></html>'
cases=[('note-320-nojs','note',320,False,False,16,'reduce','none'),
 ('note-390-keyboard','note',390,True,False,16,'no-preference','none'),
 ('note-768-touch','note',768,True,True,16,'reduce','none'),
 ('full-320-root64','full',320,True,False,64,'reduce','none'),
 ('full-1440-keyboard','full',1440,True,False,16,'no-preference','none'),
 ('full-1920-forced','full',1920,True,False,16,'reduce','active')]
reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for label,kind,width,enabled,touch,font,motion,forced in cases:
    ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,
          has_touch=touch,reduced_motion=motion,forced_colors=forced)
    page=ctx.new_page()
    page.set_content(document(html_note if kind=='note' else html_full,styles_note if kind=='note' else full_css),wait_until='load')
    if enabled:
      page.evaluate('''() => {window.__perf={lcp:[],cls:0};try{new PerformanceObserver(list=>list.getEntries().forEach(e=>window.__perf.lcp.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true})}catch(e){};try{new PerformanceObserver(list=>list.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__perf.cls+=e.value})).observe({type:'layout-shift',buffered:true})}catch(e){}}''')
      if kind=='full':page.add_script_tag(content=js)
    if font != 16:page.evaluate('(x)=>document.documentElement.style.fontSize=x+"px"',font)
    assert page.locator('[data-fv-apollo-postfire]').count()==1,label
    assert page.locator('[data-fv-r355-reviewed-source]').count()==1,label
    assert page.locator('img').count()==0,label
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),label
    ids=page.eval_on_selector_all('[id]','nodes=>nodes.map(n=>n.id)')
    assert len(ids)==len(set(ids)),label
    details=page.locator('.fv-apollo-r355__source summary');details.focus();page.keyboard.press('Enter')
    assert details.evaluate('(el)=>el.parentNode.open'),label
    assert page.get_by_role('link',name='Read NASA\'s 2018 flammability-test history').count()==1,label
    if kind=='note':
      assert page.locator('[data-fv-apollo-entry]').count()==0,label
      assert page.locator('[data-fv-apollo-filters]').count()==0,label
      assert page.locator('[data-fv-r339-cta="editorial"]').count()==0,label
    else:
      assert page.locator('[data-fv-apollo-entry]:visible').count()==13,label
      assert page.locator('[data-fv-r339-cta="editorial"]').count()==1,label
      if enabled:
        filters=page.locator('[data-fv-apollo-filters] button');assert filters.count()==5,label
        filters.nth(1).click();assert page.locator('[data-fv-apollo-entry]:visible').count()==3,label
        filters.nth(0).click();assert page.locator('[data-fv-apollo-entry]:visible').count()==13,label
      else:assert page.locator('[data-fv-apollo-filters]:visible').count()==0,label
    page.screenshot(path=str(OUT/(label+'.png')),full_page=False)
    page.wait_for_timeout(140)
    perf=page.evaluate('window.__perf||null') if enabled else None
    reports.append({'case':label,'width':width,'mode':kind,'js':enabled,'touch':touch,'root_font_px':font,
       'reduced_motion':motion,'forced_colors':forced,'keyboard_details':True,'no_horizontal_overflow':True,
       'source_named':True,'duplicate_dom_ids':0,'local_fixture_lcp_ms':round(max(perf['lcp']),1) if perf and perf['lcp'] else None,
       'local_fixture_cls':perf['cls'] if perf else None,'pass':True})
    ctx.close()
 ctx=browser.new_context(viewport={'width':390,'height':900})
 page=ctx.new_page();page.set_content(document(html_note,styles_note));page.locator('summary').click()
 pdf=OUT/'note-source-custody.pdf';pdf.write_bytes(page.pdf(print_background=True,format='A4'))
 ctx.close();browser.close()
doc=fitz.open(pdf);text='\n'.join(x.get_text() for x in doc)
assert '102 deliberate ignitions' in text and 'February 14, 2018' in text
assert any('50-years-ago-apollo-flammability-tests' in (a.get('uri') or '') for page in doc for a in page.get_links())
report={'scope':'PHP-rendered local fixture, actual Chromium; not axe-core, installed WordPress, screen readers, production CWV, or HTTP/CSP',
'cases':reports,'print':{'pages':len(doc),'approved_source_annotation':True},'pass':True}
(OUT/'browser-qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'cases_passed':len(reports),'pdf_pages':len(doc),'mode_counts':{'note':3,'full':3},'lcp_ms':[x['local_fixture_lcp_ms'] for x in reports]},indent=2))
