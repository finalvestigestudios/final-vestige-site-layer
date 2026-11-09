#!/usr/bin/env python3
"""Read-only FV Experience 2.0 live Page 6 Gutenberg-source reconciliation.

Input: a locally exported wpcom_mcp_pages_get(context=edit, id=6) JSON object.
NEVER requests a URL, logs PII, writes CMS data, or claims browser/WCAG/Jetpack QA.

Usage:
  python verify_live_homepage_reconciliation.py page6-export.json --receipt report.json

This gate answers a specific question: is the seven-chapter edition already
present in the PUBLISHED page editor document, with native subscriber capture?
It MUST NOT be treated as deployment approval or image-transfer proof.
"""
import argparse
import json
import re
from pathlib import Path

CHAPTER_IDS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence',
               'fv-hf-inquiry', 'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title')
CHAPTER_NAV_RE = re.compile(r'<nav\b[^>]*class="fv-hf__chapter-nav"[^>]*>(.*?)</nav>', re.S)
MARGIN_RE = re.compile(r'<span\b[^>]*class="fv-margin-strip__item"[^>]*style="--i:(\d+)"')
JETPACK_RE = re.compile(r'<!-- wp:jetpack/subscriptions(?:\s+\{[^\n]*?\})?\s*/-->')
FOCUS_RE = re.compile(r'\bhref="(?:https://finalvestige\.com)?/focus/"')
DISPATCH_RE = re.compile(r'\bhref="(?:https://finalvestige\.com)?/dispatch/"')
HTML_IMAGE_RE = re.compile(r'<img\b[^>]*>', re.I)


def get_page(export):
    """Accept a WP.com tool result (data) or an editor-context REST page."""
    page = export.get('structuredContent', export)
    page = page.get('data', page)
    if not isinstance(page, dict):
        raise ValueError('PAGE_EXPORT_NOT_AN_OBJECT')
    content = page.get('content')
    if isinstance(content, dict):
        content = content.get('raw')
    if not isinstance(content, str):
        raise ValueError('PAGE_EXPORT_MUST_INCLUDE_RAW_EDIT_CONTENT')
    return page, content


def audit(export):
    page, content = get_page(export)
    nav = CHAPTER_NAV_RE.search(content)
    nav_ids = re.findall(r'href="#([A-Za-z0-9_-]+)"', nav.group(1)) if nav else []
    ids = re.findall(r'\bid="([A-Za-z0-9_-]+)"', content)
    idx = [int(i) for i in MARGIN_RE.findall(content)]
    jp = JETPACK_RE.findall(content)
    imgs = HTML_IMAGE_RE.findall(content)
    findings = {
        'published_page_6': page.get('id') == 6 and page.get('status') == 'publish',
        'seven_chapter_nav': nav_ids == list(CHAPTER_IDS),
        'all_seven_anchor_ids_exist_exactly_once': all(ids.count(a) == 1 for a in CHAPTER_IDS),
        'seventy_two_ordered_margin_records': idx == list(range(72)),
        'native_jetpack_subscriptions_once': len(jp) == 1 and 'is-style-split' in jp[0],
        'focus_and_dispatch_routes': len(FOCUS_RE.findall(content)) >= 1 and len(DISPATCH_RE.findall(content)) >= 1,
        'no_private_playground_or_subscriber_spoof': not any(
            x in content for x in ('[fv_ex2_playground]', 'fv-ex2-focus-review', 'data-fv-ex2-isolated-focus')),
        'nasa_franklin_nypl_primary_sources_linked': all(x in content for x in (
            'nasa.gov', 'rmg.co.uk', 'digitalcollections.nypl.org')),
        'three_archival_images_present_in_editor': all(x in content for x in (
            's67-19766.webp', 'Franklinexpeditionnote.jpg', 'edit-017-v02-nypl-5003296-original.jpg')),
        'focus_cover_image_present': 'focus_complete_cover.webp' in content,
    }
    return {
        'kind': 'READ_ONLY_PUBLISHED_WORDPRESS_EDITOR_SOURCE_RECONCILIATION',
        'page_id': page.get('id'), 'status': page.get('status'), 'modified': page.get('modified'),
        'editor_character_count': len(content),
        'chapter_nav_targets': nav_ids, 'margins_count': len(idx),
        'native_jetpack_block_count': len(jp), 'editor_img_count': len(imgs),
        'focus_hrefs_count': len(FOCUS_RE.findall(content)),
        'dispatch_hrefs_count': len(DISPATCH_RE.findall(content)),
        'findings': findings, 'source_checks_pass': all(findings.values()),
        'strict_limits': {
            'live_rendering_verified': False,
            'native_jetpack_transaction_verified': False,
            'browser_navigation_verified': False,
            'full_wordpress_core_integration_certified': False,
            'image_network_bytes_verified': False,
            'wcag_2_2_aa_certified': False,
            'lighthouse_or_cwv_measured': False,
            'commercial_conversion_verified': False,
            'production_release_authorized': False,
        },
        'decision': 'SOURCE_PRESENT_ALREADY_PUBLIC; POST-PUBLICATION QA HOLD'
            if all(findings.values()) else 'SOURCE_DRIFT_OR_INTEGRATION_FAILURE; INVESTIGATE'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('read_only_page6_export', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    report = audit(json.loads(args.read_only_page6_export.read_text(encoding='utf-8')))
    if args.receipt:
        args.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'strict_limits'}, indent=2))
    raise SystemExit(0 if report['source_checks_pass'] else 1)


if __name__ == '__main__':
    main()
