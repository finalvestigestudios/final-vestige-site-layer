#!/usr/bin/env python3
"""R470 isolated optional-asset integrity quarantine and source-custody browser gate.
This executes genuine local Chromium via set_content (NOT hosted navigation, axe, or CWV).
Each tamper fixture is copied to a temporary directory; the working tree is never mutated.
"""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'QA' / 'r470'
OUT.mkdir(parents=True, exist_ok=True)
MODES = ('clean','missing_css','missing_js','missing_both','tampered_css','tampered_js','tampered_both')
WIDTHS = (320,390,768,1440,1920)
JS_MODES = (False, True)
HELD = 'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
results = {'method':'real Playwright Chromium with set_content of locally rendered PHP (NOT navigated WP staging)',
           'axe_core':'HOLD_NOT_RUN: no verified pinned axe-core bundle',
           'navigated_lcp_cls':'HOLD_NOT_RUN: administrator blocks browser navigation, including localhost',
           'modes':{},'cases':[]}

def generate(mode):
    with tempfile.TemporaryDirectory(prefix='apollo-r470-') as t:
        base=Path(t)
        (base/'assets').mkdir()
        for src in ('apollo_rights_gallery.php','evidence_plates.php'):
            shutil.copyfile(ROOT/src,base/src)
        for src in ('gallery.css','gallery.js'):
            shutil.copyfile(ROOT/'assets'/src,base/'assets'/src)
        if mode in ('missing_css','missing_both'):(base/'assets/gallery.css').unlink()
        if mode in ('missing_js','missing_both'):(base/'assets/gallery.js').unlink()
        if mode in ('tampered_css','tampered_both'):
            with (base/'assets/gallery.css').open('a') as f:f.write('\nhtml{display:none!important}/* QUARANTINE_CSS_SENTINEL */\n')
        if mode in ('tampered_js','tampered_both'):
            with (base/'assets/gallery.js').open('a') as f:f.write('\nwindow.__r470_tampered_script_ran=true;/* QUARANTINE_JS_SENTINEL */\n')
        cmd=['php','-r',f'require {json.dumps(str(base/"apollo_rights_gallery.php"))};echo fv457_render();']
        return subprocess.check_output(cmd,text=True)

fixtures={m:generate(m) for m in MODES}
for mode, markup in fixtures.items():
    bad_css=mode in ('tampered_css','tampered_both')
    bad_js=mode in ('tampered_js','tampered_both')
    expect_style=mode not in ('missing_css','missing_both','tampered_css','tampered_both')
    expect_script=mode in ('clean','missing_css','tampered_css') and expect_style
    assert ('<style>' in markup)==expect_style,mode
    assert ('<script>' in markup)==expect_script,mode
    assert ('Archive enhancement quarantined:' in markup)==(bad_css or bad_js),mode
    assert 'QUARANTINE_CSS_SENTINEL' not in markup and 'QUARANTINE_JS_SENTINEL' not in markup
    assert markup.count('data-fv457-card=')==6,mode
    assert 'UNVERIFIED CATALOGUE LINK WITHHELD.' in markup,mode
    assert f'href="{HELD}"' not in markup,mode
    assert f'href="{FREE}"' in markup,mode
    assert '<details>' in markup and 'Apollo 204 Review Board' in markup,mode
    results['modes'][mode]={'styles_embedded':expect_style,'script_embedded':expect_script,'quarantine':bool(bad_css or bad_js)}

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-background-networking'])
    for mode in MODES:
        html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="margin:0">'+fixtures[mode]+'</body></html>'
        for width in WIDTHS:
            for js in JS_MODES:
                context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=width==390,reduced_motion='reduce',forced_colors='active' if width==768 else 'none')
                page=context.new_page()
                errors=[]
                page.on('pageerror',lambda e: errors.append(str(e)))
                page.set_content(html,wait_until='domcontentloaded')
                assert not errors,(mode,width,js,errors)
                assert page.locator('[data-fv457-card]').count()==6,(mode,width,js)
                assert page.locator('[data-fv457-plate]').count()==3,(mode,width,js)
                assert page.locator('.fv457__moment').count()==3,(mode,width,js)
                assert page.locator('.fv457__cta a').count()==1,(mode,width,js)
                assert page.locator(f'a[href="{HELD}"]').count()==0,(mode,width,js)
                assert not page.evaluate('Boolean(window.__r470_tampered_script_ran)'),mode
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(mode,width,js,page.evaluate('document.documentElement.scrollWidth'))
                assert page.get_by_text('UNVERIFIED CATALOGUE LINK WITHHELD.').count()==1
                active=mode=='clean' and js
                assert page.locator('[data-fv457-controls]').is_visible()==active,(mode,width,js)
                if active:
                    select=page.get_by_role('button',name='NASA ID confirmed (4)')
                    if width==390:select.tap()
                    else:select.click()
                    assert page.locator('[data-fv457-card]:visible').count()==4
                    page.get_by_role('button',name='All six').focus()
                    page.keyboard.press('Enter')
                    assert page.locator('[data-fv457-card]:visible').count()==6
                else:
                    assert page.locator('[data-fv457-card]:visible').count()==6,(mode,width,js)
                # Native details are keyboard-operable even when both optional assets are altered.
                if width==390 and js and mode in ('tampered_both','missing_both','tampered_js'):
                    details=page.locator('.fv457__card details').first
                    details.locator('summary').focus()
                    page.keyboard.press('Enter')
                    assert details.get_attribute('open') is not None,(mode,width)
                if width in (390,1440) and js and mode in ('clean','tampered_css','tampered_js','tampered_both'):
                    page.evaluate('document.activeElement instanceof HTMLElement && document.activeElement.blur();window.scrollTo(0,0)')
                    page.screenshot(path=str(OUT/f'{mode}-{width}.png'),full_page=True,animations='disabled')
                if mode=='tampered_both' and width==390 and js:
                    page.emulate_media(media='print')
                    pdf=OUT/'tampered-both-source-custody.pdf'
                    pdf.write_bytes(page.pdf(print_background=True,format='A4'))
                    raw=fitz.open(pdf)
                    md=raw.metadata
                    md.update({'title':'FV Apollo R470 safe source copy','creationDate':"D:20261118000000+00'00'",'modDate':"D:20261118000000+00'00'"})
                    raw.set_metadata(md)
                    tmp=OUT/'tmp.pdf';raw.save(tmp,garbage=4,deflate=True,no_new_id=1)
                    raw.close();tmp.replace(pdf)
                    doc=fitz.open(pdf)
                    urls={l.get('uri','') for pg in doc for l in pg.get_links() if l.get('kind')==fitz.LINK_URI}
                    nasa={x for x in urls if 'nasa.gov' in x}
                    assert len(nasa)==8,(mode,sorted(nasa))
                    assert HELD not in urls and FREE in urls
                    text=' '.join((' '.join(pg.get_text() for pg in doc)).split())
                    assert 'Archive enhancement quarantined:' in text and 'UNVERIFIED CATALOGUE' in text and 'LINK WITHHELD.' in text
                    results['pdf']={'nasa_url_count':len(nasa),'held_url_unlinked':True,'free_cta':FREE in urls,'pages':doc.page_count}
                    doc.close()
                results['cases'].append({'mode':mode,'width':width,'js':js,'result':'PASS'})
                context.close()
    browser.close()
results['screenshot_sha256']={file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(OUT.glob('*.png'))}
(OUT/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
print(f"PASS R470: {len(results['cases'])} Chromium contexts; 7 clean/missing/tampered asset conditions; 8 NASA PDF links and 1 free CTA")
