#!/usr/bin/env python3
"""Exact R238 PHP-source, R253+R254 overlay browser gate. No HTTP, WordPress, or axe claims."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz

MANIFEST = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
CTA = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SELECTORS = (
    '.notice > a', '.fv-apollo-method dd a', '.fv-apollo-trace-rights a',
    '.fv-apollo-custody-rights a', '.fv-apollo-lesson-grid a', '.fv-apollo-citation-route a',
    '.fv-apollo-confidence-answer a', '.fv-apollo-rail-reading-key a'
)
SELECT = ', '.join('.fv-apollo-atlas ' + s + '[href^="https://www.nasa.gov/"]' for s in SELECTORS)
ALL = '.fv-apollo-atlas a[href^="https://www.nasa.gov/"]'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def sizes(page, selector):
    return page.locator(selector).evaluate_all('''elements=>elements.map(a=>({
        text:a.textContent.trim().slice(0,85), href:a.href,
        h:Math.round(a.getBoundingClientRect().height*100)/100,
        w:Math.round(a.getBoundingClientRect().width*100)/100,
        visible:!!(a.offsetWidth||a.offsetHeight||a.getClientRects().length)
    }))''')

def main():
    ar=argparse.ArgumentParser()
    ar.add_argument('--atlas',required=True,type=Path)
    ar.add_argument('--r253',required=True,type=Path)
    ar.add_argument('--r254',required=True,type=Path)
    ar.add_argument('--out',required=True,type=Path)
    a=ar.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    m=(a.atlas/'manifest.json').read_bytes()
    assert digest(m)==MANIFEST, 'sealed R238 manifest changed'
    for name, expected in json.loads(m)['files'].items():
        assert digest((a.atlas/name).read_bytes())==expected, 'sealed source drift '+name
    php=subprocess.run(['php',str(a.atlas/'wp-render-shim-r224.php'),
         str((a.atlas/'fv-ex2-apollo-r224.php').resolve()),'normal'],capture_output=True,text=True,check=True)
    html=json.loads(php.stdout)['html']
    assert html==(a.atlas/'templates/atlas-fragment.html').read_text(), 'PHP output drift'
    base=(a.atlas/'assets/atlas-scoped.css').read_text()
    r253=a.r253.read_text();r254=a.r254.read_text()
    assert 'min-height: 44px' in r253 and 'min-height: 44px' in r254
    assert '@media print' in r254 and '@media (forced-colors: active)' in r254
    def document(extra):
        return ('<!doctype html><html lang="en"><head><meta name="viewport" '
                'content="width=device-width,initial-scale=1"><style>'+base+'\n'+r253+'\n'+extra+
                '</style></head><body>'+html+'</body></html>')
    records=[];shots=[]; print_out=[]; before_baseline=None
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for js in (True,False):
                context=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390,
                    reduced_motion='reduce' if not js else 'no-preference')
                page=context.new_page();unexpected=[]
                page.on('request',lambda request:unexpected.append(request.url))
                page.set_content(document(''))
                page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
                before=[x for x in sizes(page,SELECT) if x['visible']]
                under=[x for x in before if x['h']<43.99]
                assert len(under)>=3, f'expected original touch gap disappeared: {under}'
                page.set_content(document(r254))
                page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
                after=[x for x in sizes(page,ALL) if x['visible']]
                fixed=[x for x in sizes(page,SELECT) if x['visible']]
                assert len(after)>=40 and len(fixed)>=7
                assert all(x['h']>=43.99 and x['w']>0 for x in after), f'NASA target below 44px: {[(x["text"],x["h"]) for x in after if x["h"]<43.99]}'
                assert all(x['href'].startswith('https://www.nasa.gov/') for x in after)
                assert page.locator('a.cta').count()==1 and page.locator('a.cta').get_attribute('href')==CTA
                assert page.locator('a[href*="payhip.com"],a[href*="awin1.com"]').count()==0
                assert page.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
                assert page.locator('#fv-apollo-source-drawer summary').count()==1
                summary=page.locator('#fv-apollo-source-drawer summary')
                summary.focus();summary.press('Enter')
                assert not page.locator('#fv-apollo-source-drawer').evaluate('(x)=>x.open')
                summary.press('Space')
                assert page.locator('#fv-apollo-source-drawer').evaluate('(x)=>x.open')
                link=page.locator('.fv-apollo-atlas .notice > a[href^="https://www.nasa.gov/"]')
                link.focus();assert link.evaluate('(e)=>document.activeElement===e')
                if js:
                    page.evaluate('''()=>{window._r254=0;for(const e of document.querySelectorAll('.fv-apollo-atlas a'))
                        e.addEventListener('click',ev=>{if(e.href.includes('nasa.gov'))
                        {ev.preventDefault();window._r254++}})}''')
                    if width<=390:link.tap()
                    else:link.press('Enter')
                    assert page.evaluate('window._r254')==1
                assert unexpected==[], 'unapproved network dependency'
                if width in (390,1440):
                    page.evaluate('''()=>{document.activeElement?.blur();window.scrollTo(0,0)}''')
                    file=a.out/f'{width}-{"js" if js else "nojs"}.png'
                    page.screenshot(path=str(file),full_page=True,animations='disabled')
                    shots.append({'path':file.name,'sha256':digest(file.read_bytes())})
                if (width,js) in ((390,True),(1440,False)):
                    page.emulate_media(media='print')
                    raw_pdf=page.pdf(print_background=True)
                    with fitz.open(stream=raw_pdf,filetype='pdf') as rendered:
                        text='\n'.join(p.get_text() for p in rendered)
                        assert text.count('nasa.gov')>=8, 'lost printable source bibliography'
                        pages=len(rendered)
                        rendered.set_metadata({'title':'Apollo R254 archival acceptance',
                            'creator':'FV Apollo staged QA','producer':'PyMuPDF',
                            'creationDate':'D:20200101000000Z','modDate':'D:20200101000000Z'})
                        pdf=rendered.tobytes(garbage=4,deflate=True,no_new_id=True)
                    file=a.out/f'{width}-source-print.pdf';file.write_bytes(pdf)
                    print_out.append({'path':file.name,'bytes':len(pdf),'sha256':digest(pdf),
                        'pages':pages,'nasa_url_occurrences':text.count('nasa.gov')})
                records.append({'width':width,'js':js,'prior_small_links':len(under),
                    'visible_verified_nasa_links':len(after),'minimum_after_px':min(x['h'] for x in after),
                    'horizontal_overflow_px':max(0,page.evaluate('document.documentElement.scrollWidth-innerWidth'))})
                context.close()
        # Mutant style demonstrates the gate is sensitive to a missing fix.
        c=browser.new_context(viewport={'width':390,'height':900});page=c.new_page()
        page.set_content(document(r254.replace('min-height: 44px','min-height: 0')))
        page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
        assert any(x['h']<44 for x in sizes(page,SELECT) if x['visible']), 'negative control ineffective'
        c.close();browser.close()
    receipt={'status':'PASS','release':'STAGING_HOLD','original_manifest_sha256':MANIFEST,
        'r253_sha256':digest(a.r253.read_bytes()),'r254_sha256':digest(a.r254.read_bytes()),
        'contexts':len(records),'rows':records,'screenshots':shots,'print_files':print_out,
        'negative_control':'PASS','axe':'NOT_RUN','installed_wordpress':'NOT_RUN',
        'http_csp':'NOT_RUN','field_cwv':'NOT_RUN','realized_net_revenue':'NOT_COMPUTABLE'}
    (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(records),
        'previous_small_targets':max(r['prior_small_links'] for r in records),
        'minimum_after_px':min(r['minimum_after_px'] for r in records),
        'screenshots':len(shots),'print_files':len(print_out)},sort_keys=True))

if __name__=='__main__':main()
