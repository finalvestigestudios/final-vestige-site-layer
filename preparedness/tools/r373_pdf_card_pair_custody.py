#!/usr/bin/env python3
"""R373 Tool #104 PDF cutout *pair* custody; additive, offline, review-only.

R372 proves browser DOM face geometry and counts notice occurrences in PDF, but
neither establishes that each front/back pair survives PDF pagination together.
This gate uses unique TEST-ONLY markers printed on synthetic card faces and
searches ACTUAL generated PDF pages for matching per-card pairs. No real contact
information is collected. The authentic tool is unchanged, and all release
flags remain false. Synthetic PDF proof is NOT a paper-print/safety approval.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r373-pdf-card-pair-custody-v1'
PIN_BODY = 'be8698ac5d020476ff649d85813810e2000c6f98'
PIN_META = '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
BODY = 'content/tools/family-reunification-card.body.html'
META = 'content/tools/family-reunification-card.meta.json'
MAX_CARDS = 4
RELEASE = {key: False for key in ('may_merge', 'may_publish','qd_pass',
    'child_privacy_approved','emergency_safety_approved','paper_trim_verified',
    'native_build_verified','full_export_verified','paid_sku_verified',
    'merchant_sale_verified','attributed_revenue_verified')}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def markers(count: int) -> list[tuple[str, str]]:
    """Unmistakable unique public TEST tokens, never personal contact values."""
    if type(count) is not int or not 1 <= count <= MAX_CARDS:
        raise ValueError('INVALID_TEST_CARD_COUNT')
    return [(f'FVTESTCARD{i:02d}FRONT', f'FVTESTCARD{i:02d}BACK')
            for i in range(1, count+1)]


def check_pdf_pairs(pdf: bytes, *, copies: int, margin_pt: float=18) -> dict:
    """Fail closed if the print pipeline drops, duplicates or page-splits a card.

    Exact \`search_for\` matches require intact PDF text. If Chromium has outlined
    text or PDF extraction is unavailable, the result correctly remains HOLD.
    margin_pt is an additional synthetic printer-safe-area proxy, not proof of
    real device margins. A marker hit does not prove all real fields fit.
    """
    result = dict(schema=SCHEMA, status='INVALID_HARD_HOLD', errors=[],
                  pdf_pages=0, verified_pairs=0, markers=0, **RELEASE)
    try:
        expected = markers(copies)
        if not isinstance(pdf, bytes) or not pdf or len(pdf) > 8_000_000:
            raise ValueError('BAD_BOUNDED_PDF_BYTES')
        if isinstance(margin_pt,bool) or not isinstance(margin_pt,(int,float)) or not 0 <= margin_pt <= 72:
            raise ValueError('INVALID_PRINT_SAFE_MARGIN')
        import fitz
        doc = fitz.open(stream=pdf, filetype='pdf')
        try:
            if not 1 <= len(doc) <= 8:
                raise ValueError('INVALID_PDF_PAGE_COUNT')
            result['pdf_pages'] = len(doc)
            for front, back in expected:
                positions = {}
                for side, token in (('front',front),('back',back)):
                    found = []
                    for page_index, page in enumerate(doc):
                        for rect in page.search_for(token):
                            found.append((page_index, rect, page.rect))
                    if len(found) != 1:
                        result['errors'].append('MISSING_OR_DUPLICATE_'+side.upper()+':'+front)
                    else:
                        pg, r, page_rect = found[0]
                        positions[side] = pg
                        result['markers'] += 1
                        if (r.x0 < margin_pt or r.y0 < margin_pt or
                            r.x1 > page_rect.width-margin_pt or r.y1 > page_rect.height-margin_pt):
                            result['errors'].append('OUTSIDE_TEST_PRINT_MARGIN:'+front+':'+side)
                if len(positions) == 2:
                    if positions['front'] != positions['back']:
                        result['errors'].append('CARD_FACE_PAGE_SPLIT:'+front)
                    else:
                        result['verified_pairs'] += 1
            # Reject any unrequested synthetic card, not just expected markers.
            full_text = '\n'.join(page.get_text() for page in doc)
            all_found = re.findall(r'FVTESTCARD\d{2}(?:FRONT|BACK)',full_text)
            expected_flat = [t for pair in expected for t in pair]
            if sorted(all_found) != sorted(expected_flat):
                result['errors'].append('UNEXPECTED_OR_DROPPED_TEST_TOKENS')
        finally:
            doc.close()
    except Exception as exc:
        result['errors'].append(type(exc).__name__+':'+str(exc))
    result['errors'] = sorted(set(result['errors']))
    if not result['errors']:
        result['status'] = 'SYNTHETIC_PDF_PAIRS_VERIFIED_STILL_HARD_HOLD'
    return result


def synthetic_print_html(copies: int, *, force_split=False,
                         hide_back=False, tiny=False) -> str:
    """Offline print fixture, deliberately NOT copied from the authentic tool."""
    pairs = markers(copies)
    cards = []
    for f,b in pairs:
        second = '' if hide_back else f'<section class="back">{b}</section>'
        css = 'break-before:page;' if force_split else ''
        cards.append(f'<div class="card"><section class="front">{f}</section>'
                     f'<div style="{css}">{second}</div></div>')
    font = '1' if tiny else '12'
    return ('<!doctype html><html><head><style>@page {size:Letter;margin:0.5in;}'
            'body{margin:0;font:12pt sans-serif}.card{width:7in;height:2.125in;'
            'box-sizing:border-box;display:flex;break-inside:avoid;page-break-inside:avoid;'
            'border:1px solid #333;margin:0 0 .2in 0;}'
            '.card section{width:3.4in;box-sizing:border-box;padding:.12in;'
            f'font-size:{font}pt}}'
            '.back{margin-left:.1in}</style></head><body>'+
            ''.join(cards)+'</body></html>')


def print_pdf_fixture(html: str, chromium: str='/usr/bin/chromium') -> bytes:
    """Strictly offline Chromium rendering. No external requests, JS disabled."""
    if not isinstance(html,str) or len(html)>250_000 or not html:
        raise ValueError('BAD_SYNTHETIC_HTML')
    if not Path(chromium).is_file():
        raise ValueError('CHROMIUM_UNAVAILABLE')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=chromium,
                   args=['--no-sandbox','--disable-background-networking','--disable-gpu'])
        try:
            ctx=browser.new_context(offline=True,java_script_enabled=False,service_workers='block')
            ctx.route('**/*',lambda r:r.abort())
            try:
                pg=ctx.new_page()
                attempts=[]
                pg.on('request',lambda req:attempts.append(req.url))
                pg.set_content(html,wait_until='domcontentloaded',timeout=15000)
                pg.emulate_media(media='print')
                pdf=pg.pdf(format='Letter',print_background=True,prefer_css_page_size=True)
                if attempts:
                    raise ValueError('NETWORK_ATTEMPTED_IN_OFFLINE_PRINT')
                return pdf
            finally:ctx.close()
        finally:browser.close()


def review(root: Path, *, browser=False) -> dict:
    """Pinned authentic custody only; never promotes synthetic proof to release."""
    result=dict(schema=SCHEMA,status='INVALID_HARD_HOLD',errors=[],evidence={},**RELEASE)
    try:
        root=Path(root)
        if not root.is_dir() or root.is_symlink():
            raise ValueError('AUTHENTIC_CHECKOUT_UNAVAILABLE')
        b,m=root/BODY,root/META
        if not b.is_file() or not m.is_file() or b.is_symlink() or m.is_symlink():
            raise ValueError('PINNED_TOOL104_SOURCE_MISSING')
        raw, meta_raw=b.read_bytes(),m.read_bytes()
        if git_blob(raw)!=PIN_BODY or git_blob(meta_raw)!=PIN_META:
            raise ValueError('TOOL104_SOURCE_OR_METADATA_DRIFT_REBASE_REQUIRED')
        meta=json.loads(meta_raw)
        if (meta.get('n')!=104 or meta.get('slug')!='family-reunification-card'
            or meta.get('status')!={'editorial':'drafted','publish':'draft'}
            or meta.get('safety_review',{}).get('state')!='pending'):
            raise ValueError('ORIGINAL_DRAFT_PENDING_SAFETY_STATE_CHANGED')
        dep=root/'tools'/'r372_card_print_trim_geometry.py'
        if not dep.is_file() or dep.is_symlink():
            raise ValueError('R372_REQUIRED_SOURCE_GUARD_UNAVAILABLE')
        result['evidence']={'body_blob':PIN_BODY,'meta_blob':PIN_META,
            'source_untouched':True,'synthetic_only':True}
        if browser:
            result['evidence']['synthetic_cases']={str(n):check_pdf_pairs(
                print_pdf_fixture(synthetic_print_html(n)),copies=n)
                for n in (1,4)}
            for check in result['evidence']['synthetic_cases'].values():
                if check['errors']:
                    result['errors'].append('SYNTHETIC_PDF_PAIR_FAILURE')
        result['status']='REVIEW_REQUIRED_HARD_HOLD' if not result['errors'] else 'INVALID_HARD_HOLD'
    except Exception as exc:
        result['errors'].append(type(exc).__name__+':'+str(exc))
    return result


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--browser',action='store_true')
    a=parser.parse_args(argv)
    print(json.dumps(review(a.root,browser=a.browser),sort_keys=True,indent=2))
    return 2  # Never publication clearance.


if __name__=='__main__':sys.exit(main())
