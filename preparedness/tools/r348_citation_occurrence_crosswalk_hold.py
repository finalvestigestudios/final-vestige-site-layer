#!/usr/bin/env python3
"""R348: citation occurrence -> original claim-region -> disputed source crosswalk.

Read-only diagnostic. An occurrence is evidence of manuscript citation *placement*,
not evidence of URL validity, substantive claim support, safety, QD or publication.
No private body text, household details, or product/revenue assertions are emitted.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha1, sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re

SCHEMA = 'fv-preparedness-r348-citation-occurrence-crosswalk-v1'
CONFLICTS = frozenset(('fsis-power-failure', 'nchfp-home',
                       'loc-prairie-traveler', 'loc-pioneer-diaries'))
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
CITE_MARKER = '{{cite:'
REGION_TAGS = frozenset(('p', 'li', 'td', 'th', 'blockquote', 'h1', 'h2', 'h3', 'h4'))
VOID_TAGS = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                       'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'))
ALLOWED_STATES = frozenset(('draft',))
PRED_BLOB = '744f5b4d905241532fabd19bc0dab2ac8dd16bd8'
FALSE_GATES = {'may_publish': False, 'may_merge': False, 'qualified_qd_pass': False,
               'safety_claims_approved': False, 'human_source_link_verified': False,
               'independent_claim_support_verified': False,
               'merchant_orders_authenticated': False, 'net_revenue_verified': False,
               'native_wordpress_build_verified': False}


def git_blob(data: bytes) -> str:
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def digest(text: str) -> str:
    return sha256(text.encode('utf-8')).hexdigest()


class CitationParser(HTMLParser):
    """Keep citations anchored to the closest authored semantic text region."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.nodes = []
        self.tokens = []
        self.errors = []
        self.next_id = 0

    def handle_starttag(self, tag, attrs):
        if any(CITE_MARKER in str(v) for _, v in attrs if v is not None):
            self.errors.append('CITATION_TOKEN_INSIDE_ATTRIBUTE')
        self.next_id += 1
        node = {'tag': tag, 'id': self.next_id, 'text': '', 'parent': self.stack[-1] if self.stack else None}
        if tag not in VOID_TAGS:
            self.stack.append(node)
        self.nodes.append(node)
        if tag in ('script', 'style', 'iframe', 'form'):
            self.errors.append('UNEXPECTED_ACTIVE_HTML:' + tag)

    def handle_startendtag(self, tag, attrs):
        if any(CITE_MARKER in str(v) for _, v in attrs if v is not None):
            self.errors.append('CITATION_TOKEN_INSIDE_ATTRIBUTE')

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append('UNBALANCED_HTML_END')
            return
        if self.stack[-1]['tag'] != tag:
            # Do not repair malformed source and invent a claim-region binding.
            self.errors.append('UNBALANCED_HTML_TAGS')
            return
        self.stack.pop()

    def handle_comment(self, data):
        if CITE_MARKER in data:
            self.errors.append('CITATION_TOKEN_INSIDE_COMMENT')

    def handle_data(self, data):
        if not self.stack:
            if CITE_MARKER in data:
                self.errors.append('CITATION_TOKEN_OUTSIDE_HTML')
            return
        for node in self.stack:
            node['text'] += data
        for m in CITE.finditer(data):
            region = next((n for n in reversed(self.stack) if n['tag'] in REGION_TAGS), None)
            if region is None:
                self.errors.append('CITATION_WITHOUT_SEMANTIC_REGION')
            else:
                self.tokens.append((m.group(1), region))
        if CITE_MARKER in CITE.sub('', data):
            self.errors.append('MALFORMED_OR_SPLIT_CITATION_TOKEN')


def inspect_record(slug: str, body: str, meta: dict, kind: str) -> dict:
    """Pure, explicit synthetic-testable inspection; never labels sources trusted."""
    errors = []
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        errors.append('INVALID_SLUG')
    if not isinstance(body, str) or not isinstance(meta, dict):
        return {'slug': slug, 'kind': kind, 'errors': ['INVALID_BODY_OR_METADATA'], 'citations': []}
    if meta.get('slug') != slug:
        errors.append('METADATA_SLUG_DRIFT')
    status = meta.get('status')
    if not isinstance(status, dict) or status.get('publish') not in ALLOWED_STATES:
        errors.append('NON_DRAFT_SOURCE_STATE')
    safety = meta.get('safety_review')
    if not isinstance(safety, dict) or safety.get('state') != 'pending':
        errors.append('SAFETY_REVIEW_STATE_NOT_PENDING')
    source_use = meta.get('source_use')
    if not isinstance(source_use, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in source_use.items()):
        errors.append('INVALID_SOURCE_USE')
        source_use = {}
    parser = CitationParser()
    try:
        parser.feed(body)
        parser.close()
    except (TypeError, ValueError):
        errors.append('HTML_PARSE_FAILURE')
    errors.extend(parser.errors)
    if parser.stack:
        errors.append('UNCLOSED_HTML_TAGS')
    literal = CITE.findall(body)
    if len(literal) != len(parser.tokens):
        errors.append('CITATION_VISIBLE_OCCURRENCE_PARITY_FAILURE')
    if body.count(CITE_MARKER) != len(literal):
        errors.append('MALFORMED_OR_NONVISIBLE_CITATION')
    observed = [sid for sid, _ in parser.tokens]
    unknown = sorted(set(observed) - set(source_use))
    if unknown:
        errors.append('CITED_SOURCE_WITHOUT_SOURCE_USE')
    entries = []
    for ordinal, (source_id, region) in enumerate(parser.tokens, 1):
        # Hash of the *entire* authored semantic region; no source claims copied out.
        region_text = ' '.join(region['text'].split())
        entries.append({'ordinal': ordinal, 'source_id': source_id,
                        'region_tag': region['tag'], 'region_sha256': digest(region_text),
                        'region_word_count': len(region_text.split()),
                        'occurrence_sha256': digest(f'{slug}|{kind}|{ordinal}|{source_id}|{digest(region_text)}')})
    return {'slug': slug, 'kind': kind, 'body_sha256': digest(body),
            'citations': entries, 'errors': sorted(set(errors)),
            'declared_only_source_ids': sorted(set(source_use) - set(observed))}


def crosswalk(root: Path, require_complete: bool = True) -> dict:
    """Inspect 35 article + 6 tool originals without editing them."""
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    contents = prep / 'content'
    errors = []
    rows = []
    for kind, required in (('articles', 35), ('tools', 6)):
        folder = contents / kind
        if folder.is_symlink():
            errors.append('SYMLINKED_CANONICAL_DIRECTORY:' + kind)
            continue
        bodies = sorted(folder.glob('*.body.html'))
        metas = sorted(folder.glob('*.meta.json'))
        if require_complete and (len(bodies) != required or len(metas) != required):
            errors.append('INCOMPLETE_' + kind.upper() + '_CORPUS')
        if {p.name.removesuffix('.body.html') for p in bodies} != {p.name.removesuffix('.meta.json') for p in metas}:
            errors.append('BODY_METADATA_SLATE_MISMATCH:' + kind)
        for body_path in bodies:
            slug = body_path.name.removesuffix('.body.html')
            meta_path = folder / (slug + '.meta.json')
            if body_path.is_symlink() or meta_path.is_symlink() or not meta_path.is_file():
                errors.append('UNSAFE_OR_MISSING_CANONICAL_PAIR:' + kind + '/' + slug)
                continue
            try:
                body = body_path.read_text('utf-8')
                meta = json.loads(meta_path.read_text('utf-8'))
            except (OSError, ValueError, UnicodeError):
                errors.append('UNREADABLE_CANONICAL_PAIR:' + kind + '/' + slug)
                continue
            row = inspect_record(slug, body, meta, kind)
            errors.extend(kind + '/' + slug + ':' + e for e in row['errors'])
            rows.append(row)
    if len({(r['kind'], r['slug']) for r in rows}) != len(rows):
        errors.append('DUPLICATED_ORIGINAL_DOC_ID')
    disputed = []
    for row in rows:
        for cite in row['citations']:
            if cite['source_id'] in CONFLICTS:
                disputed.append({'document': row['kind'] + '/' + row['slug'], **cite})
    totals = Counter(x['source_id'] for r in rows for x in r['citations'])
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'OCCURRENCE_CROSSWALK_ONLY_HARD_HOLD',
            'errors': sorted(set(errors)), 'documents_checked': len(rows),
            'article_count': sum(r['kind'] == 'articles' for r in rows),
            'tool_count': sum(r['kind'] == 'tools' for r in rows),
            'citation_occurrences': sum(totals.values()),
            'distinct_cited_sources': len(totals),
            'disputed_source_occurrences': sorted(disputed, key=lambda x: (x['document'], x['ordinal'])),
            'disputed_documents': sorted(set(r['document'] for r in disputed)),
            'declared_only_counts': {r['kind'] + '/' + r['slug']: len(r['declared_only_source_ids']) for r in rows if r['declared_only_source_ids']},
            'original_text_omitted': True,
            'occurrence_does_not_establish_claim_support': True,
            **FALSE_GATES}


def native_audit(root: Path) -> dict:
    result = crosswalk(root)
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    try:
        from preparedness.tools import r347_preparedness_offer_funnel_evidence_hold as predecessor
        p = prep / 'tools' / 'r347_preparedness_offer_funnel_evidence_hold.py'
        if p.is_symlink() or not p.is_file() or git_blob(p.read_bytes()) != PRED_BLOB:
            result['errors'].append('R347_COMMITTED_PREDECESSOR_BLOB_MISMATCH')
        prior = predecessor.native_audit(root)
        if prior.get('errors') or prior.get('may_publish') is not False or prior.get('qualified_qd_pass') is not False:
            result['errors'].append('R347_SOURCE_REVIEW_CUSTODY_NOT_ESTABLISHED')
    except (ImportError, OSError, ValueError, TypeError, KeyError) as ex:
        result['errors'].append('R347_NATIVE_PREDECESSOR_UNAVAILABLE:' + type(ex).__name__)
    result['errors'] = sorted(set(result['errors']))
    result['state'] = 'INVALID_HARD_HOLD' if result['errors'] else 'OCCURRENCE_CROSSWALK_ONLY_HARD_HOLD'
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser(description='R348 source-claim placement crosswalk; always HARD HOLD')
    ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()
    print(json.dumps(native_audit(args.repo_root), sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
