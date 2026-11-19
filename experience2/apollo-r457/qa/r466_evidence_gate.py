"""Reproducible local EvidencePlate contract checks. NOT a hosted WordPress/axe/CWV test."""
import json
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright
import fitz

ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'apollo_rights_gallery.php'
def rendered(code):
    p=subprocess.run(['php','-r',f'require {json.dumps(str(PHP))};{code}'],check=True,capture_output=True,text=True)
    return p.stdout
assert rendered('echo fv457_evidence_plates_valid(fv457_evidence_plates())?"yes":"no";')=='yes'
for mutation in ['$p[0]["source"]="https://attacker.test/";', '$p[1]["date"]="2017-01-27";', '$p[2]["id"]="cause";']:
    assert rendered(f'$p=fv457_evidence_plates();{mutation}echo fv457_evidence_plates_valid($p)?"no":"yes";')=='yes'
html='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+rendered('echo fv457_render();')+'</body></html>'
counts={'php_adversarial':4,'browser':0,'pdf':0}
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,360,390,768,1024,1440,1920):
        for js in (False,True):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
            page=ctx.new_page();page.set_content(html)
            assert page.locator('[data-fv457-plate]').count()==3
            assert page.locator('.fv457__evidence-plate details').count()==3
            assert page.locator('.fv457__cta a').count()==1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            page.locator('.fv457__evidence-plate summary').first.focus();page.keyboard.press('Enter')
            assert page.locator('.fv457__evidence-plate details').first.get_attribute('open') is not None
            assert page.locator('.fv457__evidence-plate details a').first.is_visible()
            if js:
                page.get_by_role('button',name='NASA ID confirmed (4)').click()
                assert page.locator('[data-fv457-card]:visible').count()==4
                assert page.locator('[data-fv457-plate]:visible').count()==3
            else:assert page.locator('[data-fv457-card]:visible').count()==6
            counts['browser']+=8 if js else 7
            if width==390 and js:
                page.emulate_media(media='print')
                assert page.locator('.fv457__evidence-print:visible').count()==3
                assert page.locator('[data-fv457-card]:visible').count()==6
                doc=fitz.open(stream=page.pdf(print_background=True),filetype='pdf')
                urls={link['uri'] for sheet in doc for link in sheet.get_links() if link.get('uri')}
                assert len(urls)==10 and sum('nasa.gov' in u for u in urls)==9
                counts['pdf']+=3
            ctx.close()
    browser.close()
print(json.dumps({'status':'PASS','checks':sum(counts.values()),'groups':counts,'browser':'real Chromium set_content PHP markup','hosted':'NOT RUN','axe':'NOT RUN','navigated_LCP_CLS':'NOT RUN'},sort_keys=True))
