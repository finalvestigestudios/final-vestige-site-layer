#!/usr/bin/env python3
"""Actual Chromium/CDP accessibility-tree fixture QA; no real WP, axe, HTTP or production CWV."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
ROOT=Path(__file__).resolve().parents[3]; EX=ROOT/'experience2'
OUT=EX/'apollo-r360/QA';OUT.mkdir(parents=True,exist_ok=True)
BRIDGE=EX/'apollo-r360/rights-audit.php'
code='define("ABSPATH",true); require '+json.dumps(str(BRIDGE))+'; echo fv_apollo_r360_rights_audit_shortcode();'
html=subprocess.check_output(['php','-r',code],text=True)
css=(EX/'apollo-r360/assets/rights-audit.css').read_text()
assert html.count('data-fv-rights-reviewed-link')==9
assert html.count('data-fv-commercial-clearance="not-cleared"')==9
assert '<img' not in html and '<script' not in html
cases=[('320-nojs',320,False,16,'reduce','none',False),('320-400pct',320,True,64,'reduce','none',False),('390-keyboard',390,True,16,'no-preference','none',False),('768-touch',768,True,16,'reduce','none',True),('1440-desktop',1440,True,16,'no-preference','none',False),('1920-forced',1920,True,16,'reduce','active',False)]
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for label,width,js,font,motion,forced,touch in cases:
        ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=touch,reduced_motion=motion,forced_colors=forced)
        page=ctx.new_page()
        page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
        if font!=16:page.evaluate('(px)=>document.documentElement.style.fontSize=px+"px"',font)
        assert page.locator('[data-fv-rights-annex]').count()==1,label
        assert page.locator('[data-fv-rights-reviewed-link]').count()==9,label
        assert page.locator('[data-fv-commercial-clearance="not-cleared"]').count()==9,label
        assert page.locator('img,iframe,form,button').count()==0,label
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth+1'),label
        links=page.locator('a[data-fv-rights-reviewed-link]')
        assert links.count()==9 and all('nasa.gov' in (x.get_attribute('href') or '') for x in links.all()),label
        links.first.focus();assert links.first.evaluate('e=>document.activeElement===e'),label
        assert page.evaluate("getComputedStyle(document.querySelector('.fv-apollo-r360')).color")!= 'rgba(0, 0, 0, 0)',label
        ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        named=[n for n in ax if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
        assert len(named)==9 and len(set(n.get('name',{}).get('value') for n in named))==9,label
        page.screenshot(path=str(OUT/(label+'.png')),full_page=False)
        results.append({'case':label,'width_px':width,'javascript':js,'font_px':font,'touch':touch,'motion':motion,'forced_colors':forced,'source_links_with_distinct_accessible_names':len(named),'horizontal_overflow':False,'pass':True})
        ctx.close()
    ctx=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
    page=ctx.new_page();page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+html+'</body></html>');page.emulate_media(media='print')
    pdf=OUT/'r360-rights-print.pdf';pdf.write_bytes(page.pdf(format='A4',print_background=True))
    ctx.close();browser.close()
print_doc=fitz.open(pdf)
print_text='\n'.join(x.get_text() for x in print_doc)
assert 'NOT CLEARED' in print_text and '2018 NASA flammability retrospective' in print_text
assert len(set(l.get('uri') for pg in print_doc for l in pg.get_links() if 'nasa.gov' in (l.get('uri') or '')))==9
report={'pass':True,'chromium_cases':results,'print_pdf_pages':len(print_doc),'pdf_nasa_unique_source_destinations':9,'limitations':['Real Chromium via page.set_content: no installed WP/Assembler','Browser navigation to localhost, data and file URLs denied ERR_BLOCKED_BY_ADMINISTRATOR; HTTP/CSP remains blocked','No genuine axe-core, NVDA/VoiceOver, Firefox/WebKit','No production LCP/CLS or live conversions measured']}
(OUT/'r360-browser.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed_browser_cases':len(results),'print_pdf_pages':len(print_doc),'source_annotations':9,'status':'LOCAL ONLY'},indent=2))
