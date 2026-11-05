#!/usr/bin/env python3
"""Apollo R149: exact-match, staging-only corrective HTML export transformer.

Reads an independently exported Apollo Evidence Atlas raw Gutenberg HTML file.
Outputs a separate review candidate and a SHA-256 receipt; never contacts or
changes WordPress. It is NOT a live-site QA, media-rights or purchase approval.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path

BAD = "const photos = $(box, '[data-fvx-chrono-photo]');"
GOOD = "const photos = $$(box, '[data-fvx-chrono-photo]');"
OLD_STATUS = '<p class="fvx-chrono-gallery__position" data-fvx-chrono-position hidden>'
NEW_STATUS = '<p class="fvx-chrono-gallery__position" data-fvx-chrono-position role="status" aria-live="polite" aria-atomic="true" hidden>'
NASA_SOURCES = (
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129',
    'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
)
CTA = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MARKERS = ('data-t="0"', 'data-t="6"', 'data-t="11.3"', 'data-t="14.7"')


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def inspect(html: str) -> list[str]:
    """Require exact shape of the *published* raw source before modifying."""
    errors = []
    for token, count, label in ((BAD, 1, 'EXACT_UNPATCHED_GALLERY_SELECTOR'),
                                (GOOD, 0, 'ALREADY_FIXED_SELECTOR'),
                                (OLD_STATUS, 1, 'EXACT_UNPATCHED_GALLERY_STATUS'),
                                (NEW_STATUS, 0, 'ALREADY_FIXED_STATUS')):
        if html.count(token) != count:
            errors.append(label + '_COUNT_MISMATCH')
    for index in range(3):
        if html.count(f'data-fvx-chrono-photo="{index}"') != 1:
            errors.append(f'PHOTO_{index}_NOT_UNIQUE')
    for item in NASA_SOURCES:
        if item not in html:
            errors.append('NASA_SOURCE_MISSING:' + item)
    for item in MARKERS:
        if item not in html:
            errors.append('CHRONOLOGY_MARKER_MISSING:' + item)
    for item in (CTA, 'Read the full investigation',
                 'photographs do not depict', 'data-fvx-chronology'):
        if item.casefold() not in html.casefold():
            errors.append('CONTEXT_OR_CTA_MISSING:' + item)
    return errors


def propose(html: str) -> str:
    blockers = inspect(html)
    if blockers:
        raise ValueError('SOURCE_HOLD: ' + '; '.join(blockers))
    proposed = html.replace(BAD, GOOD).replace(OLD_STATUS, NEW_STATUS)
    if proposed.count(GOOD) != 1 or proposed.count(NEW_STATUS) != 1:
        raise ValueError('SOURCE_HOLD: patch postconditions failed')
    if proposed.replace(GOOD, BAD).replace(NEW_STATUS, OLD_STATUS) != html:
        raise ValueError('SOURCE_HOLD: unapproved unrelated changes')
    return proposed


def stage(input_path: Path, output_path: Path, manifest_path: Path, expected_sha256: str) -> dict:
    if not (len(expected_sha256) == 64 and all(c in '0123456789abcdef' for c in expected_sha256)):
        raise ValueError('SOURCE_HOLD: independent input SHA-256 required')
    paths = [x.resolve() for x in (input_path, output_path, manifest_path)]
    if len(set(paths)) != 3 or output_path.exists() or manifest_path.exists():
        raise ValueError('SOURCE_HOLD: unsafe or already occupied destination')
    if not input_path.is_file():
        raise ValueError('SOURCE_HOLD: missing input')
    src = input_path.read_text(encoding='utf-8')
    if digest(src) != expected_sha256:
        raise ValueError('SOURCE_HOLD: exported content hash does not match independent source record')
    revised = propose(src)
    evidence = {
        'schema': 'fv.apollo.r149.gallery-correction.v1',
        'source': 'RAW_GUTENBERG_EXPORT_ONLY',
        'source_sha256': digest(src), 'candidate_sha256': digest(revised),
        'source_characters': len(src), 'candidate_characters': len(revised),
        'changes': ['querySelector → querySelectorAll for 3 contextual photos',
                    'role=status + aria-live=polite + aria-atomic=true for gallery position'],
        'browser_qa': 'NOT_EXECUTED_BY_THIS_TOOL', 'axe': 'NOT_EXECUTED',
        'production_lcp_cls': 'NOT_MEASURED', 'media_commercial_rights': 'NOT_CLEARED',
        'product_checkout': 'NOT_VERIFIED', 'paid_sales': 'NOT_VERIFIED',
        'published_to_wordpress': False, 'approved_to_publish': False,
        'status': 'BUILT_NOT_RELEASED_STAGING_HOLD',
    }
    output_path.write_text(revised, encoding='utf-8')
    manifest_path.write_text(json.dumps(evidence, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--expected-sha256', required=True)
    opts = parser.parse_args(argv)
    try:
        receipt = stage(opts.input, opts.output, opts.manifest, opts.expected_sha256)
    except (ValueError, OSError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({'status': receipt['status'], 'source_sha256': receipt['source_sha256'],
                      'candidate_sha256': receipt['candidate_sha256']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
