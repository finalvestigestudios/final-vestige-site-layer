#!/usr/bin/env python3
"""R476: read-only 35-article candidate SHA, citation, metadata and HOLD gate.

Source is a frozen GitHub contents API snapshot of R475's *candidate* tree,
NOT a claim that source text, emergency advice, checkout, or exports are safe.
It must never change manuscripts, mark safety PASS, or promote drafts.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r476-35-candidate-pair-snapshot-v1'
PARENT = '1f8261505202ccd3def3c10b34853da21868acf2'
REPO = 'finalvestigestudios/final-vestige-site-layer'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')
STATE = 'DRAFT_HARD_HOLD'

class Hold(ValueError):
    pass

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Hold(reason)

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def strict_json(raw: bytes):
    def pairs_unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, 'duplicate JSON key: ' + key)
            value[key] = item
        return value
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs_unique,
                      parse_constant=lambda v: (_ for _ in ()).throw(Hold('illegal number: ' + v)))

def check_manifest(snapshot: dict, expected_count: int = 35) -> list:
    require(type(snapshot) is dict and set(snapshot) ==
            {'schema', 'repository', 'candidate_parent_sha', 'release', 'permission',
             'articles', 'commerce', 'review_state'}, 'manifest structure changed')
    for key, value in [('schema', SCHEMA), ('repository', REPO),
                       ('candidate_parent_sha', PARENT), ('release', STATE),
                       ('permission', 'STRUCTURAL_EVIDENCE_ONLY_NOT_QD_PASS')]:
        require(snapshot.get(key) == value, 'untrusted manifest provenance: ' + key)
    reviews = snapshot['review_state']
    require(type(reviews) is dict and set(reviews) ==
            {'qualified_qd_pass', 'native_35_article_build_pass', 'wordpress_export_parity_pass',
             'medical_food_child_privacy_approved', 'publish_authorized', 'source_disputes_resolved'},
            'review keys changed')
    require(all(value is False for value in reviews.values()), 'invented release/safety approval')
    commerce = snapshot['commerce']
    require(type(commerce) is dict and set(commerce) ==
            {'verified_purchasable_preparedness_sku', 'published_grok_asset_id',
             'paid_order_verified', 'realized_net_revenue_per_1000_qualified_sessions'},
            'commerce keys changed')
    require(all(v is None for v in commerce.values()), 'invented product/asset/sales evidence')
    articles = snapshot['articles']
    require(type(articles) is list and len(articles) == expected_count, '35 article coverage lost')
    slugs = []
    blobs = []
    for row in articles:
        require(type(row) is dict and set(row) == {'slug', 'body', 'meta'}, 'article pin changed')
        slug = row['slug']
        require(type(slug) is str and SLUG.fullmatch(slug) is not None, 'unsafe slug')
        slugs.append(slug)
        for kind, suffix in [('body', '.body.html'), ('meta', '.meta.json')]:
            info = row[kind]
            require(type(info) is dict and set(info) == {'path', 'git_blob', 'bytes'}, 'file pin changed')
            require(info['path'] == 'content/articles/' + slug + suffix, 'path/slug alias or escape')
            require(type(info['git_blob']) is str and SHA.fullmatch(info['git_blob']) is not None,
                    'invalid Git blob')
            require(type(info['bytes']) is int and 50 <= info['bytes'] <= 150000,
                    'invalid size bound')
            blobs.append(info['git_blob'])
    require(len(set(slugs)) == expected_count and slugs == sorted(slugs), 'duplicate/unsorted route slug')
    require(len(set(blobs)) == expected_count * 2, 'duplicate body/metadata Git blob identity')
    return articles

def read_pinned(root: Path, info: dict) -> bytes:
    root = root.resolve()
    path = root / info['path']
    require(path.is_file() and not path.is_symlink() and
            path.resolve().is_relative_to(root), 'missing, symlink or escaped native file: ' + info['path'])
    raw = path.read_bytes()
    require(len(raw) == info['bytes'] and git_blob(raw) == info['git_blob'],
            'candidate Git blob / byte-length drift: ' + info['path'])
    return raw

def check_article(slug: str, body: bytes, metadata: bytes, seen_numbers: set) -> dict:
    data = strict_json(metadata)
    require(type(data) is dict and data.get('slug') == slug, 'metadata route mismatch: ' + slug)
    n = data.get('n')
    require(type(n) is int and 1 <= n <= 35 and n not in seen_numbers, 'article number collision')
    seen_numbers.add(n)
    require(type(data.get('title')) is str and data['title'].strip(), 'missing article title')
    require(type(data.get('section')) is str and data['section'].strip(), 'missing section')
    require(data.get('track') in ('modern', 'historical'), 'invalid editorial track')
    status = data.get('status')
    require(type(status) is dict and status.get('publish') == 'draft', 'publication state escalated')
    safety = data.get('safety_review')
    require(type(safety) is dict and safety.get('state') == 'pending' and safety.get('reviewer') is None,
            'safety review escalated / forged reviewer')
    source_use = data.get('source_use')
    require(type(source_use) is dict and bool(source_use), 'lost original reading-scope metadata')
    require(all(type(k) is str and SLUG.fullmatch(k) and type(v) is str and v.strip()
                for k, v in source_use.items()), 'malformed original source-use text')
    html = body.decode('utf-8')
    cited = CITE.findall(html)
    require(cited and set(cited) <= set(source_use), 'unbound original source citation')
    require('<' in html and '>' in html and len(html) > 300, 'article body is missing/empty')
    return {'n': n, 'slug': slug, 'source_use_ids': len(source_use),
            'literal_citation_occurrences': len(cited), 'track': data['track'],
            'section': data['section'], 'draft': True, 'safety_pending': True}

def check_native(root: Path, manifest: dict, expected_count: int = 35) -> dict:
    rows = check_manifest(manifest, expected_count=expected_count)
    directory = root / 'content/articles'
    require(directory.is_dir() and not directory.is_symlink(), 'article directory unavailable')
    actual = {p.name for p in directory.iterdir()
              if p.name.endswith(('.meta.json', '.body.html'))}
    expected = {info['path'].rsplit('/', 1)[1]
                for row in rows for info in [row['body'], row['meta']]}
    require(actual == expected, 'missing/extra/duplicate candidate article files')
    seen = set()
    receipt = []
    for row in rows:
        receipt.append(check_article(row['slug'], read_pinned(root, row['body']),
                                     read_pinned(root, row['meta']), seen))
    require(seen == set(range(1, expected_count + 1)), 'original 1-35 article slate incomplete')
    return {'state': STATE, 'native_candidate_article_pairs_checked': len(receipt),
            'literal_citations': sum(x['literal_citation_occurrences'] for x in receipt),
            'authored_source_use_memberships': sum(x['source_use_ids'] for x in receipt),
            'native_build_pass': False, 'qualified_qd_pass': False,
            'publication_authorized': False, 'commercial_conversion_verified': False,
            'article_rows': receipt}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    opt = parser.parse_args(argv)
    try:
        snapshot = strict_json((opt.root / 'reviews/r476_35_article_candidate_custody.json').read_bytes())
        result = check_native(opt.root, snapshot)
    except (OSError, UnicodeError, TypeError, Hold, KeyError, json.JSONDecodeError) as exc:
        result = {'state': 'R476_NATIVE_INPUT_OR_EVIDENCE_HARD_HOLD', 'reason': str(exc),
                  'native_build_pass': False, 'qualified_qd_pass': False,
                  'publication_authorized': False}
    print(json.dumps(result, sort_keys=True))
    return 2  # Even a 35/35 structural match NEVER means the advice is safe or publishable.

if __name__ == '__main__':
    sys.exit(main())
