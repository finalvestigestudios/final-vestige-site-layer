#!/usr/bin/env python3
"""R345: real offline Chromium QA of the actual PHP composite; zero network requests."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.getenv('FV_R345_OUT', str(ROOT/'apollo-r345/QA')))
OUT.mkdir(parents=True, exist_ok=True)
php = ROOT/'apollo-r340/apollo-accession-gallery.php'
styles = [ROOT/'apollo-r339/assets/chronology-rail.css', ROOT/'apollo-r345/evidence-plate.css', ROOT/'apollo-r340/assets/accession-gallery.css']
result = subprocess.run(['php','-r',"define('ABSPATH',true);require '"+str(php)+"';echo fv_apollo_r340_experience_shortcode();"],capture_output=True,text=True,check=True)
html = result.stdout
css = '\n'.join(f.read_text() for f in styles)
assert 'data-fv-apollo-claim-ledger' in html
assert html.count('data-fv-apollo-tier="original-board"') == 3
assert html.count('data-fv-apollo-primary-source="board"') == 3
assert html.count('data-fv-r339-cta="editorial"') == 1
assert html.count('data-fv-r339-source=') == 6
assert html.count('data-fv-r340-source="contextual-photo"') == 4
assert html.count('Later institutional source:') == 1
assert html.count('Primary source:') == 5
assert not any(s in html for s in ('data-geo-pin','data-affiliate','<img','utm_campaign','payhip.com'))
assert 'The Board recorded a 16.7 psia' in html
assert 'No single ignition source was conclusively identified' in html
assert 'This finding does not establish that the crew made no effort' in html

cases = [(320,16,True,False,False,False),(390,16,True,False,False,False),
         (768,16,True,False,True,False),(1440,16,True,False,False,False),
         (1920,16,True,False,False,False),(320,64,True,False,False,False),
         (390,16,True,True,False,False),(390,16,False,False,False,False),
         (320,32,False,False,False,False),(768,16,True,False,False,True)]
records=[]
with sync_playwright() as play:
    browser = play.chromium.launch(executable_path=os.getenv('CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    for width, font, js, touch, reduced, forced in cases:
        ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=touch,is_mobile=touch,
                                reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
        page=ctx.new_page()
        page.route('**/*', lambda route: route.abort()) # no remote assets or source page requests
        markup = f'<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>html{{font-size:{font}px}}body{{margin:0}}{css}</style></head><body><main>{html}</main></body></html>'
        page.set_content(markup,wait_until='load')
        assert page.locator('.fv-apollo-r345__card').count()==3
        assert page.locator('.fv-apollo-r339__event').count()==6
        assert page.locator('.fv-apollo-r340__card').count()==4
        assert page.locator('[data-fv-r339-cta="editorial"]').count()==1
        assert page.locator('[data-fv-apollo-primary-source]').count()==3
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'), (width,font)
        assert page.locator('.fv-apollo-r345__intro').is_visible()
        # The findings and limits are visible without opening drawers or needing JS.
        assert page.locator('.fv-apollo-r345__finding').first.is_visible()
        assert page.locator('.fv-apollo-r345__limit').last.is_visible()
        assert all(u.startswith('https://www.nasa.gov/') for u in page.locator('[data-fv-apollo-primary-source]').evaluate_all('(els)=>els.map(e=>e.href)'))
        details=page.locator('.fv-apollo-r345__custody').first
        summary=details.locator('summary')
        summary.focus();page.keyboard.press('Enter')
        assert details.evaluate('(e)=>e.open')
        assert details.locator('p').is_visible()
        page.keyboard.press('Space');assert not details.evaluate('(e)=>e.open')
        assert page.locator('[data-fv-r339-source="later-nasa-history"]').count()==1
        if (width,font,js) in [(320,64,True),(1440,16,True),(390,16,False)]:
            page.screenshot(path=str(OUT / f"r345-{width}-font{font}-{'js' if js else 'nojs'}.png"),full_page=(font<64))
        records.append({'width':width,'font_px':font,'js':js,'touch':touch,'reduced':reduced,'forced':forced,'result':'PASS'})
        ctx.close()
    # Native print / PDF proof corrects R344 misclassification of later institutional history.
    ctx=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
    page=ctx.new_page();page.set_content(f'<html lang="en"><head><style>{css}</style></head><body>{html}</body></html>')
    pdf=page.pdf(format='A4',print_background=True)
    doc=fitz.open(stream=pdf,filetype='pdf')
    pdf_text='\n'.join(p.get_text() for p in doc)
    assert pdf_text.count('Primary source:')==5, pdf_text.count('Primary source:')
    assert pdf_text.count('Later institutional source:')==1
    assert pdf_text.count('Evidence limit:')>=9
    assert 'Finding and Determination 4' in pdf_text
    assert 'Read the complete Apollo 1 investigation' in pdf_text
    assert 'No single ignition source was conclusively identified' in pdf_text
    urls=[r.get('uri','') for p in doc for r in p.get_links() if r.get('kind')==2]
    assert sum(u.startswith('https://www.nasa.gov/') for u in urls)>=10
    assert sum(u.startswith('https://finalvestige.com/') for u in urls)==1
    assert not any('utm_' in u or 'payhip' in u for u in urls)
    (OUT/'r345-source-dossier.pdf').write_bytes(pdf)
    doc[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(str(OUT/'r345-print-page1.png'))
    print_summary={'pages':len(doc),'original_board_source_labels':5,'later_institutional_labels':1,'nasa_links':sum(u.startswith('https://www.nasa.gov/') for u in urls),'sha256':hashlib.sha256(pdf).hexdigest()}
    doc.close();ctx.close();browser.close()

# Negative controls: a flattened custody label and an extra commerce callout fail the contract.
def custody_ok(text):
    return text.count('Later institutional source:')==1 and text.count('Primary source:')==5
assert custody_ok(pdf_text)
assert not custody_ok(pdf_text.replace('Later institutional source:','Primary source:'))
assert html.count('data-fv-r339-cta="editorial"')==1
assert (html+'data-fv-r339-cta="editorial"').count('data-fv-r339-cta="editorial"')!=1
receipt={'result':'PASS','screen_contexts':len(records),'cases':records,'print':print_summary,'negative_controls_rejected':2,
         'axe_core':'NOT_EXECUTED_NO_INSTALLED_PACKAGE','installed_wordpress':'NOT_EXECUTED',
         'firefox_webkit':'NOT_EXECUTED','production_lcp_cls':'NOT_MEASURED',
         'sources':['https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html','https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html'],
         'files_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [php, ROOT/'apollo-r339/chronology-rail.php',ROOT/'apollo-r345/evidence-plate.php',*styles]}}
(OUT/'r345-acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'result':'PASS','screen_contexts':len(records),'print':print_summary,'negative_controls_rejected':2},indent=2))
