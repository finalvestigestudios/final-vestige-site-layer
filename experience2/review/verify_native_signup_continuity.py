#!/usr/bin/env python3
"""Fail-closed WordPress Page 6 editor-block continuity gate.

This verifies RAW Gutenberg editor content, not rendered shortcode previews.
It cannot certify functioning Jetpack delivery, WordPress Core, or sales.
No network, subscriber data, credentials, or WordPress writes.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

NATIVE = re.compile(r'<!--\\s*wp:jetpack/subscriptions(?:\\s+\\{[^\\n]*?\\})?\\s*/-->')
MARGIN = re.compile(r'<span\\s+class="fv-margin-strip__item"\\s+style="--i:(\\d+)">(.*?)</span>', re.S)
MARGIN_STRIP = 'class="fv-margin-strip fv-margin-strip--rotator"'
PREVIEW_ONLY = (
    '[fv_ex2_playground]', '/fv-ex2-focus-review/',
    'data-fv-ex2-isolated-focus="1"',
    'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1',
)


def digest(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def margins(s):
    return [(int(i), value) for i, value in MARGIN.findall(s)]


def inspect(baseline, candidate):
    """Report only structural evidence and fingerprints, never subscriber data."""
    blockers = []
    baseline_native = NATIVE.findall(baseline)
    candidate_native = NATIVE.findall(candidate)
    baseline_items, candidate_items = margins(baseline), margins(candidate)

    def require(ok, name):
        if not ok:
            blockers.append(name)

    require(len(baseline_native) == 1, 'BASELINE_NATIVE_JETPACK_BLOCK_NOT_EXACTLY_ONE')
    require(len(baseline_items) == 72 and
            [i for i, _ in baseline_items] == list(range(72)), 'BASELINE_72_MARGINS_NOT_VERIFIED')
    require(baseline.count(MARGIN_STRIP) == 1, 'BASELINE_MARGINS_CONTAINER_INVALID')
    require(len(candidate_native) == 1, 'CANDIDATE_NATIVE_JETPACK_BLOCK_NOT_EXACTLY_ONE')
    require(candidate_native == baseline_native, 'CANDIDATE_NATIVE_JETPACK_BLOCK_CHANGED')
    require(candidate_items == baseline_items, 'CANDIDATE_MARGINS_CONTENT_OR_ORDER_CHANGED')
    require(candidate.count(MARGIN_STRIP) == 1, 'CANDIDATE_MARGINS_CONTAINER_INVALID')
    for needle, label in [
        ('/dispatch/', 'DISPATCH_DESTINATION_MISSING'),
        ('Unsubscribe anytime', 'DISPATCH_UNSUBSCRIBE_CONTEXT_MISSING'),
        ('/focus/', 'FOCUS_DESTINATION_MISSING'),
        ('Seven Day Focus Fieldbook', 'FIELD_BOOK_PROMISE_MISSING'),
    ]:
        require(needle in candidate, label)
    for marker in PREVIEW_ONLY:
        require(marker not in candidate, 'REVIEW_ONLY_MARKER_LEAK:' + marker)
    require('<!-- wp:' in candidate, 'RELEASE_NOT_WORDPRESS_EDITOR_BLOCK_MARKUP')

    return {
        'decision': 'SOURCE_CONTINUITY_PASS_NOT_RELEASE_APPROVAL' if not blockers else 'RELEASE_HOLD',
        'blockers': blockers,
        'published_record': {
            'native_subscription_blocks': len(baseline_native),
            'margins_items': len(baseline_items),
            'editor_sha256': digest(baseline),
        },
        'candidate_record': {
            'native_subscription_blocks': len(candidate_native),
            'margins_items': len(candidate_items),
            'editor_sha256': digest(candidate),
        },
        'checks_not_certified': [
            'WordPress parse_blocks/rendering', 'Assembler theme', 'actual Jetpack block render',
            'subscriber confirmation/delivery', 'mail consent', 'Playground rendering',
            'WCAG 2.2 AA', 'Lighthouse/CWV', 'affiliate or paid conversion',
            'image transfers and licensing', 'independent CI/QD',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True,
                        help='Authorized raw Gutenberg Page 6 editor export; public content only')
    parser.add_argument('--candidate', required=True,
                        help='Proposed Page 6 editor markup, NOT shortcode renderer output')
    parser.add_argument('--out', help='Optional machine-readable non-PII receipt path')
    args = parser.parse_args()
    result = inspect(Path(args.baseline).read_text(encoding='utf-8'),
                     Path(args.candidate).read_text(encoding='utf-8'))
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(output + '\\n', encoding='utf-8')
    print(output)
    raise SystemExit(0 if not result['blockers'] else 2)


if __name__ == '__main__':
    main()
