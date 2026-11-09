#!/usr/bin/env python3
"""R244 Apollo Research Desk printable custody regression, locally runnable.

Run in an actual source-controlled checkout:
  python qa/r244_print_custody.py --source experience2/research-desk --out /tmp/r244
The --fixture option is synthetic and MUST NOT be described as full source acceptance.
Requires php, playwright, PyMuPDF. No live network traffic or production writes.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from r243_core import SHIM

TEMPLATE_BLOB = '403d128c57b9bc82dac7c619651689070edef86c'
WIDTHS = (320, 390, 768, 1440, 1920)


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def fixture(root, print_css):
    (root/'templates').mkdir(); (root/'assets').mkdir()
    records = []
    for i in range(1, 7):
        records.append(f'''<article class="fv-ex2-ledger__card" id="fv-ex2-ledger-apollo1-record-{i:02d}" data-fvx-record data-fvx-search="source {i} oxygen record"><h2>Source record {i}</h2><p>Documented historical evidence. Distinct limitation {i}.</p><div class="fv-ex2-ledger__boundary"><strong>Evidence limitation</strong><p>This photo alone cannot prove a fire ignition source.</p></div><details class="fv-ex2-ledger__fulltext"><summary>Review the underlying finding</summary><p>Expanded contextual finding for record {i}, which must survive printing.</p></details><div class="fv-ex2-ledger__recordlinks"><a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">NASA record {i}</a></div></article>''')
    (root/'templates/ledger.html').write_text('''<section class="fv-ex2-ledger" data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title"><div class="fv-ex2-ledger__wrap"><h1 id="fv-ex2-ledger-apollo1-title">The proof and the gaps.</h1><div data-fvx-tools hidden><label for="fv-ex2-ledger-apollo1-search">Search evidence</label><input id="fv-ex2-ledger-apollo1-search" data-fvx-search aria-controls="fv-ex2-ledger-apollo1-grid"><span data-fvx-status></span></div><div class="fv-ex2-ledger__grid" id="fv-ex2-ledger-apollo1-grid">''' + ''.join(records) + '''</div><p data-fvx-empty hidden>No matching records</p><footer class="fv-ex2-ledger__footer"><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read original investigation</a></footer></div></section>''')
    (root/'assets/source-ledger.css').write_text(''' .fv-ex2-ledger{background:#090a0a;color:#f4efe6;line-height:1.6}.fv-ex2-ledger__grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.fv-ex2-ledger__card{background:#151611;color:#f4efe6;padding:18px}.fv-ex2-ledger [hidden]{display:none!important} ''' + print_css)
    (root/'assets/source-ledger.js').write_text('')


def render_php(root):
    (root/'shim.php').write_text(SHIM)
    proc = subprocess.run(['php', str(root/'shim.php'), 'late'], capture_output=True, text=True)
    if proc.returncode: raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)['first']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--fixture', action='store_true')
    args = parser.parse_args()
    out = args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    source = args.source.resolve()
    with tempfile.TemporaryDirectory(prefix='apollo-r244-') as d:
        root = Path(d)
        shutil.copy2(source/'final-vestige-ex2-research-desk.php', root/'final-vestige-ex2-research-desk.php')
        if args.fixture:
            fixture(root, (source/'assets/source-ledger.css').read_text() if (source/'assets/source-ledger.css').exists() else (source/'print_append.css').read_text())
        else:
            shutil.copytree(source/'templates',root/'templates')
            shutil.copytree(source/'assets',root/'assets')
            actual = git_blob((root/'templates/ledger.html').read_bytes())
            if actual != TEMPLATE_BLOB:
                raise RuntimeError(f'Protected Research Desk template changed: {actual} != {TEMPLATE_BLOB}')
        markup = render_php(root)
        soup = BeautifulSoup(markup,'html.parser')
        records = soup.select('[data-fvx-record]')
        if len(records) != 6: raise AssertionError('six source records must be visible in HTML')
        urls = sorted({a['href'] for a in soup.select('.fv-ex2-ledger__recordlinks a[href]')})
        if not urls or not all(u.startswith('https://www.nasa.gov/') for u in urls):
            raise AssertionError('external evidence sources changed')
        titles = [' '.join(h.stripped_strings) for h in soup.select('[data-fvx-record] h2')]
        src_js = (root/'assets/source-ledger.js').read_text()
        failures = []
        capture = {}
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,
                executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or None,
                args=['--no-sandbox','--disable-dev-shm-usage'])
            try:
                for width in WIDTHS:
                    for js in (False, True):
                        key = f'{width}-'+('js-filtered' if js else 'nojs')
                        ctx = browser.new_context(viewport={'width':width,'height':900}, java_script_enabled=js,
                            reduced_motion='reduce', is_mobile=width<=390, has_touch=width<=390)
                        page = ctx.new_page()
                        page.set_content('<!doctype html><html lang="en"><meta charset="utf-8"><body>'+markup+'</body></html>')
                        if js and src_js.strip():
                            page.add_script_tag(content=src_js)
                            field = page.locator('[data-fvx-search]')
                            if field.count():
                                field.fill('no-matching-source-9999')
                        if js:
                            # Force a hidden record even if this historical template has no filter control.
                            page.locator('[data-fvx-record]').first.evaluate('(e)=>e.hidden=true')
                        hidden_before = page.locator('[data-fvx-record][hidden]').count()
                        if js and hidden_before < 1: failures.append(key+': JS setup did not hide any records')
                        page.emulate_media(media='print')
                        details = page.locator('.fv-ex2-ledger__fulltext p')
                        visible = [details.nth(i).is_visible() for i in range(details.count())]
                        printed = page.locator('[data-fvx-record]').evaluate_all('els=>els.map(e=>({display:getComputedStyle(e).display, color:getComputedStyle(e).color}))')
                        if not all(x['display'] != 'none' for x in printed): failures.append(key+': filtered record omitted by print')
                        if not all(visible): failures.append(key+': closed details content omitted by print')
                        link_after = page.locator('.fv-ex2-ledger__recordlinks a').first.evaluate('(e)=>getComputedStyle(e,"::after").content')
                        if 'nasa.gov' not in link_after: failures.append(key+': printable evidence URL missing')
                        width_overflow = page.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth+1')
                        if width_overflow: failures.append(key+': horizontal overflow')
                        pdf = out / (key+'.pdf')
                        page.pdf(path=str(pdf),format='A4',print_background=False)
                        # Chromium embeds a wall-clock PDF CreationDate. Normalize this
                        # metadata before hashing so equivalent renders are byte stable.
                        original_doc = fitz.open(pdf)
                        metadata = dict(original_doc.metadata)
                        metadata['creationDate'] = 'D:20000101000000Z'
                        metadata['modDate'] = 'D:20000101000000Z'
                        original_doc.set_metadata(metadata)
                        normalized = out / (key+'.normalized.pdf')
                        original_doc.save(normalized, garbage=4, deflate=True, no_new_id=True)
                        original_doc.close()
                        normalized.replace(pdf)
                        text = ' '.join(' '.join(p.get_text().split()) for p in fitz.open(pdf))
                        if not all(t in text for t in titles): failures.append(key+': a title missing from PDF')
                        if text.count('nasa.gov') < 6: failures.append(key+': fewer than six printable NASA citations in PDF')
                        if 'underlying finding' not in text.lower(): failures.append(key+': expanded finding missing from PDF')
                        # Screenshots are print-media renderings, not substitutes for extracted PDF checks.
                        if width in (390,1440):
                            page.screenshot(path=str(out/(key+'.png')),full_page=True,animations='disabled')
                        capture[key] = {'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
                            'pdf_pages':len(fitz.open(pdf)), 'hidden_before':hidden_before,
                            'print_records_visible':len([v for v in printed if v['display']!='none']),
                            'print_details_visible':sum(visible), 'nasa_citation_text_hits':text.count('nasa.gov'),
                            'print_overflow':bool(width_overflow)}
                        ctx.close()
            finally: browser.close()
    receipt = {'status':'PASS' if not failures else 'FAIL','scope':'SYNTHETIC' if args.fixture else 'EXACT_TEMPLATE',
               'template_git_blob':None if args.fixture else TEMPLATE_BLOB,
               'cases':capture,'failures':failures,'browser_contexts':len(capture),
               'production_WP':False,'real_axe_core':False}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':receipt['status'],'scope':receipt['scope'], 'contexts':len(capture),'failures':failures}))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
