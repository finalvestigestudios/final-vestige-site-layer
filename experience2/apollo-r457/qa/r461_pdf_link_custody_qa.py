#!/usr/bin/env python3
"""R461 read-only browser PDF QA: real clickable NASA citations after any filter.

Chrome page.set_content tests a local PHP rendering. It is not WordPress navigation,
axe-core accessibility acceptance, or field Web Vitals measurement.
"""
from __future__ import annotations
import hashlib
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'r461'
OUT.mkdir(parents=True,exist_ok=True)
HTML=subprocess.check_output(['php','-r',f'require {json.dumps(str(ROOT/"apollo_rights_gallery.php"))}; echo fv457_render();'],text=True)
DATA=subprocess.check_output(['php','-r',f'require {json.dumps(str(ROOT/"apollo_rights_gallery.php"))}; echo json_encode(fv457_records());'],text=True)
RECORDS=json.loads(DATA)
SOURCES={r['source_url'] for r in RECORDS}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
assert len(SOURCES)==6 and all(x.startswith(('https://www.nasa.gov/','https://images.nasa.gov/')) for x in SOURCES)
RESULTS=[]
FAIL=[]
SCREENSHOTS=[]

def check(name,cb):
    try:
        cb();RESULTS.append(name)
    except Exception as e:
        FAIL.append({'case':name,'error':repr(e)[:800]})

def pdf_assert(page,label):
    exported=page.pdf(format='A4',print_background=True,tagged=True)
    doc=fitz.open(stream=exported,filetype='pdf')
    links=[l.get('uri') for p in doc for l in p.get_links() if l.get('uri')]
    # Chromium annotates each wrapped line of a long link separately; validate unique targets, not rectangle count.
    counts=Counter(links)
    assert set(counts)==SOURCES|{FREE}, f'{label}: wrong or missing source URLs: {links}'
    assert counts[FREE]==1, f'{label}: unexpected free CTA link count'
    assert all(1 <= counts[u] <= 4 for u in SOURCES),f'{label}: unexpected PDF URL rectangle counts: {counts}'
    text=' '.join(p.get_text() for p in doc)
    assert text.count('Printable NASA source:')==6, f'{label}: missing readable source text in PDF'
    assert 'Source acceptance HOLD' in text, f'{label}: provenance disclaimer disappeared'
    assert 'not commercial media clearance' in text, f'{label}: print rights disclaimer disappeared'
    assert 'Image-use permission not established.' in text, f'{label}: per-card usage boundary missing'
    for id_ in ('S66-58038','S67-15717','S67-19766','S67-21294'):
        assert id_ in text, f'{label}: lost record identifier {id_}'
    doc.close()
    return exported

with sync_playwright() as play:
    browser=play.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        for javascript in (True,False):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=javascript)
            pg=ctx.new_page()
            pg.set_content(HTML,wait_until='load')
            label=f'{width}-js{int(javascript)}'
            def screen():
                assert pg.locator('[data-fv457-card]:visible').count()==6
                assert not pg.locator('.fv457__print-custody').first.is_visible()
                assert pg.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            check(label+'-screen-no-duplicates',screen)
            if javascript:
                pg.get_by_role('button',name='Confirmed homepage (1)').click()
                check(label+'-screen-filter',lambda: (_ for _ in ()).throw(AssertionError('filter failed')) if pg.locator('[data-fv457-card]:visible').count()!=1 else None)
            def export():
                data=pdf_assert(pg,label)
                if width in (320,390,768,1440,1920) and javascript:
                    target=OUT/f'{width}-filtered-tagged.pdf'
                    target.write_bytes(data)
            check(label+'-pdf-seven-clickable-urls',export)
            if width in (320,390,768,1440,1920) and javascript:
                pg.emulate_media(media='print')
                name=f'{width}-print.png'
                pg.screenshot(path=str(OUT/name),full_page=True,animations='disabled')
                SCREENSHOTS.append(name)
                pg.emulate_media(media='screen')
                check(label+'-screen-restored',lambda: (_ for _ in ()).throw(AssertionError('filter reset')) if pg.locator('[data-fv457-card]:visible').count()!=1 else None)
            ctx.close()
    for label,kwargs in [('touch',{'has_touch':True,'is_mobile':True}),('reduced-motion',{'reduced_motion':'reduce'}),('forced-colors',{'forced_colors':'active'})]:
        ctx=browser.new_context(viewport={'width':390,'height':844},**kwargs)
        pg=ctx.new_page();pg.set_content(HTML)
        if label=='touch':pg.get_by_role('button',name='Not in Atlas (3)').tap()
        else:pg.get_by_role('button',name='Not in Atlas (3)').click()
        check(label+'-pdf-seven-clickable-urls',lambda:pdf_assert(pg,label))
        ctx.close()
    browser.close()

file_hashes={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(OUT.iterdir()) if x.is_file() and x.suffix in ('.png','.pdf')}
report={'sprint':'R461','test_subject':'local PHP rendered document in real Chromium; PDF content and URI annotations examined via PyMuPDF','passed':len(RESULTS),'failed':FAIL,'cases':RESULTS,'screenshots':SCREENSHOTS,'artifact_sha256':file_hashes,
        'verified_unique_pdf_urls_per_export':7,'NASA_source_links_per_export':6,'commercial_ctas':0,
        'hosted_wordpress':'HOLD_NOT_RUN','axe_core':'HOLD_NOT_RUN (verified axe JS bundle unavailable in this environment)','navigated_lcp_cls':'HOLD_NOT_RUN (page.goto ERR_BLOCKED_BY_ADMINISTRATOR)','screen_reader_manual':'HOLD_NOT_RUN','field_cwv':'HOLD_NOT_RUN','revenue_and_asset_id':'UNVERIFIED'}
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps({'passed':len(RESULTS),'failed':FAIL,'screenshots':SCREENSHOTS,'pdf_count':len(list(OUT.glob('*.pdf')))},indent=2))
if FAIL:sys.exit(1)
