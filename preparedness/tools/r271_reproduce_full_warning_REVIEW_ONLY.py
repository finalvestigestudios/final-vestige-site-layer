#!/usr/bin/env python3
"""Offline, review-only Chromium print reproducer; refuses input of personal data.

Run with --output an EMPTY directory outside the repository. This is not a
consumer-facing card creator or a product. Requires playwright and PyMuPDF.
"""
from __future__ import annotations
import argparse
import asyncio
import importlib.util
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/'tools/r271_full_warning_print_hold.py'
spec=importlib.util.spec_from_file_location('r271_full_warning_hold',GATE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

async def reproduce(output:Path,chromium:str):
    from playwright.async_api import async_playwright
    output=output.resolve()
    assert ROOT not in output.parents and output!=ROOT, 'output within repo denied'
    output.mkdir(parents=True,exist_ok=True)
    assert not any(output.iterdir()), 'evidence directory not empty'
    original=(ROOT/gate.PARENT_PATH).read_bytes()
    preview=(ROOT/gate.PREVIEW_PATH).read_bytes()
    gate.source_only_delta(original,preview)
    pdfs={}
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox'])
        try:
            version=browser.version
            assert version.startswith('144.'), 'reproduction environment changed'
            for enabled in (False,True):
                ctx=await browser.new_context(viewport={'width':390,'height':900},
                                              java_script_enabled=enabled)
                await ctx.route('**/*',lambda route:route.abort())
                page=await ctx.new_page()
                await page.set_content(preview.decode('utf-8'))
                await page.emulate_media(media='print')
                pdf=await page.pdf(format='Letter',print_background=True)
                # Extract and verify all lines before writing any evidence.
                gate.examine_pdf(pdf)
                pdfs[str(enabled).lower()]=pdf
                await ctx.close()
        finally:
            await browser.close()
    result=gate.create_receipt(original,preview,pdfs['false'],pdfs['true'],version)
    for mode,content in pdfs.items():
        (output/f'r271_wallet_print_js_{mode}_UNAPPROVED.pdf').write_bytes(content)
    (output/'r271_full_warning_receipt.json').write_text(
        json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return {'state':gate.STATE,'complete_privacy_copy_verified':True,
            'candidate_only_not_original_tool':True,
            'independent_qd_pass':False,'physical_print_approved':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--chromium',default=shutil.which('chromium') or '/usr/bin/chromium')
    args=parser.parse_args()
    print(json.dumps(asyncio.run(reproduce(args.output,args.chromium)),sort_keys=True))
