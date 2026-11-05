#!/usr/bin/env python3
"""Read-only Preparedness 35-article snapshot/citation custody gate. Not safety/QD approval."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
HOLD = 'DRAFT_HUMAN_REVIEW_HOLD'
PENDING = 'pending-human-source-and-reading-scope-review'
IGNORED = {'script', 'style', 'template', 'noscript'}


class IntegrityHold(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise IntegrityHold(code)


def pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'DUPLICATE_JSON_KEY:' + str(key))
        out[key] = value
    return out


def load_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs_unique)


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


class VisibleCites(HTMLParser):
    """Conservative token visibility filter; does NOT establish source support."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.visible = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        style = re.sub(r'\s+', '', attrs.get('style') or '').lower()
        hidden = tag in IGNORED or ('hidden' in attrs) or ('inert' in attrs) or (
            (attrs.get('aria-hidden') or '').lower() == 'true') or (
            'display:none' in style or 'visibility:hidden' in style)
        self.stack.append((tag, hidden or any(t[1] for t in self.stack)))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not any(t[1] for t in self.stack):
            self.visible.extend(CITE.findall(data))


def audit(root: Path, manifest: dict, expected_articles: int = 35):
    root = Path(root)
    need(manifest.get('schema_version') == 1 and manifest.get('release_status') == HOLD,
         'MANIFEST_HOLD_REQUIRED')
    need(manifest.get('candidate_parent') == '5685b54796d520e8dd50e0cdf4d35e38c9cec7a4',
         'CANDIDATE_PARENT_DRIFT')
    need(manifest.get('qd_pass') is False and manifest.get('may_publish') is False and
         manifest.get('medical_safety_verified') is False and
         manifest.get('merchant_offer_verified') is False, 'FORGED_APPROVAL')
    entries = manifest.get('files')
    need(isinstance(entries, list) and entries, 'MISSING_FILE_MANIFEST')
    declared = {}
    for entry in entries:
        path, sha = entry.get('path'), entry.get('blob_sha')
        need(isinstance(path, str) and path.startswith('preparedness/') and
             '..' not in Path(path).parts and path not in declared and
             re.fullmatch(r'[a-f0-9]{40}', str(sha)), 'BAD_FILE_MANIFEST')
        declared[path] = sha
    actual = {}
    for path, sha in declared.items():
        raw = (root / path).read_bytes()
        need(blob(raw) == sha, 'GIT_BLOB_DRIFT:' + path)
        actual[path] = raw
    bodies = sorted(p for p in declared if p.startswith('preparedness/content/articles/')
                    and p.endswith('.body.html'))
    metas = sorted(p for p in declared if p.startswith('preparedness/content/articles/')
                   and p.endswith('.meta.json'))
    need(len(bodies) == len(metas) == expected_articles, 'ARTICLE_COUNT_DRIFT')
    article_dir = root / 'preparedness/content/articles'
    need({str(p.relative_to(root)) for p in article_dir.glob('*.body.html')} == set(bodies)
         and {str(p.relative_to(root)) for p in article_dir.glob('*.meta.json')} == set(metas),
         'UNMANIFESTED_OR_MISSING_ARTICLES')
    tax = load_json(actual['preparedness/taxonomy.json'])
    slate = tax['slate']
    need(len(slate) == expected_articles and len({a['slug'] for a in slate}) == expected_articles,
         'TAXONOMY_ROSTER_DRIFT')
    need(tax['base_path'] == '/preparedness/', 'ROUTE_BASE_DRIFT')
    cross = load_json(actual['preparedness/sources/crosswalk.json'])
    need(cross.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
         'CROSSWALK_STATUS_DRIFT')
    need(len(cross['groups']) == 32, 'SHARED_SOURCE_GROUP_COUNT_DRIFT')
    for group in cross['groups']:
        need(group.get('review_status') == PENDING and group.get('reviewer') is None
             and group.get('reviewed_on') is None, 'SOURCE_GROUP_UNREVIEWED_REQUIRED')
    origins = cross['article_origins']
    files = {'base': 'register.json', **{k: 'fragments/' + k + '.json' for k in
             ('start', 'shelter', 'food', 'health', 'hist-food', 'hist-home', 'hist-field')}}
    sources = {}
    for origin, filename in files.items():
        src = load_json(actual['preparedness/sources/' + filename])['sources']
        sources[origin] = {s['id']: s for s in src}
        need(len(src) == len(sources[origin]), 'DUPLICATE_SOURCE_ID_IN_ORIGIN:' + origin)
    grouped = {(v['origin'], v['source']['id'], v['source']['url']) for g in cross['groups']
               for v in g['variants']}
    need(len(grouped) == sum(len(g['variants']) for g in cross['groups']),
         'DUPLICATE_CROSSWALK_MEMBER')
    routes = set()
    cited_total = 0
    cited_pairs = 0
    classified = Counter()
    for a in slate:
        slug = a['slug']
        mp = f'preparedness/content/articles/{slug}.meta.json'
        bp = f'preparedness/content/articles/{slug}.body.html'
        need(mp in actual and bp in actual, 'SLATE_ARTICLE_MISSING:' + slug)
        meta = load_json(actual[mp])
        need(meta['slug'] == slug and meta['section'] == a['section'] and
             meta['track'] == a['track'], 'ARTICLE_TAXONOMY_MISMATCH:' + slug)
        route = f"{tax['base_path']}{a['section']}/{slug}/"
        need(route not in routes, 'DUPLICATE_ROUTE:' + route)
        routes.add(route)
        need(meta['status']['publish'] == 'draft', 'PUBLICATION_UPGRADE:' + slug)
        state = meta['safety_review']['state']
        need(state in ('pending', 'approved', 'not-required'), 'UNKNOWN_SAFETY_STATE:' + slug)
        if a.get('gate'):
            need(state != 'not-required', 'HIGH_CONSEQUENCE_GATE_DOWNGRADE:' + slug)
        classified[state] += 1
        body = actual[bp].decode('utf-8')
        ids = CITE.findall(body)
        need('{{cite:' not in CITE.sub('', body), 'MALFORMED_CITATION:' + slug)
        parser = VisibleCites()
        parser.feed(body)
        need(len(parser.visible) == len(ids) and Counter(parser.visible) == Counter(ids),
             'HIDDEN_OR_ATTRIBUTE_CITATION:' + slug)
        cited_total += len(ids)
        used = meta.get('source_use')
        need(isinstance(used, dict) and set(used) == set(ids), 'SOURCE_USE_CROSSWALK_DRIFT:' + slug)
        origin = origins.get(slug, 'base')
        need(origin in sources, 'UNKNOWN_ARTICLE_ORIGIN:' + slug)
        for sid in set(ids):
            need(isinstance(used[sid], str) and bool(used[sid].strip()),
                 'BLANK_READING_SCOPE:' + slug + ':' + sid)
            source = sources[origin].get(sid) or sources['base'].get(sid)
            need(source is not None and source.get('verified_on'),
                 'UNCHECKED_SOURCE_FOR_AUTHOR:' + slug + ':' + sid)
            cited_pairs += 1
    need(cited_total == manifest.get('expected_citation_occurrences'), 'CITATION_TOTAL_DRIFT')
    return {'release_status': 'HOLD', 'qd_pass': False, 'may_publish': False,
            'medically_safe': False, 'articles': len(slate),
            'visible_citation_occurrences': cited_total, 'author_source_bindings': cited_pairs,
            'shared_source_groups_pending': len(cross['groups']),
            'historical_safety_states_not_independent_approval': dict(classified),
            'warning': 'Structural provenance/citation custody only. Human safety, source and QD review required.'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--manifest', type=Path, default=Path('preparedness/docs/r133/locked_files.json'))
    args = ap.parse_args(argv)
    try:
        print(json.dumps(audit(args.root, load_json((args.root / args.manifest).read_bytes())), indent=2))
        return 0
    except (IntegrityHold, OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
