#!/usr/bin/env python3
"""Explicit offline Chromium reproduction for R267. NOT a QD/release test.

Usage: python -I preparedness/tools/r267_reproduce_browser_observation_REVIEW_ONLY.py
            --output /tmp/r267-evidence
Requires Playwright and a local Chromium executable; performs no network calls.
Creates inspectable screenshots/PDFs in the explicit, external output directory.
Never modifies source, WordPress, merchant, analytics or social destinations.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_PATH = ROOT / 'audits/r264_minimal_wallet_card_REVIEW_ONLY.html'
CANDIDATE_PATH = ROOT / 'audits/r267_responsive_wallet_card_REVIEW_ONLY.html'
SOURCE_PIN = '40782ef142edfd348fec53eb6d8a0dc673244dea'
CANDIDATE_PIN = '5ae643302faf6bce47e8c507fbcfff9c099eaf00'
WIDTHS = [320,360,390,768,1440]

def blob(b:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def safely_create_outdir(folder:Path):
    root=ROOT.resolve()
    folder=folder.resolve()
    if folder==root or root in folder.parents:
        raise ValueError('R267 evidence directory cannot be inside the source tree')
    folder.mkdir(parents=True,exist_ok=True)
    if any(folder.iterdir()):
        raise ValueError('R267 evidence folder must be empty to avoid overwriting prior evidence')
    return folder

async def execute(folder:Path, chromium:str):
    from playwright.async_api import async_playwright
    source=ORIGINAL_PATH.read_bytes()
    preview=CANDIDATE_PATH.read_bytes()
    if blob(source)!=SOURCE_PIN or blob(preview)!=CANDIDATE_PIN:
        raise ValueError('R267 source identities changed; cannot reproduce recorded observation')
    record={'state':'DRAFT_HARD_HOLD','source_blob':SOURCE_PIN,'candidate_blob':CANDIDATE_PIN,
            'original':{'screen':{},'print':{}},'preview':{'screen':{},'print':{}},
            'physical_print_cut_fold_approved':False,'source_citations_approved':False,
            'privacy_approved':False,'independent_qd_pass':False,'public_published':False}
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox'])
        try:
            record['chromium_version']=browser.version
            for label, html in [('original',source.decode()),('preview',preview.decode())]:
                for width in WIDTHS:
                    context=await browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False)
                    await context.route('**/*',lambda route:route.abort())
                    page=await context.new_page()
                    await page.set_content(html)
                    data=await page.evaluate('''() => {
                      const card=document.querySelector('.pa-foldcard');
                      return {document_css_px:document.documentElement.scrollWidth,
                       card_css_px:card.getBoundingClientRect().width,
                       front_and_back_visible:[...document.querySelectorAll('.pa-privacy')].map(e=>e.getClientRects().length>0)}
                    }''')
                    record[label]['screen'][str(width)]=data
                    await page.screenshot(path=str(folder/f'{label}_{width}.png'),full_page=True)
                    await context.close()
                for js in [True,False]:
                    context=await browser.new_context(viewport={'width':390,'height':900},java_script_enabled=js)
                    await context.route('**/*',lambda route:route.abort())
                    page=await context.new_page()
                    await page.set_content(html)
                    await page.emulate_media(media='print')
                    dims=await page.evaluate('''() => ({card_width:document.querySelector('.pa-foldcard').getBoundingClientRect().width,
                      card_height:document.querySelector('.pa-foldcard').getBoundingClientRect().height,
                      face_widths:[...document.querySelectorAll('.pa-face')].map(n=>n.getBoundingClientRect().width),
                      privacy_font_px:[...document.querySelectorAll('.pa-privacy')].map(n=>getComputedStyle(n).fontSize)})''')
                    pdf=await page.pdf(format='Letter',print_background=True)
                    (folder/f'{label}_js_{int(js)}.pdf').write_bytes(pdf)
                    record[label]['print'][str(js)]={**dims,'sha256':hashlib.sha256(pdf).hexdigest()}
                    await context.close()
        finally:
            await browser.close()
    before=[record['original']['screen'][str(w)]['document_css_px'] for w in WIDTHS]
    after=[record['preview']['screen'][str(w)]['document_css_px'] for w in WIDTHS]
    # PDF byte digests can change between browser contexts/runs because of
    # PDF object IDs/metadata even when rendered card geometry and words match.
    # Never equate a changed PDF hash with either content drift or QA approval.
    match_geometry=all(
        {k:v for k,v in record['original']['print'][str(js)].items() if k!='sha256'}==
        {k:v for k,v in record['preview']['print'][str(js)].items() if k!='sha256'}
        for js in (True,False))
    def extract_pdf(path):
        return subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)
    text_matches=all(extract_pdf(folder/f'original_js_{int(js)}.pdf')==
                     extract_pdf(folder/f'preview_js_{int(js)}.pdf')
                     for js in (True,False))
    verified=before==[680,680,680,768,1440] and after==WIDTHS and match_geometry and text_matches
    record['same_run_print_geometry_parity']=match_geometry
    record['same_run_pdf_extracted_text_parity']=text_matches
    record['pdf_byte_hashes_may_differ_between_contexts']=True
    record['bounded_five_width_and_same_run_geometry_text_reproducible']=verified
    record['not_human_accessibility_or_physical_print_approval']=True
    (folder/'reproduction.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return verified

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--chromium',default=shutil.which('chromium') or '/usr/bin/chromium')
    args=parser.parse_args()
    output=safely_create_outdir(args.output)
    if not asyncio.run(execute(output,args.chromium)):
        raise SystemExit('R267 browser parity regression FAILED; all approvals remain held')
    print('R267 bounded browser reproduction complete; DRAFT_HARD_HOLD; output:', output)

if __name__=='__main__':main()
