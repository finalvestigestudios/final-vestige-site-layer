#!/usr/bin/env python3
"""R464: immutable Shelter version comparison for qualified source/safety reviewers.

Offline, deterministic, and read-only. Exact Git blob pins are required for
candidate + each witness. Delta reports are *review queues*, never QD approvals.
No CMS, network, checkout, publishing, or branch selection logic exists here.
"""
from __future__ import annotations
import argparse
from difflib import SequenceMatcher
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

HOLD = 'DRAFT_HARD_HOLD'
SLUGS = ('family-communication-plan', 'home-fire-escape-plan',
         'outage-heat-cold-generators', 'shelter-or-evacuate')
VARIANTS = ('original', 'continuation', 'followup')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
BLOCKS = frozenset(('p', 'li', 'blockquote', 'td', 'th', 'figcaption',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))
SKIP = frozenset(('script', 'style', 'noscript'))

class WitnessHold(ValueError):
    pass

def require(pred, message):
    if not pred:
        raise WitnessHold(message)

def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def clean(s):
    return ' '.join(s.split())

def exact_json(raw):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, 'duplicate JSON key: ' + k)
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=unique)

class Fragment(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.stack = []
        self.skip = []
        self.links = []
        self.all_text = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in SKIP:
            self.skip.append(tag)
        if self.skip:
            return
        self.tags.append((tag, tuple(attrs)))
        if tag in BLOCKS:
            self.stack.append([tag, []])
        if tag in ('a', 'img', 'source', 'iframe'):
            attrs_dict = dict(attrs)
            self.links.append((tag, attrs_dict.get('href'), attrs_dict.get('src'),
                               attrs_dict.get('rel'), attrs_dict.get('target')))

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip:
            if tag == self.skip[-1]:
                self.skip.pop()
            return
        if tag in BLOCKS:
            require(bool(self.stack) and self.stack[-1][0] == tag,
                    'unbalanced article reading-depth block: ' + tag)
            _, chunks = self.stack.pop()
            self.blocks.append((tag, clean(''.join(chunks))))

    def handle_data(self, data):
        if not self.skip:
            self.all_text.append(data)
            for _, chunks in self.stack:
                chunks.append(data)

def parse_fragment(raw):
    require(isinstance(raw, bytes) and 0 < len(raw) < 250000,
            'witness missing, oversized or not bytes')
    try:
        html = raw.decode('utf-8', errors='strict')
    except UnicodeError as exc:
        raise WitnessHold('non-UTF8 witness') from exc
    parser = Fragment()
    try:
        parser.feed(html)
        parser.close()
    except (AssertionError, TypeError) as exc:
        raise WitnessHold('malformed article HTML') from exc
    require(not parser.stack and not parser.skip, 'unclosed block or unsafe hidden section')
    require(len(parser.blocks) >= 1, 'article missing reading-depth blocks')
    citation_ids = CITE.findall(html)
    require(html.count('{{cite:') == len(citation_ids), 'malformed citation token')
    return {'blocks': parser.blocks, 'links': parser.links,
            'citations': citation_ids, 'plain_text': clean(' '.join(parser.all_text)),
            'tag_attributes': parser.tags}

def difference(witness_raw, candidate_raw, witness_sha, candidate_sha, *, slug, variant):
    require(slug in SLUGS and variant in VARIANTS, 'unrecognized article/branch witness')
    for val in (witness_sha, candidate_sha):
        require(isinstance(val, str) and re.fullmatch(r'[a-f0-9]{40}', val),
                'bad frozen Git identity')
    require(git_blob(witness_raw) == witness_sha, 'witness Git blob mismatch')
    require(git_blob(candidate_raw) == candidate_sha, 'candidate Git blob mismatch')
    a, b = parse_fragment(witness_raw), parse_fragment(candidate_raw)
    matcher = SequenceMatcher(None, a['blocks'], b['blocks'], autojunk=False)
    edits = []
    for op, i, j, k, l in matcher.get_opcodes():
        if op == 'equal':
            continue
        edits.append({'op': op, 'witness_range': [i, j], 'candidate_range': [k, l],
                      'witness_example': a['blocks'][i][1][:220] if i < j else '',
                      'candidate_example': b['blocks'][k][1][:220] if k < l else ''})
    return {'slug': slug, 'witness': variant, 'witness_blob': witness_sha,
            'candidate_blob': candidate_sha, 'witness_bytes': len(witness_raw),
            'candidate_bytes': len(candidate_raw),
            'whole_body_identical': witness_raw == candidate_raw,
            'visible_text_identical': a['plain_text'] == b['plain_text'],
            'block_sequence_identical': a['blocks'] == b['blocks'],
            'citation_sequence_identical': a['citations'] == b['citations'],
            'link_sequence_identical': a['links'] == b['links'],
            'tag_attributes_identical': a['tag_attributes'] == b['tag_attributes'],
            'witness_block_count': len(a['blocks']), 'candidate_block_count': len(b['blocks']),
            'witness_citation_count': len(a['citations']),
            'candidate_citation_count': len(b['citations']),
            'witness_link_count': len(a['links']), 'candidate_link_count': len(b['links']),
            'block_differences': edits,
            'release_state': HOLD, 'review_required': True,
            'qualified_safety_approval': False, 'may_publish': False,
            'paid_offer_verified': False, 'paid_revenue_verified': False}

def audit(manifest, blobs):
    """blobs is mapping (slug, variant) -> exact file bytes (candidate included)."""
    require(isinstance(manifest, dict) and manifest.get('schema') == 1 and
            manifest.get('state') == HOLD and manifest.get('qd_pass') is False,
            'witness manifest not held for review')
    require(isinstance(blobs, dict) and len(blobs) == 16, 'four-article four-version census drift')
    require(set(manifest.get('articles', {})) == set(SLUGS), 'missing Shelter article')
    reports = []
    for slug in SLUGS:
        sha = manifest['articles'][slug]
        require(isinstance(sha, dict) and set(sha) == {'candidate', *VARIANTS},
                'missing/fabricated witness: ' + slug)
        for variant in VARIANTS:
            require((slug, variant) in blobs and (slug, 'candidate') in blobs,
                    'missing witness byte stream')
            reports.append(difference(blobs[(slug, variant)], blobs[(slug, 'candidate')],
                                      sha[variant], sha['candidate'], slug=slug,
                                      variant=variant))
    require(set(blobs) == {(s, v) for s in SLUGS for v in (*VARIANTS, 'candidate')},
            'unauthorized extra evidence')
    return {'state': 'TWELVE_SHELTER_WITNESS_DELTAS_REVIEW_ONLY',
            'release_state': HOLD, 'qualified_qd_pass': False, 'may_publish': False,
            'candidate_winner_selected': False, 'source_adjudication_complete': False,
            'review_count': len(reports), 'reports': reports}

def safe_load_file(root, path, *, max_size=250000):
    require(isinstance(path, Path) and not path.is_absolute() and '..' not in path.parts,
            'unsafe evidence path')
    file = root / path
    require(file.is_file() and not file.is_symlink(), 'missing or symlinked evidence: ' + str(path))
    require(file.stat().st_size < max_size, 'evidence exceeds size budget')
    return file.read_bytes()

def native(root, witness_root):
    root = root.resolve()
    witness_root = witness_root.resolve()
    manifest = exact_json(safe_load_file(root, Path('audits/R464_SHELTER_WITNESS_PINS.json')))
    rows = {}
    for slug in SLUGS:
        rows[(slug, 'candidate')] = safe_load_file(root, Path('content/articles') / (slug + '.body.html'))
        for version in VARIANTS:
            rows[(slug, version)] = safe_load_file(witness_root,
                                                Path(version) / (slug + '.body.html'))
    return audit(manifest, rows)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--witness-root', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'audits/r464_witnesses')
    args = parser.parse_args(argv)
    try:
        result = native(args.root, args.witness_root)
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        result = {'state':'WITNESS_VALIDATION_HARD_HOLD','error':str(exc),
                  'release_state':HOLD,'qualified_qd_pass':False,'may_publish':False}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # Structural parity never constitutes a release gate PASS.

if __name__ == '__main__':
    sys.exit(main())
