#!/usr/bin/env python3
"""R110 private adjacent uncited-caveat custody — reviewer workorder, never PASS.

R109 hashes a citation's own block. Changing an adjacent *uncited* warning
can reframe an unchanged cited paragraph; track same-section neighboring text
without exporting advice, declaring source support, or writing to the CMS.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = 'r110-adjacent-uncited-caveat-custody-HOLD-v1'
TOKEN = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
INTENT = re.compile(r'\{\{cite:')
SPACE = re.compile(r'\s+')
BLOCK = frozenset('p li td th dt dd blockquote figcaption h1 h2 h3 h4 h5 h6'.split())
HEADINGS = frozenset('h1 h2 h3 h4 h5 h6'.split())
SUPPRESSED = frozenset('script style template noscript svg math'.split())
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
WARN_CLASSES = frozenset('pa-act pa-tag--unc pa-warning pa-alert pa-caution pa-safety'.split())
MAX_BYTES = 2_000_000
MAX_BLOCKS = 40_000
MAX_CITES = 20_000
ADJACENCY = 2

class Hold(ValueError):
    """Evidence too ambiguous for auto clearance."""

def require(condition: bool, message: str):
    if not condition:
        raise Hold(message)

def sha(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def norm(value: str) -> str:
    return SPACE.sub(' ', value).strip()

class _Blocks(HTMLParser):
    """Conservative HTMLParser block model; NOT a browser renderer."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.blocks: list[dict] = []
        self.section = 0
        self.ambiguities = 0
        self.orphan_citations = 0
        self.invisible_citations = 0
        self.attribute_citations = 0
        self.comment_citations = 0
        self.invalid_tokens = 0
        self.citations = 0

    def start(self, tag: str, attrs: list):
        at = dict(attrs)
        for _, val in attrs:
            if isinstance(val, str) and INTENT.search(val):
                self.attribute_citations += len(TOKEN.findall(val))
                self.invalid_tokens += len(INTENT.findall(val)) - len(TOKEN.findall(val))
        hidden = (tag in SUPPRESSED or 'hidden' in at or
                  (at.get('aria-hidden') or '').strip().lower() == 'true' or
                  re.search(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\b',
                            at.get('style') or '', re.I) is not None)
        warning = (bool(WARN_CLASSES & set((at.get('class') or '').split())) or
                   (at.get('role') or '').lower() == 'alert')
        if tag in HEADINGS:
            self.section += 1
        bid = None
        if tag in BLOCK:
            require(len(self.blocks) < MAX_BLOCKS, 'too many text blocks')
            bid = len(self.blocks)
            self.blocks.append({'tag': tag, 'pieces': [], 'section': self.section,
                                'warning': warning or any(f['warning'] for f in self.stack),
                                'hidden': hidden or any(f['hidden'] for f in self.stack)})
        if tag not in VOID:
            self.stack.append({'tag': tag, 'bid': bid, 'hidden': hidden, 'warning': warning})

    def handle_starttag(self, tag, attrs):
        self.start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.start(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.ambiguities += 1
            return
        if self.stack[-1]['tag'] == tag:
            self.stack.pop()
            return
        self.ambiguities += 1
        index = next((i for i in range(len(self.stack)-1, -1, -1)
                      if self.stack[i]['tag'] == tag), -1)
        if index >= 0:
            del self.stack[index:]

    def handle_data(self, data):
        if any(f['hidden'] for f in self.stack):
            self.invisible_citations += len(TOKEN.findall(data))
            self.invalid_tokens += len(INTENT.findall(data)) - len(TOKEN.findall(data))
            return
        bid = next((f['bid'] for f in reversed(self.stack) if f['bid'] is not None), None)
        if bid is None:
            self.orphan_citations += len(TOKEN.findall(data))
            self.invalid_tokens += len(INTENT.findall(data)) - len(TOKEN.findall(data))
        else:
            self.blocks[bid]['pieces'].append(data)

    def handle_comment(self, data):
        self.comment_citations += len(TOKEN.findall(data))
        self.invalid_tokens += len(INTENT.findall(data)) - len(TOKEN.findall(data))

    def summarize(self):
        self.ambiguities += len(self.stack)
        rows = []
        for block in self.blocks:
            value = norm(''.join(block['pieces']))
            ids = TOKEN.findall(value)
            self.invalid_tokens += len(INTENT.findall(value)) - len(ids)
            self.citations += len(ids)
            rows.append({'section': block['section'], 'tag': block['tag'],
                         'ids': ids, 'sha': sha(value), 'warning': block['warning'],
                         'nonempty': bool(value)})
        require(self.citations <= MAX_CITES, 'too many citations')
        by_source = defaultdict(list)
        heading_by_section = {0: sha('ROOT')}
        for row in rows:
            if row['tag'] in HEADINGS:
                heading_by_section[row['section']] = row['sha']
        for i, row in enumerate(rows):
            if not row['ids']:
                continue
            wing = []
            for direction in (-1, 1):
                for step in range(1, ADJACENCY + 1):
                    j = i + direction * step
                    if not 0 <= j < len(rows):
                        break
                    candidate = rows[j]
                    if candidate['section'] != row['section']:
                        break
                    if candidate['ids'] or candidate['tag'] in HEADINGS:
                        break
                    wing.append((direction, step, candidate['tag'], candidate['sha'],
                                 candidate['warning'], candidate['nonempty']))
            fingerprint = sha(json.dumps([heading_by_section.get(row['section']), wing],
                                        sort_keys=True, separators=(',', ':')))
            any_warning = any(w[4] for w in wing)
            for sid in row['ids']:
                by_source[sid].append({'adjacent_sha256': fingerprint,
                                       'adjacent_warning_present': any_warning,
                                       'adjacent_uncited_blocks': len(wing)})
        return {
            'source_adjacency': {
                sid: sorted(vals, key=lambda v: (v['adjacent_sha256'],
                           v['adjacent_warning_present'], v['adjacent_uncited_blocks']))
                for sid, vals in sorted(by_source.items())},
            'visible_citation_count_text_model': self.citations,
            'source_ids': sorted(by_source),
            'uncited_block_count': sum(1 for x in rows if x['nonempty'] and not x['ids'] and x['tag'] not in HEADINGS),
            'adjacent_warning_context_total': sum(v['adjacent_warning_present'] for vals in by_source.values() for v in vals),
            'html_ambiguities': self.ambiguities,
            'malformed_markers': self.invalid_tokens,
            'orphan_citations': self.orphan_citations,
            'invisible_citations': self.invisible_citations,
            'attribute_citations': self.attribute_citations,
            'comment_citations': self.comment_citations,
            'text_model_only': True,
        }

def inspect(raw: bytes) -> dict:
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'not bytes or oversized article')
    try:
        content = raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise Hold('invalid UTF-8 article') from exc
    parser = _Blocks()
    parser.feed(content)
    parser.close()
    return parser.summarize()

def compare(old: bytes, new: bytes) -> dict:
    before, after = inspect(old), inspect(new)
    a, b = before['source_adjacency'], after['source_adjacency']
    common = set(a) & set(b)
    changed = sorted(sid for sid in common
                     if Counter(x['adjacent_sha256'] for x in a[sid]) !=
                        Counter(x['adjacent_sha256'] for x in b[sid]))
    warnings = sorted(sid for sid in common
                      if Counter((x['adjacent_warning_present'], x['adjacent_uncited_blocks']) for x in a[sid]) !=
                         Counter((x['adjacent_warning_present'], x['adjacent_uncited_blocks']) for x in b[sid]))
    return {
        'same_source_id_adjacent_uncited_context_changed_NOT_APPROVED': changed,
        'source_ids_with_adjacent_warning_presence_or_span_changed_NOT_APPROVED': warnings,
        'source_ids_added': sorted(set(b)-set(a)),
        'source_ids_removed': sorted(set(a)-set(b)),
        'source_ids_in_both': sorted(common),
        'visible_citations_before': before['visible_citation_count_text_model'],
        'visible_citations_after': after['visible_citation_count_text_model'],
        'uncited_block_count_before': before['uncited_block_count'],
        'uncited_block_count_after': after['uncited_block_count'],
        'text_model_ambiguity_or_nontext_citations': any(
            x[k] for x in (before, after) for k in
            ('html_ambiguities', 'malformed_markers', 'orphan_citations',
             'invisible_citations', 'attribute_citations', 'comment_citations')),
        'all_modified_advice_requires_human_review': True,
        'underlying_source_support_verified': False,
        'qualified_safety_review_approved': False,
        'independent_QD_PASS': False,
        'may_publish': False,
    }

def scan(root: Path) -> dict:
    """Re-run R107/R109 Git custody; add reviewer-only adjacency signals."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import r109_citation_context_custody as r109
    import r107_exact_branch_progression_adjudication as r107
    import r108_source_citation_change_impact_crosswalk as r108
    r109_docket = r109.scan(root)
    r107_docket = r107.scan(root)
    tips = {entry['origin']: entry for entry in r107_docket['seven_contributor_commit_ancestry']}
    rows = []
    for row in r109_docket['rows_NOT_APPROVED']:
        origin, path = row['origin'], row['path']
        tip = tips[origin]
        require(row['frozen_oid'] and row['observed_oid'],
                'created/removed body remains outside R110 adjacency model')
        old = r108.git_object(root, tip['frozen_commit_sha'], path)
        new = r108.git_object(root, tip['observed_commit_sha'], path)
        require(r107.r60.blob_sha(old) == row['frozen_oid'] and
                r107.r60.blob_sha(new) == row['observed_oid'],
                'changed-body Git OID mismatch after R109 workorder')
        rows.append({'origin': origin, 'path': path, 'frozen_oid': row['frozen_oid'],
                     'observed_oid': row['observed_oid'],
                     'cross_paragraph_review_NOT_APPROVED': compare(old, new),
                     'human_source_review': 'NOT_REVIEWED', 'may_publish': False})
    result = {'schema': SCHEMA, 'issue': 136, 'release_state': 'HOLD',
              'may_publish': False, 'independent_QD_PASS': False,
              'qualified_emergency_safety_approved': False,
              'R109_sha256_NOT_A_SIGNATURE': r109_docket['sha256_NOT_A_SIGNATURE'],
              'changed_body_review_count': len(rows),
              'rows_NOT_APPROVED': sorted(rows, key=lambda r: (r['origin'], r['path'])),
              'review_required': 'Inspect adjacent uncited caveats in original and revised prose against source readings; no factual or safety approval inferred.'}
    result['sha256_NOT_A_SIGNATURE'] = sha(json.dumps(
        result, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False))
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    result = scan(args.repo_root.resolve())
    if args.json:
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({'schema': SCHEMA, 'release_state': 'HOLD',
                          'may_publish': False,
                          'changed_body_review_count': result['changed_body_review_count'],
                          'sha256_NOT_A_SIGNATURE': result['sha256_NOT_A_SIGNATURE']},
                         sort_keys=True))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Hold, KeyError, OSError, ValueError) as exc:
        print('R110 PRIVATE CAVEAT CUSTODY HOLD: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
