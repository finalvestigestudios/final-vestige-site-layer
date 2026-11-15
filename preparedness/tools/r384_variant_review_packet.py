"""R384: immutable Preparedness variant review packets; never select or clear a draft.

Compares each manuscript+metadata variant by pinned Git blob, and records prose,
citation, safety-state and reading-depth differences for qualified human review.
This is evidence custody, NOT semantic equivalence or a medical/safety ruling.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import itertools
import json
from pathlib import Path
import re
import subprocess

SHA = re.compile(r'[a-f0-9]{40}\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
BLOCK = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'td', 'th', 'figcaption', 'dt', 'dd'}
BODY_SUFFIX = '.body.html'
META_SUFFIX = '.meta.json'
PREFIX = 'preparedness/content/articles/'


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data, usedforsecurity=False).hexdigest()


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.active = None
        self.depth = 0
        self.suppressed = 0

    def flush(self):
        if self.active is not None:
            raw = ''.join(self.active['raw'])
            visible = ' '.join(CITE.sub('', raw).split())
            citations = CITE.findall(raw)
            if visible or citations:
                self.rows.append({'tag': self.active['tag'], 'text': visible,
                                  'citations': citations,
                                  'prose_sha256': hashlib.sha256(visible.casefold().encode()).hexdigest(),
                                  'full_sha256': hashlib.sha256((visible + '\n' + ','.join(citations)).encode()).hexdigest(),
                                  'words': len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", visible))})
        self.active = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'template'}:
            self.suppressed += 1
        if self.suppressed:
            return
        if tag in BLOCK:
            if self.active is None:
                self.active = {'tag': tag, 'raw': []}
                self.depth = 1
            else:
                self.depth += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'template'} and self.suppressed:
            self.suppressed -= 1
            return
        if self.suppressed:
            return
        if tag in BLOCK and self.active:
            self.depth -= 1
            if self.depth <= 0:
                self.flush()

    def handle_data(self, data):
        if not self.suppressed and self.active:
            self.active['raw'].append(data)


def paragraphs(data: bytes) -> list[dict]:
    parser = Blocks()
    parser.feed(data.decode('utf-8'))
    parser.close()
    parser.flush()
    return parser.rows


def pair_delta(a: dict, b: dict) -> dict:
    """Directional diff, never a claim that one variant is better or correct."""
    ar, br = a['blocks'], b['blocks']
    from collections import Counter
    ac, bc = Counter(x['full_sha256'] for x in ar), Counter(x['full_sha256'] for x in br)
    removed, added = ac - bc, bc - ac
    ap, bp = Counter(x['prose_sha256'] for x in ar), Counter(x['prose_sha256'] for x in br)
    changed_support = sorted(set(ap) & set(bp) & {
        x['prose_sha256'] for x in ar + br if any(y['prose_sha256'] == x['prose_sha256']
        and y['citations'] != x['citations'] for y in ar + br)})
    ca, cb = Counter(itertools.chain.from_iterable(x['citations'] for x in ar)), Counter(itertools.chain.from_iterable(x['citations'] for x in br))
    return {'from_branch': a['branch'], 'to_branch': b['branch'],
            'removed_exact_blocks': sum(removed.values()), 'added_exact_blocks': sum(added.values()),
            'removed_block_sha256': sorted(removed.elements()),
            'added_block_sha256': sorted(added.elements()),
            'changed_support_prose_sha256': changed_support,
            'removed_citation_occurrences': dict(sorted((ca - cb).items())),
            'added_citation_occurrences': dict(sorted((cb - ca).items())),
            'source_use_ids_removed': sorted(set(a['source_use']) - set(b['source_use'])),
            'source_use_ids_added': sorted(set(b['source_use']) - set(a['source_use'])),
            'source_use_text_changed': sorted(k for k in set(a['source_use']) & set(b['source_use']) if a['source_use'][k] != b['source_use'][k]),
            'word_delta': b['words'] - a['words'],
            'historical_safety_state_changed': a['safety_state'] != b['safety_state'],
            'requires_human_review': a['body_sha'] != b['body_sha'] or a['meta_sha'] != b['meta_sha']}


def build_packet(manifest: dict, reader) -> dict:
    """Refuse incomplete/authenticity-mismatched manifests; never write sources."""
    packet = {'schema': 1, 'release': 'DRAFT_HARD_HOLD', 'publication_approved': False,
              'qualified_safety_approved': False, 'status': 'INVALID_HARD_HOLD', 'errors': [], 'articles': [],
              'review_deltas': [], 'unselected_conflicts': []}
    error = packet['errors']
    if not isinstance(manifest, dict) or manifest.get('release_state') != 'DRAFT_HARD_HOLD' or manifest.get('article_count') != 35 or manifest.get('conflict_count') != 9:
        error.append('MANIFEST_INVARIANT_MISMATCH'); return packet
    pins = manifest.get('branch_pins'); objs = manifest.get('objects')
    if not isinstance(pins, list) or len(pins) != 9 or not isinstance(objs, list) or len(objs) != 77:
        error.append('ORIGINAL_OBJECT_OR_BRANCH_COUNT_MISMATCH'); return packet
    branches = {p.get('branch') for p in pins if isinstance(p, dict) and SHA.fullmatch(str(p.get('sha', '')))}
    if len(branches) != 9:
        error.append('INVALID_BRANCH_PINS'); return packet
    bypath = {}
    for obj in objs:
        if not isinstance(obj, dict) or not isinstance(obj.get('path'), str) or obj['path'] in bypath or obj.get('selected_sha') is not None:
            error.append('INVALID_PATH_OR_UNREVIEWED_SELECTION'); return packet
        bypath[obj['path']] = obj
    def read_variant(v):
        sha = v.get('sha'); expected = v.get('size')
        if not isinstance(sha, str) or not SHA.fullmatch(sha) or not isinstance(expected, int) or expected < 0:
            raise ValueError('INVALID_OBJECT_RECORD')
        data = reader(sha)
        if not isinstance(data, bytes) or len(data) != expected or blob_sha(data) != sha:
            raise ValueError('OBJECT_SHA_OR_SIZE_MISMATCH')
        return data
    # Read every pinned original, including metadata and source fragments; never drop a branch.
    try:
        for obj in objs:
            variants = obj.get('variants')
            if not isinstance(variants, list) or not variants:
                raise ValueError('MISSING_VARIANTS')
            for v in variants:
                if not isinstance(v, dict) or v.get('branch') not in branches:
                    raise ValueError('UNKNOWN_BRANCH')
                read_variant(v)
    except (ValueError, KeyError, TypeError, UnicodeError, OSError, subprocess.SubprocessError) as exc:
        error.append('ORIGINAL_OBJECT_READ_FAILED:' + type(exc).__name__); return packet
    paths = [p for p in bypath if p.startswith(PREFIX)]
    bodies = {p[len(PREFIX):-len(BODY_SUFFIX)]: bypath[p] for p in paths if p.endswith(BODY_SUFFIX)}
    metas = {p[len(PREFIX):-len(META_SUFFIX)]: bypath[p] for p in paths if p.endswith(META_SUFFIX)}
    if len(bodies) != 35 or set(bodies) != set(metas):
        error.append('MANUSCRIPT_METADATA_PAIR_MISMATCH'); return packet
    for slug in sorted(bodies):
        bv = {v['branch']: v for v in bodies[slug]['variants']}
        mv = {v['branch']: v for v in metas[slug]['variants']}
        if set(bv) != set(mv):
            error.append('BRANCH_VARIANT_PAIR_MISMATCH:' + slug); continue
        variants = []
        for branch in sorted(bv):
            try:
                body, meta = read_variant(bv[branch]), json.loads(read_variant(mv[branch]))
                if not isinstance(meta, dict) or meta.get('slug') != slug or meta.get('status', {}).get('publish') != 'draft':
                    raise ValueError('CANONICAL_SLUG_OR_DRAFT_STATE_MISMATCH')
                safety = meta.get('safety_review', {})
                if not isinstance(safety, dict) or safety.get('state') not in {'pending', 'approved', 'not-required'}:
                    raise ValueError('HISTORICAL_SAFETY_STATE_INVALID')
                scopes = meta.get('source_use')
                if not isinstance(scopes, dict):
                    raise ValueError('SOURCE_USE_INVALID')
                blocks = paragraphs(body)
                all_ids = set(itertools.chain.from_iterable(x['citations'] for x in blocks))
                variants.append({'branch': branch, 'body_sha': bv[branch]['sha'], 'meta_sha': mv[branch]['sha'],
                                 'safety_state': safety['state'], 'source_use': scopes,
                                 'blocks': blocks, 'words': sum(x['words'] for x in blocks),
                                 'citations': sorted(all_ids),
                                 'missing_reading_scopes': sorted(x for x in all_ids if not isinstance(scopes.get(x), str) or not scopes.get(x, '').strip())})
            except (ValueError, KeyError, TypeError, UnicodeError, AttributeError) as exc:
                error.append('VARIANT_PARSE_FAILED:' + slug + ':' + branch + ':' + type(exc).__name__)
        packet['articles'].append({'slug': slug, 'variants': variants})
        if len(variants) > 1:
            for a, b in itertools.combinations(variants, 2):
                packet['review_deltas'].append({'slug': slug, **pair_delta(a, b)})
    for obj in objs:
        shas = {v['sha'] for v in obj['variants']}
        if len(shas) > 1:
            packet['unselected_conflicts'].append({'path': obj['path'], 'blobs': sorted(shas)})
    if len(packet['unselected_conflicts']) != 9:
        error.append('FORK_COUNT_CHANGED')
    packet['status'] = 'INVALID_HARD_HOLD' if error else 'REVIEW_PACKET_HARD_HOLD'
    return packet


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--manifest-blob', default='5e7d9a8972872c82b4bc46ac13aab18883d8149a')
    args = ap.parse_args()
    def read(sha):
        return subprocess.run(['git', '-C', str(Path(args.repo)), 'cat-file', 'blob', sha], check=True, capture_output=True, timeout=20).stdout
    try:
        raw = read(args.manifest_blob)
        if blob_sha(raw) != args.manifest_blob:
            raise ValueError('MANIFEST_SHA_MISMATCH')
        result = build_packet(json.loads(raw), read)
    except (ValueError, OSError, subprocess.SubprocessError, TypeError) as exc:
        result = {'status': 'INVALID_HARD_HOLD', 'errors': ['AUTHENTIC_GIT_OBJECTS_UNAVAILABLE:' + type(exc).__name__], 'publication_approved': False}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2  # Never authorizes publication, even when custody checks pass.


if __name__ == '__main__':
    raise SystemExit(main())
