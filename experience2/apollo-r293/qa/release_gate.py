#!/usr/bin/env python3
"""R293 source-controlled PHP + offline Playwright gate (NOT installed WordPress/axe)."""
from pathlib import Path
from subprocess import run
from playwright.sync_api import sync_playwright
import sys, json, hashlib
ROOT=Path(__file__).resolve().parents[2]/'apollo-r281'
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r293-gate')
OUT.mkdir(parents=True,exist_ok=True)
php=ROOT/'apollo-source-experience.php'
css=(ROOT/'assets/apollo-source-experience.css').read_text()
checks=[]
for state in ('done','enqueued','registered','absent'):
    stub="""define('ABSPATH','/test/');function add_action($a,$b,$c=10){}function add_shortcode($a,$b){}function plugins_url($a,$b){return '/qa.css';}function wp_style_is($a,$state){return $state==='STATE';}require 'apollo-source-experience.php';echo fv_r281_render();echo fv_r281_render();""".replace('STATE',state)
    r=run(['php','-r',stub],cwd=ROOT,text=True,capture_output=True,check=True)
    links=r.stdout.count('<link rel="stylesheet"')
    assert links==(0 if state in ('done','enqueued') else 1),(state,links)
    checks.append({'state':state,'fallback_links':links,'result':'PASS'})
markup=r.stdout
html='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+markup+'</body></html>'
contexts=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        for js in (False,True):
            ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=width<=390)
            page=ctx.new_page();requests=[];page.on('request',lambda req:requests.append(req.url));page.set_content(html)
            ids=page.evaluate("()=>[...document.querySelectorAll('[id]')].map(e=>e.id)")
            assert len(ids)==len(set(ids))
            assert page.evaluate("()=>[...document.querySelectorAll('a[href^=\"#\"]')].every(a=>document.getElementById(a.hash.slice(1)))")
            assert not requests and page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert page.locator('.fv-r281__next a').count()==2
            for i in (1,2):
                link=page.locator(f'#fv-r281-{i}-event-1 .fv-r281__source-jump a');link.focus();link.press('Enter')
                assert page.evaluate('document.activeElement.id')==f'fv-r281-{i}-source-1'
            contexts.append({'width':width,'js':js,'pass':True});ctx.close()
    print_page=b.new_page(viewport={'width':390,'height':900})
    print_page.set_content(html)
    print_page.pdf(path=str(OUT/'r293-print-pagination.pdf'),print_background=True)
    b.close()
# Real Chromium PDF, not a CSS media-query existence assertion.
import fitz
pdf=fitz.open(str(OUT/'r293-print-pagination.pdf'))
first_page=pdf[0].get_text()
assert 'The pad test and fire' in first_page and 'Open NASA Apollo 1 mission history' in first_page, 'print orphaned the first evidence record'
print_pages=len(pdf)
pdf.close()
report={'php_states':checks,'browser_contexts':contexts,'browser_passes':len(contexts),
        'print_first_sheet_source':'PASS','printed_pages':print_pages,
        'php_sha256':hashlib.sha256(php.read_bytes()).hexdigest(),
        'css_sha256':hashlib.sha256(css.encode()).hexdigest(),
        'axe':'NOT_EXECUTED','http_csp':'BLOCKED_BY_ADMINISTRATOR',
        'installed_wordpress':'NOT_TESTED','field_lcp_cls':'NOT_MEASURED','release':'HARD_HOLD'}
(OUT/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print('R293 source-controlled: WordPress state 4/4; Chromium 10/10 PASS; release HARD HOLD')
