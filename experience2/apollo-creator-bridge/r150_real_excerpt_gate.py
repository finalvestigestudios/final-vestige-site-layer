#!/usr/bin/env python3
"""R150 source-bound offline Apollo QA admission. No WordPress writes or release.

Real QA requires the exact GitHub-committed R149 raw WordPress excerpt,
not a copy of the synthetic R149 model. R149's native Chromium runner supplies
before/after interaction checks; this gate adds strict source custody, all-width
no-JS acceptance, optional axe scans, and explicit incomplete/release states.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from r149_gallery_release_candidate import inspect, propose, CTA, NASA_SOURCES
from r149_gallery_browser_regression import review, WIDTHS, GALLERY, RANGE

ACTUAL_WP_EXCERPT_BLOB = '899b7c4a1c46b2e6c46bf079d6784124636a011e'


def git_blob_sha(text: str) -> str:
    raw = text.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def check_source(html: str, model: bool = False) -> dict:
    blob = git_blob_sha(html)
    if not model and blob != ACTUAL_WP_EXCERPT_BLOB:
        raise ValueError('SOURCE_HOLD: expected committed R149 WP-derived excerpt blob ' + ACTUAL_WP_EXCERPT_BLOB + ', got ' + blob)
    errors = inspect(html)
    if errors:
        raise ValueError('SOURCE_HOLD: unpatched source integrity: ' + '; '.join(errors))
    fixed = propose(html)
    if fixed == html or git_blob_sha(fixed) == blob:
        raise ValueError('SOURCE_HOLD: patch was not applied')
    return {'type': 'CONTROLLED_MODEL' if model else 'ACTUAL_WP_DERIVED_EXCERPT',
            'original_blob': blob, 'candidate_blob': git_blob_sha(fixed), 'source': fixed}


def inspect_accessibility(html: str, axe: Path | None) -> dict:
    """Supplement R149 with Chromium no-JS, viewport QA and axe, if supplied."""
    checks = []
    axes = []
    def add(width, kind, good, detail=''):
        checks.append({'width': width, 'check': kind, 'pass': bool(good), 'detail': str(detail)[:220]})
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True,
            executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                context = browser.new_context(viewport={'width':width,'height':820},
                    java_script_enabled=False, reduced_motion='reduce')
                context.route('**/*',lambda route:route.abort('blockedbyclient'))
                page = context.new_page()
                try:
                    page.set_content(html, wait_until='domcontentloaded',timeout=15000)
                    figures=page.locator(GALLERY)
                    add(width,'no_js_three_context_photos',figures.count()==3 and
                        all(figures.nth(i).is_visible() for i in range(3)))
                    add(width,'no_js_tool_hidden',page.locator('[data-fvx-chrono-tool]').is_hidden())
                    add(width,'no_js_original_source_links',all(page.locator('a[href="'+u+'"]').count()>=1
                        for u in NASA_SOURCES[:3]))
                    add(width,'no_js_reader_link',page.locator('a[href="'+CTA+'"]').count()==1)
                    add(width,'no_js_no_horizontal_scroll',page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'))
                except Exception as error:
                    add(width,'no_js_runtime_failure',False,repr(error))
                finally:
                    context.close()
                if axe is not None:
                    context = browser.new_context(viewport={'width':width,'height':820},
                        java_script_enabled=True, reduced_motion='reduce')
                    context.route('**/*',lambda route:route.abort('blockedbyclient'))
                    page = context.new_page()
                    try:
                        page.set_content(html, wait_until='domcontentloaded',timeout=15000)
                        page.add_script_tag(path=str(axe))
                        value=page.evaluate('async()=>{const r=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","wcag22aa"]}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),incomplete:r.incomplete.length}}')
                        axes.append({'width':width,**value})
                        add(width,'axe_no_wcag_violations',len(value['violations'])==0,value)
                    except Exception as error:
                        add(width,'axe_execution',False,repr(error))
                    finally:
                        context.close()
        finally:
            browser.close()
    return {'checks':checks,'axe_results':axes}


def run(input_file: Path, output_dir: Path, *, model: bool=False, axe: Path | None=None) -> dict:
    if output_dir.exists():
        raise ValueError('SOURCE_HOLD: output directory already exists; no overwrite')
    if not input_file.is_file():
        raise ValueError('SOURCE_HOLD: missing input')
    if axe is not None and (not axe.is_file() or axe.stat().st_size < 10000):
        raise ValueError('SOURCE_HOLD: axe path missing or not a credible local script')
    identity=check_source(input_file.read_text(encoding='utf-8'),model=model)
    candidate=identity.pop('source')
    base=review(input_file.read_text(encoding='utf-8'),output_dir)
    extra=inspect_accessibility(candidate,axe)
    output={'schema':'fv.apollo.r150.source-bound-browser.v1','source':identity,
        'r149_native_browser': {'passed':base['passed'],'failed':base['failed']},
        'r150_extra':extra,
        'axe': 'EXECUTED' if axe is not None else 'NOT_EXECUTED_AXE_UNAVAILABLE',
        'rights':'NOT_CLEARED_FOR_COMMERCIAL_PRODUCT','production_lcp_cls':'NOT_MEASURED',
        'actual_site_browser':'NOT_EXECUTED','approved_to_publish':False,
        'commercial_offer':'NOT_VERIFIED','sales':'NOT_VERIFIED',
        'release':'STAGING_HOLD'}
    output['passed']=base['passed']+sum(x['pass'] for x in extra['checks'])
    output['failed']=base['failed']+sum(not x['pass'] for x in extra['checks'])
    output['source_excerpt_qa_complete']=(not model and axe is not None and output['failed']==0)
    output['production_qa_complete']=False
    output['status']='SOURCE_EXCERPT_PASS_STAGING_HOLD' if output['source_excerpt_qa_complete'] else 'SOURCE_EXCERPT_INCOMPLETE_STAGING_HOLD'
    output['screenshots']=base['screenshots']
    (output_dir/'r150_qa_receipt.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return output


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--axe',type=Path,help='Local, verified axe-core browser bundle')
    parser.add_argument('--controlled-model',action='store_true',help='Explicitly downgrade receipt to synthetic model only')
    a=parser.parse_args(argv)
    try:
        r=run(a.input,a.out,model=a.controlled_model,axe=a.axe)
    except (ValueError,OSError) as error:
        parser.error(str(error))
    print(json.dumps({k:r[k] for k in ('status','passed','failed','axe','source_excerpt_qa_complete','production_qa_complete')}))
    return 0 if r['failed']==0 else 2

if __name__=='__main__': raise SystemExit(main())
