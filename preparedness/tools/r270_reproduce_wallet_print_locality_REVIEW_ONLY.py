#!/usr/bin/env python3
"""Manual offline proof-of-placement, not a legibility, privacy, child-safety or QD approval.

Requires locally installed Chromium, Playwright and PyMuPDF; optional for R220.
Runs only when explicitly requested; no WordPress, network, user data or writes
inside the tracked repository.  PDF bytes are deliberately not hash-compared.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'audits/r269_cutout_status_card_REVIEW_ONLY.html'
SOURCE_BLOB = '4fbe028e0460dc81478825f501d76b03596faeaf'
LABEL = 'UNAPPROVED - DO NOT USE'
FRONT = ('Privacy: This card may be lost', 'Out-of-area contact:', 'Telephone:')
BACK = ('Privacy: A finder can read', 'Backup contact:', 'Backup telephone:', 'Plan reviewed:')
HOLD = 'DRAFT_HARD_HOLD'


def git_blob(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\\0' + b).hexdigest()


def require(ok, why):
    if not ok:
        raise ValueError('R270 bounded print locality FAIL: ' + why)


def extract_page(pdf_bytes):
    import fitz
    document = fitz.open(stream=pdf_bytes, filetype='pdf')
    require(len(document) == 1, 'expected exactly one physical PDF page')
    page = document[0]
    require(abs(page.rect.width - 612) < .25 and abs(page.rect.height - 792) < .25,
            'expected Letter format 612x792 pt')
    spans=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for s in line['spans']:
                if s['text'].strip():
                    spans.append({'text': s['text'].strip(), 'font_pt': round(s['size'], 2),
                                  'bounds_pt': [round(v,2) for v in s['bbox']]})
    return spans


def face_receipt(spans, left, right, must_contain):
    subset=[s for s in spans if s['bounds_pt'][0] >= left and s['bounds_pt'][2] <= right]
    words=' '.join(x['text'] for x in subset)
    require(words.count(LABEL) == 1, 'status label not once within printed face')
    for required in must_contain:
        require(required in words, 'PDF face missing source-backed copy: ' + required)
    small=[s for s in subset if (s['text'].startswith('Privacy:') or LABEL in s['text'])]
    require(len(small) == 2, 'face privacy/status text spans missing')
    small_font=[float(s['font_pt']) for s in small]
    require(all(7.7 <= x <= 8.3 for x in small_font), 'print caution size unexpectedly changed')
    require(all(s['bounds_pt'][1] >= 70 and s['bounds_pt'][3] <= 220 for s in subset),
            'face text extends outside measured printable card vertical region')
    return {'status_count': 1, 'privacy_count': 1,
            'min_warning_font_pt': min(small_font),
            'max_warning_font_pt': max(small_font),
            'verified_field_labels': list(must_contain[1:]),
            'text_inside_expected_cutout_bounds': True}


async def run(output, chrome):
    from playwright.async_api import async_playwright
    source = SOURCE.read_bytes()
    require(git_blob(source) == SOURCE_BLOB, 'R269 source drift')
    output = output.resolve()
    require(ROOT not in output.parents and output != ROOT, 'evidence must be outside repository')
    output.mkdir(parents=True,exist_ok=True)
    require(not any(output.iterdir()), 'refuse to overwrite evidence')
    report={'schema':'fv.r270.wallet.pdf-face-locality.v1','state':HOLD,
            'source_git_blob':SOURCE_BLOB,'pdf_page_size_pt':[612,792],
            'proof_scope':'bounded offline Chromium+PDF spans, not physical usability',
            'javascript_modes':{},'physical_print_approved':False,
            'legibility_approved':False,'child_privacy_approved':False,
            'independent_qd_pass':False,'publication_authorized':False,
            'commerce_approved':False,'full_native_pipeline_executed':False}
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path=chrome,headless=True,args=['--no-sandbox'])
        try:
            report['chromium_version']=browser.version
            for enabled in (False, True):
                ctx=await browser.new_context(viewport={'width':390,'height':900},java_script_enabled=enabled)
                await ctx.route('**/*',lambda route:route.abort())
                page=await ctx.new_page()
                await page.set_content(source.decode('utf-8'))
                await page.emulate_media(media='print')
                require(await page.locator('.pa-face').count() == 2, 'two faces required')
                pdf=await page.pdf(format='Letter',print_background=True)
                spans=extract_page(pdf)
                require(sum(LABEL in s['text'] for s in spans)==2, 'two source badges in printed PDF')
                # Physical-page x bounds established independently from 7in/2-face print grid:
                # left 0.5in margin=36pt plus 6pt HTML margin -> card starts 42pt.
                # center=294pt; card right=546pt. Allow 1pt rounding at the face split.
                a=face_receipt(spans, 42, 294.2, FRONT)
                b=face_receipt(spans, 294.2, 546.2, BACK)
                report['javascript_modes'][str(enabled).lower()]={'page_count':1,
                    'front':a,'back':b,'pdf_text_label_count':2}
                (output/f'wallet_print_js_{int(enabled)}.pdf').write_bytes(pdf)
                await ctx.close()
        finally:
            await browser.close()
    require(report['javascript_modes']['false'] == report['javascript_modes']['true'],
            'JavaScript-on/off printed face evidence differs')
    require(all(report['javascript_modes'][k][f]['min_warning_font_pt'] < 9
                for k in ('false','true') for f in ('front','back')),
            'review-risk claim about sub-9pt cautions no longer supported')
    report['printed_warning_below_internal_9pt_review_floor'] = True
    report['physical_paper_cut_fold_not_tested'] = True
    (output/'r270_print_locality_receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--chromium',default=shutil.which('chromium') or '/usr/bin/chromium')
    args=parser.parse_args()
    result=asyncio.run(run(args.output,args.chromium))
    print(json.dumps({'state':result['state'], 'source_blob':result['source_git_blob'],
          'both_face_observations':len(result['javascript_modes']),
          'printed_warning_below_internal_9pt_review_floor':True,
          'physical_legibility_approved':False}))
if __name__=='__main__':main()
