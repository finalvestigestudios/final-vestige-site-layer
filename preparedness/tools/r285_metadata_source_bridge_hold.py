#!/usr/bin/env python3
"""Mechanical metadata-to-source custody bridge. ALWAYS DRAFT/HARD HOLD.

Run only against a complete authenticated Preparedness checkout. Does not certify
citation scope, real-world advice, independent QA, fulfillment, or publication.
"""
from __future__ import annotations
import hashlib
import types
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SHA = re.compile(r'[a-f0-9]{40}')
TOOL_PINS = {
    'tools/r279_live_slate_gate.py': '567205e1132a83a52296f5b6d3fa3b7066b703d9',
    'tools/r282_evidence_lineage_hold.py': '28e64ac7babebb4c354dd1c25b91e0fa4a732e06',
}
ORIGINAL = ('audits/r200_seven_cluster_35_article_frozen_custody.json',
            '5822f9dfde21d1f3bdfc26658769d852c639438c')
INTEGRATED = ('audits/r276_all_slate_identity_UNAPPROVED.json',
              'b8c7c6df0dca62b04b01abc5671b7083ad9cb61e')
SOURCE_ROSTER = frozenset({
    'sources/register.json',
    *(f'sources/fragments/{name}.json' for name in
      ('start', 'shelter', 'food', 'health', 'hist-field', 'hist-food', 'hist-home')),
})


def require(condition, why):
    if not condition:
        raise ValueError(why)


def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()


def strict_json(raw):
    def pairs(values):
        out = {}
        for key, value in values:
            require(key not in out, 'duplicate JSON key: '+key)
            out[key] = value
        return out
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def pinned_bytes(root, rel, expected_sha):
    require(type(rel) is str and type(expected_sha) is str and SHA.fullmatch(expected_sha), 'bad pin')
    path = Path(root)
    require(path.is_dir() and not path.is_symlink(), 'unsafe root')
    for part in rel.split('/'):
        require(part not in ('', '..', '.'), 'unsafe pinned path')
        path = path / part
        require(not path.is_symlink(), 'symlinked pinned file: '+rel)
    require(path.is_file(), 'missing pinned file: '+rel)
    raw = path.read_bytes()
    require(blob(raw) == expected_sha, 'pinned file changed: '+rel)
    return raw


def evaluate(original, integrated, metadata, sources):
    """Pure deterministic check for unit tests; caller authenticates all bytes."""
    arts = original.get('articles')
    rows = integrated.get('entries')
    require(type(arts) is list and len(arts) == 35, '35 original articles missing')
    require(type(rows) is list and len(rows) == 96, '96-entry integrated inventory missing')
    require(original.get('state') == integrated.get('state') == HOLD, 'upstream hold missing')
    for key in ('publication_authorized', 'independent_qd_pass', 'medical_safety_verified'):
        require(original.get(key) is False and integrated.get(key) is False, 'upstream release flags')
    require(type(metadata) is dict and type(sources) is dict, 'semantic inputs not dictionaries')
    require(set(sources) == SOURCE_ROSTER, 'eight-source roster drift')
    indexed = defaultdict(list)
    count = 0
    for origin in sorted(sources):
        data = sources[origin]
        require(type(data) is dict and type(data.get('sources')) is list, 'source register malformed')
        for item in data['sources']:
            require(type(item) is dict and type(item.get('id')) is str and item['id'], 'source ID malformed')
            require(type(item.get('url')) is str and item['url'].startswith('https://'), 'source URL malformed')
            indexed[item['id']].append((origin, item))
            count += 1
    require(count == 244, '244 frozen source rows missing')
    meta_rows = [x for x in rows if x['role'] in ('article_meta', 'tool_meta')]
    require(len(meta_rows) == 41 and set(metadata) == {x['path'] for x in meta_rows}, '41 metadata items mismatch')
    arts_by_slug = {a['slug']: a for a in arts}
    require(len(arts_by_slug) == 35, 'duplicate original article slugs')
    used, unresolved, ambiguities, approved_in_metadata = 0, [], set(), []
    tool_slugs = set()
    for row in sorted(meta_rows, key=lambda x:x['path']):
        path = row['path']
        meta = metadata[path]
        require(type(meta) is dict, 'invalid metadata object: '+path)
        slug = path.rsplit('/', 1)[-1].removesuffix('.meta.json')
        require(meta.get('slug') == slug, 'metadata slug mismatch: '+path)
        require(type(meta.get('status')) is dict and meta['status'].get('publish') == 'draft',
                'public metadata state: '+path)
        require(type(meta.get('n')) is int and meta['n'] > 0, 'metadata number invalid: '+path)
        if row['role'] == 'article_meta':
            a = arts_by_slug.get(slug)
            require(a is not None, 'article missing original: '+slug)
            for field in ('n', 'section', 'track'):
                require(meta.get(field) == a.get(field), 'metadata/original '+field+' mismatch: '+slug)
        else:
            require(slug not in tool_slugs, 'duplicate tool slug: '+slug)
            tool_slugs.add(slug)
        review = meta.get('safety_review')
        require(type(review) is dict and type(review.get('state')) is str,
                'safety review record missing: '+slug)
        if review['state'].lower() in ('approved','pass','verified','complete'):
            # A historical editor/founder label is NOT independent medical/privacy/QD clearance.
            approved_in_metadata.append(slug)
        mapping = meta.get('source_use')
        require(type(mapping) is dict and bool(mapping), 'source_use absent: '+slug)
        for id_, purpose in mapping.items():
            require(type(id_) is str and id_ and type(purpose) is str and bool(purpose.strip()),
                    'source_use explanation absent: '+slug)
            used += 1
            candidates = indexed.get(id_, [])
            if not candidates:
                unresolved.append((slug, id_))
            elif len(candidates) > 1:
                ambiguities.add(id_)
    # Missing IDs are explicit INVALID: do not invent or auto-choose citations.
    require(not unresolved, 'unregistered citation IDs: '+repr(sorted(unresolved)[:12]))
    require(len(tool_slugs) == 6, 'tool census changed')
    return {
        'state': HOLD, 'publication_authorized': False, 'independent_qd_pass': False,
        'medical_safety_verified': False, 'privacy_approved': False,
        'source_records': count, 'articles': 35, 'tools': 6, 'metadata_records': 41,
        'source_use_mentions': used, 'ambiguous_citation_ids': sorted(ambiguities),
        'historical_metadata_approved_labels_NOT_independent_approval': sorted(approved_in_metadata),
        'requires_source_scope_review': True, 'requires_qualified_safety_review': True,
    }


def load_pinned_gate(root, rel, pin):
    """Execute exactly the authenticated Git blob bytes, never cached .pyc.

    Hashing the source and subsequently loading a filesystem path creates a
    second-read/bytecode-cache custody gap. CPython's path loader may reuse a
    timestamp-valid __pycache__ file instead of compiling the reviewed source.
    Compile the bytes returned by the *same* verified read; neither the source
    pathname nor any cache is consulted again for the module's code.
    """
    raw = pinned_bytes(root, rel, pin)
    name = 'fv_custody_' + rel.split('/')[-1].removesuffix('.py')
    module = types.ModuleType(name)
    module.__file__ = str(Path(root) / rel)
    module.__package__ = ''
    code = compile(raw, module.__file__, 'exec', dont_inherit=True)
    exec(code, module.__dict__)
    require(callable(getattr(module, 'audit', None)), 'pinned gate has no callable audit: '+rel)
    return module


def audit(root):
    root = Path(root)
    try:
        # Enforce both independently reviewed mechanical gates, not either one.
        # Bind code execution to the bytes whose Git identities were verified.
        modules = {rel: load_pinned_gate(root, rel, pin)
                   for rel, pin in TOOL_PINS.items()}
        for rel, module in modules.items():
            result = module.audit(root)
            require(result.get('state') == HOLD and
                    result.get('publication_authorized') is False and
                    result.get('independent_qd_pass') is False,
                    'inherited custody audit failed: '+rel)
        original = strict_json(pinned_bytes(root, *ORIGINAL))
        integrated = strict_json(pinned_bytes(root, *INTEGRATED))
        metadata = {}
        for row in integrated['entries']:
            if row['role'] in ('article_meta','tool_meta'):
                metadata[row['path']] = strict_json(pinned_bytes(root,row['path'],row['sha']))
        sources = {}
        for row in integrated['entries']:
            if row['path'] in SOURCE_ROSTER:
                sources[row['path']] = strict_json(pinned_bytes(root,row['path'],row['sha']))
        return evaluate(original, integrated, metadata, sources)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, ImportError, SyntaxError) as exc:
        return {'state': INVALID, 'publication_authorized': False,
                'independent_qd_pass': False, 'errors': [str(exc)]}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    print(json.dumps(result, sort_keys=True, indent=2))
    raise SystemExit(2 if result['state'] == HOLD else 3)
