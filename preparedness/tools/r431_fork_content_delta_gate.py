#!/usr/bin/env python3
"""R431: exact original-fork byte custody and loss-of-depth comparison. DRAFT ONLY.

Consumes the original Git-pinned R397 docket, plus *locally supplied* original
Git blob bytes named <sha>.blob. Produces review deltas, never picks a winner,
proves a public citation, or permits publishing/payment/safety approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
spec = spec_from_file_location('r430_conflict_adjudication_escrow', HERE / 'r430_conflict_adjudication_escrow.py')
assert spec and spec.loader
r430 = module_from_spec(spec)
spec.loader.exec_module(r430)
TOKEN = re.compile(r'\{\{(cite|link):([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
WORD = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
MAX = 2_000_000


class Reader(HTMLParser):
    """Conservative text inventory; visibility estimates are NOT browser/QD proof."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.tags = []
        self.text = []
        self.heading = None
        self.headings = []
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = (self.hidden[-1] if self.hidden else False) or tag in (
            'script', 'style', 'template', 'svg', 'noscript') or 'hidden' in attrs or (
            attrs.get('aria-hidden') == 'true') or re.search(
            r'(^|;)\s*display\s*:\s*none\b', attrs.get('style') or '', re.I) is not None
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.hidden.append(bool(hidden))
            self.tags.append(tag)
        if not hidden and tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading = [tag, []]
        if not hidden and tag == 'a' and isinstance(attrs.get('href'), str):
            self.hrefs.append(attrs['href'])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.tags:
            i = len(self.tags) - 1 - self.tags[::-1].index(tag)
            del self.tags[i:]
            del self.hidden[i:]
        if self.heading and self.heading[0] == tag:
            self.headings.append(' '.join(' '.join(self.heading[1]).split())[:140])
            self.heading = None

    def handle_data(self, data):
        if not any(self.hidden):
            self.text.append(data)
            if self.heading:
                self.heading[1].append(data)


def strict_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=r430.unique_pairs,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))


def safe_blob(root: Path, sha: str, length: int):
    """Bounded files in a reviewer-owned directory; no symlinks/hardlinks/escapes."""
    if not isinstance(root, Path) or root.is_symlink() or not root.is_dir():
        raise ValueError('unsafe blob directory')
    if not isinstance(sha, str) or not r430.SHA40.fullmatch(sha) or type(length) is not int or not 0 < length <= MAX:
        raise ValueError('invalid expected blob')
    f = root / (sha + '.blob')
    fd = os.open(f, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size != length or st.st_size > MAX:
            raise ValueError('nonregular, linked, oversized or changed candidate')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(MAX + 1)
        if len(raw) != length or r430.git_blob(raw) != sha:
            raise ValueError('wrong Git object bytes')
        return raw
    finally:
        os.close(fd)


def inspect_bytes(path, raw):
    text = raw.decode('utf-8')
    if '\x00' in text:
        raise ValueError('NUL in editorial bytes')
    if path.endswith('.body.html'):
        r = Reader()
        r.feed(text)
        r.close()
        visible = ' '.join(r.text)
        tokens = TOKEN.findall(visible)
        if visible.count('{{cite:') != sum(k == 'cite' for k, _ in tokens) or \
           visible.count('{{link:') != sum(k == 'link' for k, _ in tokens):
            raise ValueError('unrecognized or malformed source token')
        return {'kind': 'BODY', 'visible_words_estimate': len(WORD.findall(visible)),
                'headings_in_order': r.headings,
                'citation_ids_in_order': [sid for k, sid in tokens if k == 'cite'],
                'article_links_in_order': [sid for k, sid in tokens if k == 'link'],
                'literal_href_in_order': r.hrefs,
                'reading_depth_estimate_only': True}
    if path.endswith('.meta.json') or path.endswith('.json'):
        obj = strict_json(raw)
        if not isinstance(obj, dict):
            raise ValueError('JSON artifact must be an object')
        if '\\u0000' in json.dumps(obj, ensure_ascii=True).lower():
            raise ValueError('NUL in JSON editorial values')
        return {'kind': 'META' if path.endswith('.meta.json') else 'SOURCE_FRAGMENT',
                'root_keys': sorted(obj),
                'source_ids_in_source_array': [v.get('id') for v in obj.get('sources', []) if isinstance(v, dict)]
                if isinstance(obj.get('sources'), list) else [],
                'source_count': len(obj.get('sources', [])) if isinstance(obj.get('sources'), list) else None}
    raise ValueError('unsupported fork path')


def delta(a, b):
    result = {'a_branch': a['branch'], 'b_branch': b['branch'],
              'same_blob': a['sha'] == b['sha'], 'selected': None}
    ma, mb = a['metrics'], b['metrics']
    if ma['kind'] == 'BODY' and mb['kind'] == 'BODY':
        ac, bc = Counter(ma['citation_ids_in_order']), Counter(mb['citation_ids_in_order'])
        ah, bh = Counter(ma['headings_in_order']), Counter(mb['headings_in_order'])
        result.update({'visible_word_delta_b_minus_a': mb['visible_words_estimate'] - ma['visible_words_estimate'],
                       'citations_removed_from_b': sorted((ac - bc).elements()),
                       'citations_added_in_b': sorted((bc - ac).elements()),
                       'headings_removed_from_b': sorted((ah - bh).elements()),
                       'headings_added_in_b': sorted((bh - ah).elements()),
                       'citation_sequence_changed': ma['citation_ids_in_order'] != mb['citation_ids_in_order'],
                       'href_sequence_changed': ma['literal_href_in_order'] != mb['literal_href_in_order']})
    else:
        result['structured_candidate_changed'] = a['sha'] != b['sha']
    return result


def held(errors, cases=(), digest=None):
    return {'schema': 1, 'issue': 136, 'conversion_issue': 820, 'release_state': 'DRAFT_HARD_HOLD',
            'eligible': False, 'publication_approved': False, 'qualified_safety_approved': False,
            'merchant_offer_verified': False, 'paid_activation_approved': False,
            'verified_orders': None, 'net_revenue_per_1000_qualified_human_sessions': None,
            'all_original_fork_bytes_verified': not errors and len(cases) == 9,
            'errors': sorted(set(errors)), 'fork_reviews': list(cases),
            'unselected_original_forks': 9, 'source_disputes_unresolved': 5,
            'review_receipt_sha256': digest, 'human_source_and_safety_review': 'REQUIRED',
            'visible_depth_is_not_rendered_browser_validation': True,
            'native_35_article_build_and_70_export_parity': 'NOT_TESTED_BY_R431',
            'paid_conversion_evidence': 'NOT_AUTHENTICATED'}


def audit(docket, blob_root, *, raw_docket=None, test_only=False):
    prior = r430.audit(docket, raw=raw_docket, test_only=test_only)
    if not prior['escrow_structure_ok']:
        return held(['R431_R430_ESCROW_FAILED'] + prior['errors'])
    errors, cases = [], []
    for c in prior['unresolved_cases']:
        if c['kind'] != 'MANUSCRIPT_FORK':
            continue
        variants = []
        for v in c['contenders']:
            try:
                raw = safe_blob(blob_root, v['git_blob_sha'], v['byte_length'])
                metrics = inspect_bytes(c['id'], raw)
                variants.append({'branch': v['branch'], 'branch_pin': v['branch_head_pin'],
                                 'sha': v['git_blob_sha'], 'bytes': len(raw), 'metrics': metrics,
                                 'human_selected': False, 'qualified_source_check': False})
            except (OSError, ValueError, UnicodeError, TypeError, OverflowError) as e:
                errors.append('R431_CANDIDATE_UNAVAILABLE_OR_INVALID:' + c['id'] + ':' + v['branch'] + ':' + type(e).__name__)
        variants.sort(key=lambda v: v['branch'])
        pairs = [delta(a, b) for i, a in enumerate(variants) for b in variants[i+1:]]
        cases.append({'path': c['id'], 'selection': None, 'state': 'HUMAN_REVIEW_REQUIRED',
                      'original_candidate_count': len(c['contenders']),
                      'verified_candidate_count': len(variants),
                      'candidates': variants, 'pairwise_unselected_deltas': pairs})
    if len(cases) != 9 or any(c['verified_candidate_count'] != c['original_candidate_count'] for c in cases):
        errors.append('R431_9_FORK_CANDIDATE_COVERAGE_INCOMPLETE')
    receipt = None
    if not errors:
        obj = {'original': r430.ORIGINAL_GIT_BLOB if not test_only else 'TEST_FIXTURE', 'cases': cases}
        receipt = hashlib.sha256(b'FV-R431-ORIGINAL-FORK-BYTE-REVIEW\0' +
                                 json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
    return held(errors, cases=cases, digest=receipt)


def main(argv=None):
    p = argparse.ArgumentParser(description='Read-only 9 original fork byte comparisons; ALWAYS HARD HOLD')
    p.add_argument('original_r397_docket', type=Path)
    p.add_argument('candidate_blob_directory', type=Path)
    args = p.parse_args(argv)
    try:
        f = args.original_r397_docket
        if f.is_symlink() or not f.is_file() or f.stat().st_nlink != 1 or not 0 < f.stat().st_size <= MAX:
            raise ValueError('unsafe docket file')
        raw = f.read_bytes()
        docket = strict_json(raw)
        result = audit(docket, args.candidate_blob_directory, raw_docket=raw)
    except (OSError, ValueError, UnicodeError, TypeError, OverflowError) as e:
        result = held(['R431_ORIGINAL_DOCKET_UNAVAILABLE_OR_INVALID:' + type(e).__name__])
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2))
    return 2


if __name__ == '__main__':
    sys.exit(main())