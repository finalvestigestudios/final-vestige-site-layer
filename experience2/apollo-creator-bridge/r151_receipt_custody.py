#!/usr/bin/env python3
"""R151 independent acceptance audit of R149/R150 Apollo offline browser receipts.

No network, deployment, publication, analytics or merchant operations. A valid
source-excerpt result is NOT a full rendered WordPress / commercial release pass.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from r149_gallery_release_candidate import digest, inspect, propose
from r150_real_excerpt_gate import ACTUAL_WP_EXCERPT_BLOB, git_blob_sha
from r149_gallery_browser_regression import WIDTHS

NOJS_CHECKS = frozenset({
    'no_js_three_context_photos', 'no_js_tool_hidden',
    'no_js_original_source_links', 'no_js_reader_link',
    'no_js_no_horizontal_scroll',
})
STAGE_CHECKS = frozenset({
    'range_exists', 'three_source_figures', 'gallery_at_0',
    'gallery_at_6', 'gallery_at_11.3', 'gallery_at_14.7',
    'no_runtime_exception', 'no_horizontal_overflow',
})
AFTER_CHECKS = frozenset({
    'status_announced', 'status_historical_disclaimer',
    'one_real_reader_link', 'keyboard_operates_range',
})
SCREENSHOTS = frozenset({f'r149-after-{w}.png' for w in WIDTHS} | {'r149-after-nojs-390.png'})


def audit(source: str, r149: dict, r150: dict, artifact_dir: Path) -> dict:
    """Validate independent inputs, never trust receipt totals or claims alone."""
    errors, incomplete = [], []
    def require(ok: bool, key: str, *, missing: bool = False):
        if not ok: (incomplete if missing else errors).append(key)
    require(not inspect(source), 'source_unpatched_shape_invalid')
    require(git_blob_sha(source) == ACTUAL_WP_EXCERPT_BLOB, 'not_pinned_actual_wp_excerpt')
    candidate = propose(source) if not inspect(source) else None
    src = r150.get('source') or {}
    require(src.get('type') == 'ACTUAL_WP_DERIVED_EXCERPT', 'receipt_scope_not_actual_excerpt')
    require(src.get('original_blob') == git_blob_sha(source), 'source_blob_receipt_mismatch')
    require(candidate is not None and src.get('candidate_blob') == git_blob_sha(candidate or ''), 'candidate_blob_receipt_mismatch')
    require(r149.get('source_sha256') == digest(source), 'r149_source_sha256_mismatch')
    require(candidate is not None and r149.get('candidate_sha256') == digest(candidate or ''), 'r149_candidate_sha256_mismatch')
    require(r149.get('scope') == 'OFFLINE_SOURCE_FRAGMENT_NOT_RENDERED_WP', 'r149_scope_mismatch')
    require(r150.get('schema') == 'fv.apollo.r150.source-bound-browser.v1', 'r150_schema_mismatch')
    require(r149.get('schema') == 'fv.apollo.r149.browser.v1', 'r149_schema_mismatch')
    require(str(r149.get('browser_version','')).split('.')[0].isdigit(), 'chromium_version_missing')
    for stage in ('before','after'):
        for width in WIDTHS:
            reported = [v for v in r149.get('checks',[]) if v.get('stage') == stage and v.get('width') == width]
            keys = {v.get('check') for v in reported if v.get('pass') is True}
            needed = STAGE_CHECKS | (AFTER_CHECKS if stage == 'after' else frozenset())
            require(needed <= keys, f'chrome_{stage}_{width}_missing_or_failed:{sorted(needed-keys)}')
    nojs = [v for v in r149.get('checks',[]) if v.get('stage') == 'nojs' and v.get('width') == 390]
    require({'all_three_figures_visible','all_three_nasa_links','slider_enhancement_hidden'} <=
        {v.get('check') for v in nojs if v.get('pass') is True}, 'r149_nojs_incomplete')
    require(not any(v.get('pass') is not True for v in r149.get('checks',[])), 'r149_failed_check')
    require(r149.get('failed') == 0 and r149.get('passed') == len(r149.get('checks',[])), 'r149_totals_untrustworthy')
    extra = (r150.get('r150_extra') or {}).get('checks') or []
    for width in WIDTHS:
        ok = {v.get('check') for v in extra if v.get('width') == width and v.get('pass') is True}
        require(NOJS_CHECKS <= ok, f'r150_nojs_{width}_missing_or_failed:{sorted(NOJS_CHECKS-ok)}')
        require('axe_no_wcag_violations' in ok, f'axe_{width}_not_passed', missing=True)
    require(not any(v.get('pass') is not True for v in extra), 'r150_failed_check', missing=True)
    require(r150.get('failed') == 0, 'r150_nonzero_failure_count', missing=True)
    require(r150.get('axe') == 'EXECUTED', 'axe_not_executed', missing=True)
    axes = (r150.get('r150_extra') or {}).get('axe_results') or []
    for width in WIDTHS:
        found = [v for v in axes if v.get('width') == width]
        require(len(found) == 1 and found[0].get('violations') == [] and found[0].get('incomplete') == 0,
                f'axe_{width}_violations_incomplete_or_missing', missing=True)
    pictures = r149.get('screenshots') or []
    require({p.get('file') for p in pictures} == SCREENSHOTS and len(pictures) == 7, 'screenshot_manifest_missing')
    require(r150.get('screenshots') == pictures, 'r150_screenshot_manifest_divergence')
    for shot in pictures:
        name = shot.get('file','')
        if name not in SCREENSHOTS: continue
        path = artifact_dir / name
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == shot.get('sha256'),
                'screenshot_missing_or_tampered:' + name)
    for label, data in (('r149',r149),('r150',r150)):
        require(data.get('approved_to_publish') is False, f'{label}_unsafe_publish_flag')
    require(r150.get('actual_site_browser') == 'NOT_EXECUTED', 'misleading_live_browser_claim')
    require(r150.get('production_qa_complete') is False, 'misleading_production_qa_claim')
    require(r150.get('rights') == 'NOT_CLEARED_FOR_COMMERCIAL_PRODUCT', 'misleading_media_rights_claim')
    require(r150.get('sales') == 'NOT_VERIFIED', 'misleading_sales_claim')
    status = 'FAIL_STAGING_HOLD' if errors else ('INCOMPLETE_STAGING_HOLD' if incomplete else 'SOURCE_EXCERPT_QA_PASS_STAGING_HOLD')
    return {'schema':'fv.apollo.r151.receipt-custody.v1', 'status':status,
            'errors':sorted(set(errors)), 'incomplete':sorted(set(incomplete)),
            'source_git_blob':git_blob_sha(source), 'candidate_git_blob':git_blob_sha(candidate or ''),
            'screenshots_inspected':len(pictures), 'verified_live':False,
            'approved_to_publish':False, 'verified_paid_orders':False,
            'realized_net_revenue':'NOT_COMPUTABLE'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('source','r149','r150','artifacts','out'): p.add_argument('--'+field,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists(): p.error('refusing to overwrite existing receipt')
    result=audit(a.source.read_text(encoding='utf8'),json.loads(a.r149.read_text()),
                 json.loads(a.r150.read_text()),a.artifacts)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'errors':len(result['errors']),'incomplete':len(result['incomplete'])}))
    return 0 if result['status']=='SOURCE_EXCERPT_QA_PASS_STAGING_HOLD' else 2

if __name__=='__main__':raise SystemExit(main())
