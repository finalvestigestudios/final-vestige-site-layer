#!/usr/bin/env python3
"""Fail-closed audit of Apollo actual-page Chromium evidence. Does NOT certify production readiness.

Usage: python qa_r125_assurance.py --receipt /path/R113_BROWSER_RECEIPT.json \
       --expected-blob <GitHub landing-preview.html blob SHA> --out /path/R125_ASSURANCE.json
No network, installs, analytics or writes outside --out.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
AXE_STATES = {(390, 'all'), (390, 'limit'), (1440, 'all'), (1440, 'limit')}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def blob_id(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def assess(receipt_path, expected_blob, root=BASE):
    receipt_path = Path(receipt_path).resolve()
    root = Path(root).resolve()
    html = root / 'landing-preview.html'
    runner = root / 'qa_r113_print.py'
    data = json.loads(receipt_path.read_text(encoding='utf-8'))
    checks = {}
    if html.is_file() and runner.is_file():
        checks['exact_github_html_blob'] = blob_id(html.read_bytes()) == expected_blob
        checks['runner_present'] = True
        checks['receipt_matches_html'] = data.get('source_sha256') == digest(html)
    else:
        checks['exact_github_html_blob'] = checks['runner_present'] = checks['receipt_matches_html'] = False
    checks['source_gate'] = data.get('source_identity') == 'EXACT_GIT_HEAD' and data.get('classification') == 'actual-source'
    expected = {f'{width}px-js-{int(js)}' for width in WIDTHS for js in (False, True)}
    modes = data.get('modes', [])
    checks['full_responsive_matrix'] = len(modes) == 14 and set(modes) == expected
    perf = data.get('performance', [])
    seen = {(p.get('width'), p.get('trial')) for p in perf}
    def good_perf(p):
        lcp, cls = p.get('lcp_ms'), p.get('cls')
        return (isinstance(lcp, (float, int)) and not isinstance(lcp, bool)
                and isinstance(cls, (float, int)) and not isinstance(cls, bool)
                and math.isfinite(lcp) and math.isfinite(cls)
                and 0 <= lcp <= 2500 and 0 <= cls <= 0.1 and p.get('lab_only') is True)
    checks['six_lab_performance_trials'] = (len(perf) == 6
        and seen == {(w, t) for w in (390, 1440) for t in (1, 2, 3)}
        and all(good_perf(p) for p in perf))
    shots = data.get('screenshots', {})
    checks['screenshots_sha256'] = (set(shots) == {'R113_WEB_390.png', 'R113_WEB_1440.png'}
        and all((receipt_path.parent / name).is_file()
                and digest(receipt_path.parent / name) == hash_value
                and (receipt_path.parent / name).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
                for name, hash_value in shots.items()))
    for label, key in (('complete_packet_pdf', 'pdf'), ('student_only_pdf', 'worksheet_pdf')):
        item = data.get(key) or {}
        name = item.get('name', '')
        candidate = receipt_path.parent / name if name and '/' not in name and '\\' not in name else None
        checks[label] = bool(candidate and candidate.is_file()
                            and candidate.read_bytes().startswith(b'%PDF-')
                            and digest(candidate) == item.get('sha256'))
    axe = data.get('axe_scans', [])
    checks['axe_four_unambiguous_scans'] = (len(axe) == 4
        and {(v.get('width'), v.get('state')) for v in axe} == AXE_STATES
        and all(v.get('violations') == 0 and v.get('incomplete') == 0
                and isinstance(v.get('passes'), int) and v['passes'] >= 30 for v in axe))
    files = [receipt_path]
    for name in sorted(shots):
        p = receipt_path.parent / name
        if p.is_file(): files.append(p)
    for k in ('pdf', 'worksheet_pdf'):
        v = data.get(k) or {}
        p = receipt_path.parent / v.get('name', '') if v.get('name') else None
        if p and p.is_file(): files.append(p)
    paths = {p.name: {'size': p.stat().st_size, 'sha256': digest(p)} for p in sorted(files)}
    pre_axe = all(v for k, v in checks.items() if k != 'axe_four_unambiguous_scans')
    status = ('BROWSER_PARTIAL_AXE_REQUIRED' if pre_axe and not checks['axe_four_unambiguous_scans']
              else 'BROWSER_QA_CHECKED_NOT_RELEASE_APPROVED' if all(checks.values()) else 'FAILED_OR_INCOMPLETE')
    return {'classification': status, 'release_gate': 'STAGING_HOLD',
            'expected_github_blob': expected_blob,
            'actual_html_blob': blob_id(html.read_bytes()) if html.is_file() else None,
            'chromium_version': data.get('browser'), 'checks': checks,
            'artifact_sha256_manifest': paths,
            'limitations': ['Local Chromium lab evidence, not field CWV or production traffic.',
                            'No merchant order, approved product, rights clearance, WordPress acceptance or founder release implied.',
                            'Axe scans MUST use a verified local bundle; incomplete/manual-review results cannot pass.']}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--expected-blob', required=True, help='Git blob from authenticated GitHub fetch_file')
    parser.add_argument('--out', type=Path, required=True)
    a = parser.parse_args()
    result = assess(a.receipt, a.expected_blob)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'classification': result['classification'], 'checks': result['checks']}, sort_keys=True))
    return 0 if result['classification'] == 'BROWSER_QA_CHECKED_NOT_RELEASE_APPROVED' else 2

if __name__ == '__main__':
    raise SystemExit(main())
