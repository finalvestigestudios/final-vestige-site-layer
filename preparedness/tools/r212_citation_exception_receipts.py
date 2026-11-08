#!/usr/bin/env python3
"""R212: source-bound, never-approving receipts for three held citations.

Issue #136. Reads only authentic frozen Start Here files with R211's safe reader.
A HOLD result is neither an editorial nor a medical-safety approval.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r212-exception-receipts-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
FROZEN_HEAD = '2122d856fce9f64887c16df3d52e64be9f59a55b'
A7 = 'preparedness/content/articles/homemade-water-filters'
A20 = 'preparedness/content/articles/preparedness-real-households'
REGISTER = 'preparedness/sources/register.json'
START = 'preparedness/sources/fragments/start.json'
PINS = {
 A7+'.body.html': '67aa44e9a332f57fb70298a3867410d8f66c8c15',
 A7+'.meta.json': '33789d3db0ec06007deb50d0293361f07cea27ae',
 A20+'.body.html': '70d03c366e10db623929f118501becfa26c48bab',
 A20+'.meta.json': 'a0c3a09143a825560b5a5ed79d857b7402bfa295',
 REGISTER: 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
 START: '29574c328cbab0548e6e5d4a026694857d56b6b4',
}
HELD = {
 'cdc-find-clean-water': {'article': 7, 'occurrences': 2,
  'url': 'https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html'},
 'start-ready-plan': {'article': 20, 'occurrences': 1,
  'url': 'https://www.ready.gov/plan'},
}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')

class Violation(ValueError):
    pass


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def strict_json(raw: bytes):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise Violation('duplicate JSON key: '+str(key))
            obj[key] = value
        return obj
    def bad_constant(value):
        raise Violation('non-finite JSON constant: '+value)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=bad_constant)


def evaluate(raw: dict[str, bytes], *, expected: dict[str, str] | None = None) -> dict:
    """Immutable evidence ledger. Expected override exists ONLY for isolated tests."""
    report = {'schema': SCHEMA, 'issue': 136, 'conversion_issue': 820,
              'source_head': FROZEN_HEAD, 'state': INVALID, 'files': [],
              'held_occurrences': [], 'errors': [], 'publication_authorized': False,
              'independent_qd_pass': False, 'medically_safe': False,
              'human_link_check_complete': False, 'source_claim_review_complete': False}
    try:
        def require(condition, message):
            if not condition:
                raise Violation(message)
        reference = PINS if expected is None else expected
        require(type(raw) is dict and set(raw) == set(PINS), 'missing or unexpected source files')
        require(type(reference) is dict and set(reference) == set(PINS), 'incomplete blob pins')
        for path in PINS:
            data = raw[path]
            require(type(data) is bytes, 'non-byte source file: '+path)
            expected_sha = reference[path]
            require(type(expected_sha) is str and re.fullmatch('[0-9a-f]{40}', expected_sha), 'invalid SHA pin: '+path)
            found_sha = blob_sha(data)
            require(found_sha == expected_sha, 'source blob drift: '+path)
            report['files'].append({'path': path, 'sha': found_sha, 'bytes': len(data)})
        global_sources = strict_json(raw[REGISTER])
        start_sources = strict_json(raw[START])
        require(type(global_sources) is dict and type(global_sources.get('sources')) is list,
                'global sources schema invalid')
        require(type(start_sources) is dict and type(start_sources.get('sources')) is list,
                'Start Here sources schema invalid')
        # Other historical ID collisions are NOT silently normalized or adjudicated.
        pool = global_sources['sources'] + start_sources['sources']
        require(all(type(x) is dict and type(x.get('id')) is str for x in pool),
                'source entries malformed')
        for number, prefix, target in ((7, A7, 'cdc-find-clean-water'),
                                        (20, A20, 'start-ready-plan')):
            body = raw[prefix+'.body.html'].decode('utf-8')
            meta = strict_json(raw[prefix+'.meta.json'])
            require(type(meta) is dict and meta.get('n') == number and
                    meta.get('slug') == prefix.rsplit('/', 1)[-1], 'article identity drift')
            require(meta.get('status', {}).get('publish') == 'draft' and
                    meta.get('safety_review', {}).get('state') == 'pending',
                    'unexpected article publication or safety status')
            source_use = meta.get('source_use')
            require(type(source_use) is dict, 'article source explanations absent')
            cites = list(CITE.finditer(body))
            require(cites and body.count('{{cite:') == len(cites), 'malformed citation marker')
            cited_ids = {m.group(1) for m in cites}
            require(set(source_use) == (cited_ids - {target}),
                    'missing/extra explanations beyond known held exception')
            require(all(type(s) is str and s.strip() for s in source_use.values()),
                    'empty source-use explanation')
            require(target not in source_use, 'held source-use explanation changed; re-review required')
            matches = [m for m in cites if m.group(1) == target]
            require(len(matches) == HELD[target]['occurrences'],
                    'held occurrence count changed')
            source_records = [x for x in pool if x.get('id') == target]
            require(len(source_records) == 1, 'held source is absent or disputed by duplicate records')
            record = source_records[0]
            require(record.get('url') == HELD[target]['url'], 'held URL unexpectedly changed')
            require(record.get('human_link_check') is False, 'human link check changed; adjudication required')
            require(all(x in cited_ids or x == target for x in source_use),
                    'unused source explanations present')
            for occurrence, match in enumerate(matches, 1):
                # Exact byte offsets, not Python Unicode character positions.
                byte_start = len(body[:match.start()].encode('utf-8'))
                byte_end = len(body[:match.end()].encode('utf-8'))
                window = body[max(0, match.start()-240):min(len(body), match.end()+240)]
                fingerprint = hashlib.sha256((str(number)+'\0'+target+'\0'+
                    blob_sha(raw[prefix+'.body.html'])+'\0'+str(byte_start)+'\0'+
                    window).encode('utf-8')).hexdigest()
                report['held_occurrences'].append({
                    'article': number, 'source_id': target, 'occurrence': occurrence,
                    'body_sha': blob_sha(raw[prefix+'.body.html']),
                    'byte_span': [byte_start, byte_end], 'receipt_sha256': fingerprint,
                    'source_url': record['url'], 'human_link_check': False,
                    'claim_support_review': 'PENDING', 'action': 'HUMAN_ADJUDICATION_REQUIRED'})
        require(len(report['held_occurrences']) == 3, 'not exactly three held citations')
        report['state'] = HOLD
    except (ValueError, UnicodeError, TypeError, KeyError, IndexError, AttributeError) as exc:
        report['errors'].append(str(exc))
    return report


def read_checkout(root: Path):
    path = Path(__file__).with_name('r211_path_guard.py')
    spec = importlib.util.spec_from_file_location('fv_r211_guard_for_r212', path)
    if spec is None or spec.loader is None:
        raise Violation('missing I/O safety guard')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.read_files(root, PINS)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='R212 citation exception preflight: never release')
    parser.add_argument('--checkout', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = evaluate(read_checkout(args.checkout))
    except (OSError, ValueError, ImportError) as exc:
        report = {'schema': SCHEMA, 'issue': 136, 'state': INVALID,
                  'publication_authorized': False, 'independent_qd_pass': False,
                  'medically_safe': False, 'errors': [str(exc)]}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if report['state'] == HOLD else 3

if __name__ == '__main__':
    raise SystemExit(main())
