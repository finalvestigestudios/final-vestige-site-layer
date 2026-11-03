#!/usr/bin/env python3
"""Same-WordPress-run ABBA diagnostic for existing Gutenberg CSS ordering.

Creates NO new source chapter, external dependency, production page or account.
Runs against the already saved disposable local WP draft, restores it in finally.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from statistics import median
from urllib.parse import urlsplit
from verify_saved_frontend_admission import validate_saved_preview
from verify_saved_gutenberg_lab import run_saved_native_lab

SITE = 'http://127.0.0.1:9400'
STYLE = re.compile(r'<style>.*?</style>', re.DOTALL)
SCRIPT = re.compile(r'<script\b')
ORDER = ('early', 'late', 'late', 'early')


def make_css_late_variant(candidate: str) -> str:
    """Move only the single identical CSS block to before the first JS script."""
    if not isinstance(candidate, str) or not candidate.startswith('<!-- wp:html -->\n<style>'):
        raise ValueError('CSS_ABBA_EXPECTED_EARLY_GUTENBERG_BLOCK')
    styles = list(STYLE.finditer(candidate))
    if len(styles) != 1 or candidate.count('</style>') != 1:
        raise ValueError('CSS_ABBA_SINGLE_STYLE_REQUIRED')
    match = styles[0]
    opening = candidate[:match.start()] + candidate[match.end():]
    script = SCRIPT.search(opening)
    if script is None or script.start() <= len('<!-- wp:html -->'):
        raise ValueError('CSS_ABBA_TRAILING_SCRIPT_REQUIRED')
    late = opening[:script.start()] + match.group(0) + opening[script.start():]
    if late.replace(match.group(0), '', 1) != opening:
        raise ValueError('CSS_ABBA_EDITORIAL_PARITY_FAILURE')
    if late == candidate or not late.rstrip().endswith('<!-- /wp:html -->'):
        raise ValueError('CSS_ABBA_TRANSFORMATION_FAILURE')
    return late


def summarize_pairs(records: list[dict]) -> dict:
    if [x.get('variant') for x in records] != list(ORDER):
        raise ValueError('CSS_ABBA_ORDER_INVALID')
    result = {}
    for variant in ('early', 'late'):
        subset = [x for x in records if x['variant'] == variant]
        times = [s['lcp_ms'] for x in subset for s in x['samples']
                 if s.get('viewport') == 390]
        if len(times) != 4 or any(type(x) not in (int, float) or x <= 0 for x in times):
            raise ValueError('CSS_ABBA_MOBILE_MEASUREMENT_MISSING')
        result[variant + '_median_mobile_lcp_ms'] = round(median(times), 1)
        result[variant + '_mobile_lcp_samples_ms'] = times
    result['late_minus_early_median_ms'] = round(
        result['late_median_mobile_lcp_ms'] - result['early_median_mobile_lcp_ms'], 1)
    return result


def run_css_order_abba(page, page_id: int, candidate: str, probe: str,
                       out: Path, expected_sha: str) -> dict:
    """Compare ABBA CSS order in a single disposable WP runtime (no release pass)."""
    if type(page_id) is not int or page_id < 1 or probe.count(candidate) != 1:
        raise ValueError('CSS_ABBA_EXACT_LOCAL_DRAFT_REQUIRED')
    validate_saved_preview(page.url, page_id)
    late = make_css_late_variant(candidate)
    originals = {'early': probe, 'late': probe.replace(candidate, late, 1)}
    if originals['late'] == originals['early'] or len(originals['late']) < 100000:
        raise ValueError('CSS_ABBA_ALTERNATE_DOC_INVALID')
    out.mkdir(parents=True, exist_ok=True)
    records = []

    def save_local(content: str) -> None:
        page.goto(SITE + '/wp-admin/post-new.php?post_type=page',
                  wait_until='domcontentloaded', timeout=40000)
        p = urlsplit(page.url)
        if (p.scheme != 'http' or p.hostname != '127.0.0.1' or p.port != 9400
                or p.username is not None or p.password is not None
                or not p.path.startswith('/wp-admin/')):
            raise ValueError('CSS_ABBA_LOCAL_ADMIN_REQUIRED')
        page.wait_for_function('Boolean(window.wp && window.wp.apiFetch)', timeout=30000)
        result = page.evaluate('''async ({id, content}) => {
          await wp.apiFetch({path:'/wp/v2/pages/'+id,
            method:'POST', data:{status:'draft',content}});
          const read = await wp.apiFetch({path:'/wp/v2/pages/'+id+'?context=edit'});
          return {id:read.id,status:read.status,raw:read.content && read.content.raw};
        }''', {'id': page_id, 'content': content})
        if (result.get('id') != page_id or result.get('status') != 'draft'
                or result.get('raw') != content):
            raise ValueError('CSS_ABBA_GUTENBERG_BYTES_CHANGED')

    try:
        for index, variant in enumerate(ORDER, start=1):
            save_local(originals[variant])
            page.goto(SITE + '/?page_id=' + str(page_id) + '&preview=true',
                      wait_until='domcontentloaded', timeout=45000)
            validate_saved_preview(page.url, page_id)
            page.locator('[data-fv-home-flagship]').wait_for(state='visible', timeout=20000)
            dirname = 'CSS_ORDER_ABBA_%02d_%s' % (index, variant.upper())
            receipt = run_saved_native_lab(page, page_id, out / dirname, expected_sha)
            if receipt.get('failure_codes'):
                raise ValueError('CSS_ABBA_REAL_LAB_INSTRUMENTATION_INVALID')
            page.set_viewport_size({'width': 390, 'height': 844})
            page.evaluate('window.scrollTo(0,0)')
            screenshot = dirname + '_390.png'
            page.screenshot(path=str(out / screenshot), timeout=20000,
                            animations='disabled')
            records.append({
                'sequence': index,
                'variant': variant,
                'saved_content_sha256': hashlib.sha256(
                    originals[variant].encode('utf-8')).hexdigest(),
                'samples': receipt['samples'],
                'screenshot': screenshot,
                'lab_budget_gate': receipt['native_lab_budget_gate'],
            })
        result = {
            'source_sha': expected_sha,
            'sequence': 'ABBA',
            'environment': 'DISPOSABLE_LOCAL_WORDPRESS_SAVED_GUTENBERG',
            'comparison': 'CSS_ORDER_ONLY_SAME_RUN_NOT_RANDOMIZED',
            'production_writes': False,
            'hosted_wordpress_com': 'NOT_TESTED',
            'field_cwv': 'NOT_MEASURED',
            'release_gate': 'HOLD',
            'claim': 'DIAGNOSTIC_NOT_CAUSAL_PROOF',
            'records': records,
            'comparison_ms': summarize_pairs(records),
        }
        (out / 'GUTENBERG_SAVED_CSS_ORDER_ABBA.json').write_text(
            json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        return result
    finally:
        # This is ONLY an ephemeral localhost page; restore even on test failure.
        save_local(originals['early'])
