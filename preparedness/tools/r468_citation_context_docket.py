#!/usr/bin/env python3
"""R468: review-only per-context citation witness docket for 35 authored articles.

No external fetch, writes, publication, safety or commerce approvals. Every CLI run
ends HARD_HOLD, even when its structural evidence is internally consistent.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys

CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
BLOCKS = frozenset(('p','li','td','th','h1','h2','h3','h4','h5','h6','pre','dt','dd','figcaption'))
SKIP = frozenset(('script','style','template'))
HOLD = 'DRAFT_HARD_HOLD'

class ContextHold(ValueError):
    pass

def require(ok, msg):
    if not ok:
        raise ContextHold(msg)

def sha(raw):
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def clean(value):
    return ' '.join(value.split())

class Segmenter(HTMLParser):
    """Deterministically segments *visible text*, never judges claim support."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.units = []
        self.parts = []
        self.skipped = []
        self.events = []
        self.breaks = 0

    def flush(self):
        txt = clean(''.join(self.parts))
        if txt:
            ix = len(self.units)
            ids = CITE.findall(txt)
            self.units.append({'unit': ix, 'text_sha256': sha(txt),
                               'characters': len(txt), 'excerpt': txt[:260],
                               'citation_ids': ids})
            for sid in ids:
                self.events.append({'ordinal': len(self.events), 'unit': ix, 'source_id': sid,
                                    'context_sha256': sha(txt), 'context_excerpt': txt[:260]})
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skipped.append(tag)
        elif not self.skipped and tag in BLOCKS:
            self.flush()
            self.breaks += 1
        elif not self.skipped and tag == 'br':
            self.parts.append(' ')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.skipped:
            if tag == self.skipped[-1]:
                self.skipped.pop()
        elif tag in BLOCKS:
            self.flush()

    def handle_data(self, data):
        if not self.skipped:
            self.parts.append(data)

    def handle_comment(self, data):
        pass

    def finish(self):
        self.flush()
        require(not self.skipped, 'unterminated nonvisible HTML container')
        return self.units, self.events

def docket_article(slug, meta, body, origin, registries):
    """Fail closed on identity/citation drift; retain literal URL and reading scope."""
    require(isinstance(slug, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug), 'bad slug')
    require(isinstance(meta, dict) and isinstance(body, str) and meta.get('slug') == slug,
            'authored body/metadata mismatch')
    require(meta.get('status', {}).get('publish') == 'draft', 'non-draft article')
    require(isinstance(meta.get('source_use'), dict) and bool(meta['source_use']),
            'missing authored reading scopes')
    require(isinstance(registries, dict) and origin in registries and 'base' in registries,
            'source origin unavailable')
    segmenter = Segmenter()
    segmenter.feed(body)
    units, events = segmenter.finish()
    literal_ids = CITE.findall(body)
    require(len(events) == len(literal_ids) and [e['source_id'] for e in events] == literal_ids,
            'citations concealed outside visible body or altered in parsing')
    require(set(literal_ids) == set(meta['source_use']) and len(literal_ids) > 0,
            'authored reading-scope/citation mismatch')
    for event in events:
        sid = event['source_id']
        note = meta['source_use'][sid]
        require(isinstance(note, str) and bool(note.strip()), 'empty reading scope')
        matches = [r for r in registries[origin] if r.get('id') == sid]
        if not matches:
            matches = [r for r in registries['base'] if r.get('id') == sid]
            selected_origin = 'base'
        else:
            selected_origin = origin
        require(len(matches) == 1 and isinstance(matches[0].get('url'), str) and
                matches[0]['url'].startswith('https://'), 'missing/ambiguous source identity')
        event.update({'literal_url': matches[0]['url'], 'selected_origin': selected_origin,
                      'authored_reading_scope_sha256': sha(note),
                      'authored_reading_scope': note})
    return {'slug': slug, 'origin': origin, 'state': HOLD,
            'body_sha256': sha(body),
            'citation_count': len(events), 'source_use_count': len(meta['source_use']),
            'unit_count': len(units), 'units': units, 'citation_events': events,
            'claim_support_verified': False, 'qualified_qd_pass': False,
            'may_publish': False, 'merchant_orders_verified': False}

def compare(old, new):
    """Mechanical drift docket; never selects a safer version."""
    require(old.get('slug') == new.get('slug'), 'cannot compare different article identities')
    keys = ('body_sha256', 'citation_count', 'source_use_count', 'unit_count')
    changes = [k for k in keys if old.get(k) != new.get(k)]
    for key in ('units','citation_events'):
        a, b = old.get(key), new.get(key)
        require(isinstance(a, list) and isinstance(b, list), 'malformed context ledger')
        if len(a) != len(b):
            changes.append(key + '_length')
        for i in range(min(len(a), len(b))):
            for field in (('text_sha256','citation_ids') if key == 'units' else
                          ('source_id','unit','context_sha256','literal_url','selected_origin',
                           'authored_reading_scope_sha256')):
                if a[i].get(field) != b[i].get(field):
                    changes.append(key + '[' + str(i) + '].' + field)
    return {'slug': old['slug'], 'review_required': bool(changes),
            'differences': sorted(set(changes)), 'release_state': HOLD,
            'qualified_qd_pass': False, 'claim_support_verified': False}

def _load_tool(path):
    require(path.is_file() and not path.is_symlink(), 'required source tool unavailable')
    spec = importlib.util.spec_from_file_location('r468_prior', path)
    require(spec is not None and spec.loader is not None, 'cannot load prior gate')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def native(root):
    """Run R463's original-body/source gate first; load only its pinned inputs."""
    root = root.resolve()
    prior = _load_tool(root / 'tools/r463_article_citation_use_custody.py')
    receipt = prior.native(root)
    require(receipt['article_count'] == 35 and receipt['citation_occurrences'] == 2000
            and receipt['distinct_article_source_use_memberships'] == 385,
            'original article census drift')
    snapshot = prior.pinned_json(root, 'audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json',
                                 prior.SNAPSHOT_BLOB)
    cw = prior.pinned_json(root, 'sources/crosswalk.json', prior.CROSSWALK_BLOB,
                           max_size=180000)
    regs = {}
    for entry in cw['source_files']:
        rel = entry['path'].removeprefix('preparedness/')
        source = prior.pinned_json(root, rel, entry['git_blob_sha'])
        require(entry['origin'] not in regs, 'duplicate source family')
        regs[entry['origin']] = source['sources']
    items = []
    for slug, pins in sorted(snapshot['candidate']['articles'].items()):
        rel = 'content/articles/' + slug + '.'
        meta = prior.pinned_json(root, rel + 'meta.json', pins['meta'])
        body = prior.pinned_bytes(root, rel + 'body.html', pins['body'], max_size=180000).decode('utf-8')
        items.append(docket_article(slug, meta, body, cw['article_origins'][slug], regs))
    require(len(items) == 35 and sum(x['citation_count'] for x in items) == 2000
            and sum(x['source_use_count'] for x in items) == 385,
            'full citation context census drift')
    return {'state': 'CITATION_CONTEXT_REVIEW_REQUIRED', 'release_state': HOLD,
            'article_count': 35, 'citation_count': 2000, 'source_use_count': 385,
            'qualified_qd_pass': False, 'claim_support_verified': False,
            'may_publish': False, 'verified_orders': None, 'net_revenue_per_1000': None,
            'articles': items}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args(argv)
    try:
        print(json.dumps(native(args.root), sort_keys=True, indent=2))
    except (ContextHold, ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        print(json.dumps({'state': 'CITATION_CONTEXT_FAILURE_HARD_HOLD',
                          'release_state': HOLD, 'qualified_qd_pass': False,
                          'may_publish': False, 'error': str(exc)}, sort_keys=True))
    return 2

if __name__ == '__main__':
    sys.exit(main())
