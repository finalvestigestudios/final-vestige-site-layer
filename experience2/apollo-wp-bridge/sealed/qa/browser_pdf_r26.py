#!/usr/bin/env python3
"""R26 actual Chromium PDF output/record integrity QA, seven widths, no JS.

Read-only private PHP-stub HTML, **not** a real installed WordPress page,
HTTP CSP/cookies, a screen-reader/axe audit, or field CWV measurements.
Chromium PDFs are per-run evidence, NOT expected byte-identical across runs
because Chromium injects metadata; deterministic source builds are separate.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from browser_exact import get_fixture
from print_source_transcript_r25 import CASEFILE, GENERATED, CASEFILE_PIN, NASA_POLICY, REPORT as NASA_REPORT
WIDTHS=(320,360,390,768,1024,1440,1920)
OUT=HERE/'r26-pdf-evidence'
REPORT=HERE/'R26_REAL_PDF_RESULTS.json'

def cmd(*args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=30).stdout.decode('utf-8',errors='replace')

def verify_pdf_semantics(info: str, urls: str, expected_nasa: list[str]) -> dict:
    """Fail closed unless the *actual PDF* is tagged and links only to pinned NASA URLs.

    pdfinfo -url exposes PDF annotations, not merely printed URL strings. This
    checks offline reader navigation; it is NOT an axe, PDF/UA or screen-reader pass.
    """
    fields = dict((m.group(1), m.group(2).strip()) for m in
                  re.finditer(r'^([A-Za-z ]+):\s*(.*?)\s*$', info, re.M))
    if fields.get('Tagged', '').lower() != 'yes':
        raise AssertionError('Offline evidence PDF is not structurally tagged')
    if ('Apollo 1' not in fields.get('Title', '') or
            'Final Vestige' not in fields.get('Title', '')):
        raise AssertionError('Offline PDF missing recognizable document title')
    if fields.get('JavaScript', '').lower() != 'no':
        raise AssertionError('Offline PDF must contain no embedded JavaScript')
    if len(expected_nasa) != 6 or len(set(expected_nasa)) != 6:
        raise AssertionError('Exactly six distinct canonical NASA sources required')
    lines = [x for x in urls.splitlines() if x.strip()]
    if not lines or lines[0].strip() != 'Page  Type          URL':
        raise AssertionError('pdfinfo annotation inventory missing')
    seen = []
    for line in lines[1:]:
        match = re.fullmatch(r'\s*\d+\s+Annotation\s+(https://\S+)\s*', line)
        if match is None:
            raise AssertionError('Unrecognized, untrusted or non-HTTPS PDF annotation')
        seen.append(match.group(1))
    counts = Counter(seen)
    allowed = set(expected_nasa) | {NASA_REPORT, NASA_POLICY}
    if set(counts) != allowed:
        raise AssertionError('Missing canonical NASA link or unauthorized PDF link destination')
    if any(counts[url] != 1 for url in expected_nasa):
        raise AssertionError('Each NASA photograph must have one clickable PDF source link')
    if not (1 <= counts[NASA_REPORT] <= 2 and 1 <= counts[NASA_POLICY] <= 2):
        raise AssertionError('NASA report/policy links missing or duplicated unexpectedly')
    return {'tagged': True, 'title_present': True,
            'clickable_nasa_records': 6, 'clickable_nasa_rights_and_report': 2,
            'annotation_count': len(seen), 'unapproved_destinations': 0,
            'embedded_javascript': False}


def audit_pdf(path:Path,width:int,case_sha:str,export_sha:str)->dict:
    metadata=cmd('pdfinfo',str(path))
    m=re.search(r'^Pages:\s*(\d+)',metadata,re.M)
    assert m,(width,'pdfinfo could not determine page count')
    pages=int(m.group(1));assert 1<=pages<=6,(width,'unbounded paper size',pages)
    expected_urls=[r['image_url'] for r in json.loads((CASEFILE/'records.json').read_text(encoding='utf-8'))['records']]
    semantics=verify_pdf_semantics(metadata,cmd('pdfinfo','-url',str(path)),expected_urls)
    per_page=[cmd('pdftotext','-f',str(n),'-l',str(n),'-layout',str(path),'-') for n in range(1,pages+1)]
    text='\n'.join(per_page)
    dense=re.sub(r'\s+','',text)
    assert all(len(t.strip())>75 for t in per_page),(width,'blank or near-empty page')
    assert text.count('Apollo 1 — Six-Source Research Custody Ledger')==1
    for rid in range(1,7):
        title=f'Record {rid:02d} —'
        hits=[i for i,t in enumerate(per_page) if title in t]
        assert len(hits)==1,(width,'duplicate or split record heading',rid,hits)
        assert 'IMAGE REUSE NOT CLEARED' in per_page[hits[0]],(width,'rights notice separated from record',rid)
    for value in (CASEFILE_PIN,case_sha,export_sha):
        assert value in dense,(width,'source-fingerprint not extractable in printed PDF',value)
    assert 'IDENTITY REVIEW HOLD' in text and 'S67-19766' in text and 'S66-30236' in text
    assert text.count('IMAGE REUSE NOT CLEARED')==6
    assert 'No NASA endorsement is implied' in text
    assert 'notindependentlyauthenticateNASArecords' in dense
    assert all(x not in text for x in ('_wpnonce','admin-ajax','data-lat=','data-lon=','wp_ajax_'))
    assert len(re.findall(r'https://www\.nasa\.gov/image-',text))==6,(width,'missing NASA source URL')
    images=cmd('pdfimages','-list',str(path)).splitlines()
    assert len(images)==2,(width,'PDF contains unexpected embedded image',images)
    return {'width':width,'pages':pages,'record_count':6,'rights_hold_count':6,
            'nasa_photo_source_urls':6,'embedded_images':0,'casefile_sha256':case_sha,
            'evidence_export_sha256':export_sha,'pdf_sha256':sha256(path.read_bytes()).hexdigest(),
            'pdf_bytes':path.stat().st_size, 'pdf_semantics':semantics,'status':'PASS'}

def run():
    OUT.mkdir(exist_ok=True,parents=True)
    html,plugin_sha=get_fixture()
    case_sha=sha256((CASEFILE/'records.json').read_bytes()).hexdigest()
    export_sha=sha256((GENERATED/'evidence-export.json').read_bytes()).hexdigest()
    results=[];screens=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':960},java_script_enabled=False,reduced_motion='reduce')
            page=ctx.new_page();errors=[]
            page.on('pageerror',lambda ex:errors.append(str(ex)))
            page.set_content(html,wait_until='load')
            assert page.locator('#fv-ex2-print-transcript').count()==1
            assert not page.locator('#fv-ex2-print-transcript').is_visible()
            pdf_path=OUT/f'apollo-r26-custody-{width}.pdf'
            page.pdf(path=str(pdf_path),format='A4',print_background=True,prefer_css_page_size=True,tagged=True,outline=True)
            assert not errors,(width,errors)
            results.append(audit_pdf(pdf_path,width,case_sha,export_sha))
            if width in (390,1440):
                # Reproducible PDF raster evidence; these images render the PDF,
                # not an artificially constructed HTML screenshot.
                shot=OUT/f'apollo-r26-page1-{width}'
                subprocess.run(['pdftoppm','-f','1','-l','1','-scale-to','1200','-png','-singlefile',str(pdf_path),str(shot)],check=True,timeout=30,stdout=subprocess.DEVNULL)
                path=shot.with_suffix('.png')
                screens.append({'filename':path.name,'sha256':sha256(path.read_bytes()).hexdigest()})
            ctx.close()
        browser.close()
    report={'source':'R25 sealed PHP renderer + R26 ledger custody revision',
        'source_plugin_sha256':plugin_sha,'casefile_pin':CASEFILE_PIN,
        'browser':'Chromium Playwright print_to_pdf, javascript disabled',
        'pdf_engine':'Chromium / A4 tagged+outline; pdftotext/pdfinfo/pdfimages/pdftoppm verified',
        'source_build_determinism':'separate build twice required',
        'pdf_bytes_determinism':'not asserted; metadata may vary',
        'axe_core':'NOT TESTED (no independently verified axe-core bundle)',
        'screen_reader_pdf_ua':'NOT TESTED; tagged PDF is not proof of PDF/UA compliance',
        'actual_wordpress':'NOT TESTED','http_csp':'NOT TESTED',
        'core_web_vitals_p75':'NOT MEASURED','results':results,'screenshots':screens}
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('R27 tagged Chromium PDF: 7/7 widths PASS, 6 clickable NASA links, zero other origins, no JS')
    return report

if __name__=='__main__':run()
