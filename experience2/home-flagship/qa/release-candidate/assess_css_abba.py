#!/usr/bin/env python3
"""Fail-closed, read-only adjudication of a pinned real-Gutenberg ABBA CI ZIP.

No network, WordPress writes, authentication, deployed performance claims or private data.
PASS of this script's data-integrity checks never means a publication PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median
from zipfile import ZipFile, BadZipFile

RECEIPT = 'GUTENBERG_SAVED_CSS_ORDER_ABBA.json'
SEQUENCE = ('early', 'late', 'late', 'early')
IMAGE_PATHS = tuple(f'CSS_ORDER_ABBA_{i:02d}_{v.upper()}_390.png'
                    for i, v in enumerate(SEQUENCE, 1))


def positive_number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def adjudicate(receipt: dict, images: list[bytes], expected_sha: str) -> dict:
    if receipt.get('source_sha') != expected_sha or len(expected_sha) != 40:
        raise ValueError('source SHA is not the reviewed exact head')
    expected_fields = {'sequence': 'ABBA', 'release_gate': 'HOLD',
                       'production_writes': False,
                       'environment': 'DISPOSABLE_LOCAL_WORDPRESS_SAVED_GUTENBERG',
                       'field_cwv': 'NOT_MEASURED',
                       'hosted_wordpress_com': 'NOT_TESTED'}
    if any(receipt.get(k) != value or type(receipt.get(k)) is not type(value)
           for k, value in expected_fields.items()):
        raise ValueError('unsafe or contradictory provenance')
    records = receipt.get('records')
    if not isinstance(records, list) or len(records) != 4 or len(images) != 4:
        raise ValueError('incomplete ABBA sequence or screenshots')
    if not all(image == images[0] and image.startswith(b'\x89PNG\r\n\x1a\n') for image in images):
        raise ValueError('first-screen PNG captures differ or are invalid')
    results = {'early': [], 'late': []}
    cls = {'early': [], 'late': []}
    fcp = {'early': [], 'late': []}
    desktop = {'early': [], 'late': []}
    for index, (rec, expected) in enumerate(zip(records, SEQUENCE), 1):
        if (not isinstance(rec, dict) or rec.get('sequence') != index
                or rec.get('variant') != expected
                or rec.get('screenshot') != IMAGE_PATHS[index-1]
                or rec.get('lab_budget_gate') != 'FAIL'
                or not isinstance(rec.get('saved_content_sha256'), str)
                or len(rec['saved_content_sha256']) != 64):
            raise ValueError('invalid sequence, fixture or source pairing')
        samples = rec.get('samples')
        if not isinstance(samples, list) or len(samples) != 3:
            raise ValueError('incomplete mobile/desktop samples')
        for j, sample in enumerate(samples):
            if (sample.get('http_status') != 200 or sample.get('chapters') != 7
                    or sample.get('instrumentation_failed') is not False
                    or sample.get('failure_codes') != []
                    or sample.get('cache') != 'disabled'):
                raise ValueError('browser admission or provenance failure')
            if any(not positive_number(sample.get(x)) for x in ('lcp_ms', 'cls')):
                raise ValueError('invalid LCP/CLS')
            if j < 2:
                if (sample.get('viewport') != 390
                        or sample.get('profile') != f'mobile_390_trial_{j + 1}'
                        or sample.get('cpu_slowdown_x') != 4
                        or sample.get('network') != '150ms_RTT_1.6Mbps'
                        or not positive_number(sample.get('page_timing_ms', {}).get('fcp'))):
                    raise ValueError('mobile profile mismatch')
                results[expected].append(sample['lcp_ms'])
                cls[expected].append(sample['cls'])
                fcp[expected].append(sample['page_timing_ms']['fcp'])
            else:
                if (sample.get('viewport') != 1440 or sample.get('profile') != 'desktop_1440'
                        or sample.get('cpu_slowdown_x') != 1):
                    raise ValueError('desktop profile mismatch')
                desktop[expected].append(sample['lcp_ms'])
    for variant in ('early', 'late'):
        hashes = {r['saved_content_sha256'] for r in records if r['variant'] == variant}
        if len(hashes) != 1:
            raise ValueError('saved Gutenberg source drifted within variant')
    a, b = median(results['early']), median(results['late'])
    budget = all(v <= 2500 for v in results['early'])
    return {
        'exact_head_sha': expected_sha,
        'environment': 'DISPOSABLE_LOCAL_WORDPRESS_SAVED_GUTENBERG',
        'sample_order': 'ABBA',
        'early_lcp_ms': results['early'],
        'late_lcp_ms': results['late'],
        'early_lcp_median_ms': a,
        'late_lcp_median_ms': b,
        'observed_lcp_delta_ms': b-a,
        'observed_early_improvement_pct': round(100*(b-a)/b, 2) if b else None,
        'fcp_median_ms': {k: median(v) for k,v in fcp.items()},
        'cls_max': {k: max(v) for k,v in cls.items()},
        'desktop_lcp_median_ms': {k: median(v) for k,v in desktop.items()},
        'four_first_screen_pngs_byte_identical': True,
        'early_mobile_lcp_budget_2500ms': 'PASS' if budget else 'FAIL',
        'causal_proof': False,
        'field_cwv': 'NOT_MEASURED',
        'hosted_wordpress_com': 'NOT_TESTED',
        'release_decision': 'HOLD',
    }


def audit_archive(path: Path, expected_digest: str, exact_head: str) -> dict:
    if len(expected_digest) != 64 or any(c not in '0123456789abcdef' for c in expected_digest):
        raise ValueError('invalid pinned artifact sha256')
    actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_digest != expected_digest:
        raise ValueError('CI artifact digest mismatch')
    with ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('archive duplicate member')
        if RECEIPT not in names or any(x not in names for x in IMAGE_PATHS):
            raise ValueError('missing required lab evidence')
        if z.getinfo(RECEIPT).file_size > 120_000:
            raise ValueError('unreasonable receipt size')
        evidence = json.loads(z.read(RECEIPT))
        images = [z.read(x) for x in IMAGE_PATHS]
    result = adjudicate(evidence, images, exact_head)
    result['verified_ci_artifact_sha256'] = actual_digest
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--head', required=True)
    args = p.parse_args()
    try:
        report = audit_archive(args.artifact, args.sha256, args.head)
    except (ValueError, KeyError, TypeError, OSError, BadZipFile, json.JSONDecodeError) as exc:
        print(json.dumps({'verification':'FAIL', 'release_decision':'HOLD', 'error':str(exc)}))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0  # Integrity PASS, *not* performance or release approval.

if __name__ == '__main__':
    raise SystemExit(main())
