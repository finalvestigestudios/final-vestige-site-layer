#!/usr/bin/env python3
"""R432: paragraph-level citation-context and reading-depth custody, REVIEW ONLY.

Consumes R431's original, unselected Git-pinned fork records and blob bytes.
Every detected change is a human-review observation, never a safety, QD,
WordPress, commerce, or publication approval. Deterministic; no network/writes.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
spec = spec_from_file_location('r431_fork_content_delta_gate', HERE / 'r431_fork_content_delta_gate.py')
assert spec and spec.loader
r431 = module_from_spec(spec)
spec.loader.exec_module(r431)
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
TOKEN = re.compile(r'\{\{(?:cite|link):[a-z0-9]+(?:-[a-z0-9]+)*\}\}')
WORD = re.compile(r"\b[\w’'-]+\b", re.UNICODE)
BLOCKS = frozenset(('p', 'li', 'blockquote', 'figcaption', 'dd', 'dt', 'th', 'td', 'pre', 'summary'))
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'))
RISK_GROUPS = {
    'emergency_contacts_privacy': ('contact', 'child', 'school', 'pickup', 'reunification', 'privacy'),
    'medical_dependency': ('medication', 'medical', 'insulin', 'refrigerated', 'oxygen'),
    'combustion_power': ('generator', 'carbon monoxide', 'gas', 'fumes', 'exhaust'),
    'evacuation_fire': ('evacuation', 'evacuate', 'fire', 'smoke', 'shelter'),
}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def normal(text):
    return ' '.join(text.split())


class Blocks(HTMLParser):
    """Heuristic editorial paragraph inventory, not a CSS/browser rendering engine."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.active = None
        self.parts = []
        self.items = []
        self.outside = []

    def flush(self):
        if self.active is None:
            return
        raw = normal(''.join(self.parts))
        if raw:
            self.items.append((self.active, raw))
        self.active, self.parts = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = (self.stack[-1][1] if self.stack else False) or tag in (
            'script', 'style', 'template', 'svg', 'noscript') or 'hidden' in attrs or (
            attrs.get('aria-hidden', '').strip().lower() == 'true') or bool(re.search(
            r'(^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\b', attrs.get('style') or '', re.I))
        if tag in BLOCKS or re.fullmatch(r'h[1-6]', tag):
            self.flush()
            if not hidden:
                self.active, self.parts = tag, []
        if tag not in VOID:
            self.stack.append((tag, bool(hidden)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.active == tag:
            self.flush()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not (self.stack and self.stack[-1][1]):
            if self.active is not None:
                self.parts.append(data)
            elif normal(data):
                self.outside.append(normal(data))

    def finish(self):
        self.flush()
        return self.items


def passage_inventory(raw):
    # Reuse R431's strict UTF-8, token, NUL and candidate validation first.
    prior = r431.inspect_bytes('sample.body.html', raw)
    p = Blocks()
    p.feed(raw.decode('utf-8'))
    p.close()
    rows, source_contexts = [], defaultdict(list)
    for kind, text in p.finish():
        ids = CITE.findall(text)
        stripped = normal(TOKEN.sub(' ', text))
        terms = WORD.findall(stripped)
        content_hash = hashlib.sha256(stripped.casefold().encode()).hexdigest()
        tags = sorted(k for k, words in RISK_GROUPS.items()
                      if any(re.search(r'(?<!\w)' + re.escape(w) + r'(?!\w)', stripped, re.I) for w in words))
        row = {'kind': kind, 'words': len(terms), 'body_sha256': content_hash,
               'citation_ids_in_order': ids, 'risk_review_tags': tags}
        rows.append(row)
        for sid in ids:
            source_contexts[sid].append(content_hash)
    # This is a caution about text outside supported blocks, not an approval.
    coverage = sum(v['words'] for v in rows)
    return {'passages': rows, 'citation_contexts': {k: sorted(v) for k, v in sorted(source_contexts.items())},
            'unanchored_text_found': bool(p.outside),
            'unanchored_text_word_estimate': sum(len(WORD.findall(x)) for x in p.outside),
            'passage_words_estimate': coverage,
            'r431_visible_words_estimate': prior['visible_words_estimate'],
            'paragraph_measure_is_not_rendered_depth': True}


def compare(a, b):
    ar, br = a['passages'], b['passages']
    ac = Counter((x['kind'], x['body_sha256']) for x in ar)
    bc = Counter((x['kind'], x['body_sha256']) for x in br)
    ah = Counter(x['body_sha256'] for x in ar if x['kind'] in ('h1','h2','h3','h4','h5','h6'))
    bh = Counter(x['body_sha256'] for x in br if x['kind'] in ('h1','h2','h3','h4','h5','h6'))
    removed = []
    for (kind, sha), n in sorted((ac - bc).items()):
        source = next(x for x in ar if x['kind'] == kind and x['body_sha256'] == sha)
        removed.append({'kind': kind, 'body_sha256': sha, 'count': n,
                        'words_each': source['words'], 'risk_review_tags': source['risk_review_tags'],
                        'citations_from_passage': source['citation_ids_in_order']})
    added = sum((bc-ac).values())
    moved = []
    for sid in sorted(set(a['citation_contexts']) & set(b['citation_contexts'])):
        old, new = Counter(a['citation_contexts'][sid]), Counter(b['citation_contexts'][sid])
        if old != new:
            moved.append({'source_id': sid,
                          'old_context_occurrences_lost': sum((old-new).values()),
                          'new_context_occurrences': sum((new-old).values())})
    return {'same_full_passage_sequence': ar == br,
            'passages_lost_or_changed': removed, 'passages_added_or_changed_count': added,
            'original_words_in_lost_or_changed_passages': sum(x['words_each']*x['count'] for x in removed),
            'headings_lost_or_changed_count': sum((ah-bh).values()),
            'citation_context_reassignments': moved,
            'visible_word_delta_b_minus_a': b['r431_visible_words_estimate']-a['r431_visible_words_estimate'],
            'requires_human_claim_and_source_review': True}


def held(errors, cases=(), receipt=None):
    return {'schema': 1, 'issue': 136, 'conversion_issue': 820,
            'release_state': 'DRAFT_HARD_HOLD', 'eligible': False,
            'publication_approved': False, 'qualified_safety_approved': False,
            'verified_paid_orders': None, 'net_revenue_per_1000_qualified_human_sessions': None,
            'original_forks': 9, 'source_disputes_unresolved': 5,
            'body_forks_covered': sum(c['path'].endswith('.body.html') for c in cases),
            'errors': sorted(set(errors)), 'body_review_cases': list(cases),
            'review_receipt_sha256': receipt,
            'native_35_article_build': 'NOT_TESTED_BY_R432',
            'wordpress_preview_export_parity': 'NOT_TESTED_BY_R432',
            'citation_adequacy_and_emergency_safety': 'QUALIFIED_REVIEW_REQUIRED',
            'commerce_and_campaign_authentication': 'NOT_VERIFIED'}


def audit(docket, blob_root, *, raw_docket=None, test_only=False):
    parent = r431.audit(docket, blob_root, raw_docket=raw_docket, test_only=test_only)
    if not parent['all_original_fork_bytes_verified'] or parent['errors']:
        return held(['R432_ORIGINAL_R431_CUSTODY_FAILED'] + parent['errors'])
    errors, cases = [], []
    for case in parent['fork_reviews']:
        if not case['path'].endswith('.body.html'):
            continue
        records = []
        for v in case['candidates']:
            try:
                raw = r431.safe_blob(blob_root, v['sha'], v['bytes'])
                inv = passage_inventory(raw)
                if inv['unanchored_text_found']:
                    errors.append('R432_UNANCHORED_EDITORIAL_TEXT:' + case['path'] + ':' + v['branch'])
                records.append({'branch': v['branch'], 'git_blob_sha': v['sha'],
                                'original_branch_pin': v['branch_pin'], 'inventory': inv,
                                'human_selected': False})
            except (OSError, ValueError, UnicodeError, TypeError, OverflowError) as ex:
                errors.append('R432_INVALID_BODY:' + case['path'] + ':' + v['branch'] + ':' + type(ex).__name__)
        records.sort(key=lambda r:r['branch'])
        comparisons = [{'a_branch': x['branch'], 'b_branch': y['branch'],
                        **compare(x['inventory'], y['inventory'])}
                       for i,x in enumerate(records) for y in records[i+1:]]
        cases.append({'path': case['path'], 'candidate_count': len(records),
                      'candidates': records, 'comparisons': comparisons,
                      'state': 'UNSELECTED_QUALIFIED_HUMAN_REVIEW'})
        if len(records) != case['original_candidate_count']:
            errors.append('R432_INCOMPLETE_BODY_FORK:' + case['path'])
    if len(cases) != 4:
        errors.append('R432_EXPECTED_FOUR_BODY_FORKS')
    receipt = digest({'parent_receipt': parent['review_receipt_sha256'], 'cases': cases}) if not errors else None
    return held(errors, cases, receipt)


def main(argv=None):
    ap=argparse.ArgumentParser(description='Read-only original body paragraph/citation context review; ALWAYS HOLD')
    ap.add_argument('original_r397_docket',type=Path)
    ap.add_argument('candidate_blob_directory',type=Path)
    args=ap.parse_args(argv)
    try:
        f=args.original_r397_docket
        if f.is_symlink() or not f.is_file() or f.stat().st_nlink != 1 or not 0 < f.stat().st_size <= r431.MAX:
            raise ValueError('unsafe docket')
        raw=f.read_bytes()
        result=audit(r431.strict_json(raw),args.candidate_blob_directory,raw_docket=raw)
    except (OSError,ValueError,TypeError,UnicodeError,OverflowError) as ex:
        result=held(['R432_INPUT_UNAVAILABLE_OR_INVALID:'+type(ex).__name__])
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2


if __name__=='__main__':
    sys.exit(main())
