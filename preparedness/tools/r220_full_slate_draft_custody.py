#!/usr/bin/env python3
"""R220: immutable 35-article -> 41-draft WordPress custody; read-only, HOLD-only.

Checks two distinct source identities: R200 contributor originals and the R219
integration head. A changed integrated body is NOT an approval or an error if its
exact SHA is on the explicit review docket. Native build and independent human
review remain separate mandatory gates.
"""
from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 'fv-preparedness-r220-full-slate-draft-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
MANIFEST_PATH = 'audits/r200_seven_cluster_35_article_frozen_custody.json'
MANIFEST_BLOB = '5822f9dfde21d1f3bdfc26658769d852c639438c'
# R221 authenticated module: 35 frozen routes + 6 tools + 2026-11-08 taxonomy.
R221_AUTHORITY_PATH = 'tools/r221_frozen_route_tool_authority.py'
R221_AUTHORITY_BLOB = '88a8d37955957b4e1cba7a73e73ed4ee1e2fe0d1'
# R222 pins the renderer, source registers/fragments, CSS and nine inline scripts.
R222_BUNDLE_PATH = 'tools/r222_producer_source_bundle_gate.py'
R222_BUNDLE_BLOB = '31ee5604ccff115ded6b856ec175fa82776e08eb'
# These are independently observed R219 integration Git blobs, not certified text.
# Missing entries MUST match the older R200 original exactly.
INTEGRATED_DIFFS = {
     1: 'f81cd43516e8295104230412f18776919148f905',
     2: '933f38ff3cd55a241cf9b392014fc52d4961e84f',
    12: '2cd3e30b3a7e3dfdb3fd30cfd2b832355f58dfe2',
    13: '0412484304a3bcf08f0bb1b170110f617e3c2869',
    14: 'de3cb805041904cf22d4f216296bd4c8ddec17c1',
    15: '8ac8bd7dba3be15d477c15737e54d83364d72527',
    16: 'e5910015fc6e33ad015bc5dc0605b86622b701be',
    20: '68344cf6c4022285fffb2a01f42027bf6f9ee95d',
    24: '058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7',
    25: '0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5',
    27: '2ff8d029769aa9a97de6b1e388d937899f3af38c',
    32: '3c02e58c30d1d608224944142f31fbead44a1252',
    33: 'd56df76647d2598f35cfd4609f91649cef063f12',
    34: 'ad158ee898f76d05bcb65c845b1e4a0e8103c660',
}
INTEGRATED_META_DIFFS = {
     2: '1c69d5f1636a3a41631a5d93f11254d85cbe1b59',
     6: '827d861eb3beebfd010ee98fcca764b23a2de90e',
     7: '91c730bd1c7a61fa3140a86245c9bc0c88160c29',
    12: 'be37b602d0b82593d438083dfc8a1e5ef595dd44',
    13: 'ff1246dcbfb0dd0bc864977f815badb9ad4e7ed8',
    14: 'cb559141d1e4a39debad16cf5cb796b746a01f19',
    15: 'dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3',
    20: 'ba840917f34634ccd634c488eeca4a8a6b3a8fe2',
    21: '1c4c5396da703f3724b584c67e49e2128ab1f4c6',
    24: '7191acba55d63dc405ad9c2003d66193276da89f',
    25: '03d3824e07fe51931671d0ddc7aa8c85eda58435',
    34: '4d2dc4958736e3c5257c65dda8ed016a473ac6be',
}
EXPECTED_EXCEPTIONS = {(7, 'cdc-find-clean-water'): 2,
                       (20, 'start-ready-plan'): 1}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|([^}]+)\}\}')
TOKEN = re.compile(r'\{\{[^}]*\}\}')
SAFE_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def strict_object(data: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def reject_constant(x):
        raise ValueError('nonfinite JSON literal: ' + x)
    result = json.loads(data.decode('utf-8', 'strict'), object_pairs_hook=unique,
                        parse_constant=reject_constant)
    if type(result) is not dict:
        raise ValueError('expected JSON object')
    return result


def safe_read(root: Path, relative: str) -> bytes:
    """Reject symlink ancestors, missing paths and escapes, including checkout root."""
    if not relative or relative.startswith('/') or '\\' in relative:
        raise ValueError('unsafe relative path: ' + relative)
    parts = Path(relative).parts
    if any(p in ('', '.', '..') for p in parts):
        raise ValueError('path traversal: ' + relative)
    current = root
    for segment in parts:
        if current.is_symlink():
            raise ValueError('symlink ancestor: ' + str(current))
        current = current / segment
    if current.is_symlink() or not current.is_file():
        raise ValueError('missing or symlinked input: ' + relative)
    return current.read_bytes()


def verify_roster(doc: dict) -> list[dict]:
    if (doc.get('schema') != 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1'
            or doc.get('state') != HOLD or doc.get('issue') != 136
            or doc.get('conversion_issue') != 820
            or doc.get('artifact_count') != 35
            or doc.get('export_target_count_with_six_tools') != 41):
        raise ValueError('R200 governance / count mismatch')
    for flag in ('publication_authorized', 'independent_qd_pass',
                 'human_source_approved', 'medical_safety_verified',
                 'merchant_offer_verified'):
        if doc.get(flag) is not False:
            raise ValueError('false release flag missing: ' + flag)
    heads = doc.get('branch_heads')
    if type(heads) is not dict or set(heads) != {
        'start', 'shelter', 'food', 'health', 'hist-field', 'hist-food', 'hist-home'
    } or any(not re.fullmatch('[0-9a-f]{40}', x) for x in heads.values()):
        raise ValueError('seven original contributor identities required')
    articles = doc.get('articles')
    if type(articles) is not list or len(articles) != 35:
        raise ValueError('exactly 35 frozen articles required')
    routes = set()
    for n, a in enumerate(articles, 1):
        if (type(a) is not dict or type(a.get('n')) is not int or a['n'] != n
                or a.get('source_cluster') not in heads
                or a.get('branch_sha') != heads[a['source_cluster']]):
            raise ValueError('frozen contributor mapping drift at #' + str(n))
        slug = a.get('slug'); section = a.get('section'); route = a.get('route')
        if (not isinstance(slug, str) or SAFE_SLUG.fullmatch(slug) is None
                or not isinstance(section, str) or SAFE_SLUG.fullmatch(section) is None
                or route != f'/preparedness/{section}/{slug}/'
                or route in routes):
            raise ValueError('duplicate/invalid canonical route at #' + str(n))
        routes.add(route)
        for key in ('body_oid', 'meta_oid'):
            if not re.fullmatch('[0-9a-f]{40}', str(a.get(key, ''))):
                raise ValueError('frozen object ID missing: ' + key)
    if not set(INTEGRATED_DIFFS) <= set(range(1, 36)):
        raise ValueError('integration docket has unknown article')
    return articles


def verify_originals(root: Path, articles: list[dict]) -> tuple[list[dict], dict]:
    status = []; exceptions = {}
    for a in articles:
        n = a['n']; slug = a['slug']
        raw = safe_read(root, f'content/articles/{slug}.body.html')
        actual = git_blob(raw)
        expected = INTEGRATED_DIFFS.get(n, a['body_oid'])
        if actual != expected:
            raise ValueError(f'#{n} changed without reviewed custody receipt: {actual}')
        meta_raw = safe_read(root, f'content/articles/{slug}.meta.json')
        expected_meta = INTEGRATED_META_DIFFS.get(n, a['meta_oid'])
        if git_blob(meta_raw) != expected_meta:
            raise ValueError(f'#{n} metadata changed without custody receipt')
        meta = strict_object(meta_raw)
        if (meta.get('n') != n or meta.get('slug') != slug
                or meta.get('section') != a['section']
                or meta.get('track') != a['track']
                or meta.get('status', {}).get('publish') != 'draft'
                or not isinstance(meta.get('source_use'), dict)):
            raise ValueError(f'#{n} metadata/slug/status contradiction')
        # A historically authored safety label is NOT an independent QD PASS.
        safety = meta.get('safety_review', {})
        if not isinstance(safety, dict) or safety.get('state') not in (
                'pending', 'approved', 'not-required'):
            raise ValueError(f'#{n} missing/invalid legacy safety label')
        body = raw.decode('utf-8', 'strict')
        tokens = [m.group(0) for m in TOKEN.finditer(body)]
        cited = [m.group(1) for m in CITE.finditer(body)]
        linked = [m.group(1) for m in LINK.finditer(body)]
        allowed = {m.group(0) for m in CITE.finditer(body)} | {
            m.group(0) for m in LINK.finditer(body)}
        allowed |= {m.group(0) for m in re.finditer(r'\{\{inline-js:[a-z_]+\.js\}\}', body)}
        if any(t not in allowed for t in tokens):
            raise ValueError(f'#{n} unknown template opcode')
        slugs = {x['slug'] for x in articles}
        if any(x not in slugs for x in linked):
            raise ValueError(f'#{n} internal link outside frozen roster')
        missing = {}
        for sid in cited:
            if sid not in meta['source_use']:
                missing[sid] = missing.get(sid, 0) + 1
        for sid, times in missing.items():
            exceptions[(n, sid)] = times
        status.append({'n': n, 'slug': slug, 'source_cluster': a['source_cluster'],
                       'original_blob': a['body_oid'], 'integrated_blob': actual,
                       'changed_since_original': actual != a['body_oid'],
                       'citations': len(cited), 'sources': len(set(cited)),
                       'links': len(linked), 'meta_blob': git_blob(meta_raw),
                       'route': a['route'], 'legacy_safety_label': safety['state']})
    if exceptions != EXPECTED_EXCEPTIONS:
        raise ValueError('source-use explanations changed; independently adjudicate: ' + str(exceptions))
    return status, {f'{n}:{sid}': count for (n, sid), count in exceptions.items()}


def verify_render(root: Path, articles: list[dict], report: dict, library, builder) -> dict:
    actual = report.get('articles')
    if type(actual) is not list or len(actual) != 41:
        raise ValueError('expected 41 individual article/tool build-report entries')
    by_slug = {}
    for row in actual:
        if type(row) is not dict or not isinstance(row.get('slug'), str):
            raise ValueError('invalid build-report article entry')
        if row['slug'] in by_slug:
            raise ValueError('duplicate WordPress export slug: ' + row['slug'])
        by_slug[row['slug']] = row
    frozen_slugs = {a['slug'] for a in articles}
    if not frozen_slugs <= set(by_slug) or set(by_slug) != set(library.articles):
        raise ValueError('frozen articles or six tools missing / extra exports')
    if set(library.articles) - frozen_slugs != {
        p.name.removesuffix('.meta.json') for p in (root / 'content' / 'tools').glob('*.meta.json')
    } or len(set(library.articles) - frozen_slugs) != 6:
        raise ValueError('exact six existing tools required')
    seen_routes = set()
    for slug, meta in library.articles.items():
        route = library.url_path(slug)
        if route in seen_routes:
            raise ValueError('colliding route: ' + route)
        seen_routes.add(route)
        expected, order = builder.resolve_tokens(library, meta)
        row = by_slug[slug]
        if (row.get('canonical') != 'https://finalvestige.com' + route
                or row.get('sources') != order
                or row.get('words') != builder.word_count(expected)):
            raise ValueError('build-report source/canonical/reading-depth drift: ' + slug)
        wrapper = '<div class="pa-body" id="pa-main">' + expected + '</div>'
        for mode in ('wp', 'preview'):
            raw = safe_read(root, f'build/{mode}/{slug}.html')
            page = raw.decode('utf-8', 'strict')
            if page.count(wrapper) != 1:
                raise ValueError('body lost, truncated, duplicated or hidden in ' + mode + ':' + slug)
            if page.count('class="pa-body" id="pa-main"') != 1:
                raise ValueError('unexpected duplicate article body in ' + mode + ':' + slug)
            if meta['status']['publish'] != 'draft':
                raise ValueError('published article disallowed')
            if 'Independent safety/source and QD verification pending' not in page:
                raise ValueError('mandatory warning absent in ' + mode + ':' + slug)
    if report.get('release_evidence', {}).get('wordpress_publication_performed') is not False:
        raise ValueError('WordPress publication flag must remain false')
    if report.get('release_evidence', {}).get('independent_qa_verified') is not False:
        raise ValueError('independent QA flag must remain false')
    return {'exports_verified': len(by_slug), 'draft_channels': 2,
            'channel_files_verified': 2 * len(by_slug), 'canonical_routes': len(seen_routes)}


def load_r221_authority(root: Path):
    """Import only the exact read-only R221 authority bytes pinned by this gate."""
    source = safe_read(root, R221_AUTHORITY_PATH)
    if git_blob(source) != R221_AUTHORITY_BLOB:
        raise ValueError('R221 frozen-authority module identity mismatch')
    spec = importlib.util.spec_from_file_location(
        'fv_preparedness_r221_frozen_authority', root / R221_AUTHORITY_PATH)
    if spec is None or spec.loader is None:
        raise ValueError('R221 module cannot be loaded')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def load_r222_bundle(root: Path):
    """Pin the R222 gate itself before checking any mutable build dependencies."""
    source = safe_read(root, R222_BUNDLE_PATH)
    if git_blob(source) != R222_BUNDLE_BLOB:
        raise ValueError('R222 producer/source custody gate identity mismatch')
    spec = importlib.util.spec_from_file_location(
        'fv_preparedness_r222_source_bundle', root / R222_BUNDLE_PATH)
    if spec is None or spec.loader is None:
        raise ValueError('R222 bundle gate cannot be loaded')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def audit(root: Path, *, verify_exports: bool = True) -> dict:
    result = {'schema': SCHEMA, 'state': INVALID, 'issue': 136, 'conversion_issue': 820,
              'publication_authorized': False, 'independent_qd_pass': False,
              'human_claim_verified': False, 'medical_safety_verified': False,
              'merchant_offer_verified': False, 'errors': [], 'articles': [],
              'reconciliation': None, 'source_exceptions': None}
    try:
        original = safe_read(root, MANIFEST_PATH)
        if git_blob(original) != MANIFEST_BLOB:
            raise ValueError('frozen manifest identity changed')
        roster = verify_roster(strict_object(original))
        authority = load_r221_authority(root)
        result['authorities'] = authority.verify_authorities(root, roster, safe_read)
        # Fail before importing or executing the mutable WordPress producer.
        bundle = load_r222_bundle(root)
        result['producer_sources'] = bundle.check_bundle(root, safe_read)
        status, exceptions = verify_originals(root, roster)
        result['articles'] = status
        result['source_exceptions'] = exceptions
        if verify_exports:
            # Only imports the repository's own build code from its trusted tools path.
            tools_path = root / 'tools'
            if tools_path.is_symlink() or not tools_path.is_dir():
                raise ValueError('untrusted tools directory')
            sys.path.insert(0, str(tools_path))
            try:
                import build
                library = build.Library(root=root)
                authority.verify_routes(roster, library)
                report = strict_object(safe_read(root, 'build/build-report.json'))
                result['render'] = verify_render(root, roster, report, library, build)
            finally:
                sys.path.remove(str(tools_path))
        result['reconciliation'] = {'frozen_articles': 35,
                                    'integrated_changes_held_for_review': sum(
                                        x['changed_since_original'] for x in status),
                                    'unchanged_originals': sum(not x['changed_since_original'] for x in status),
                                    'word_level_review': 'REQUIRED',
                                    'source_url_adjudication': 'REQUIRED'}
        result['state'] = HOLD
    except (ValueError, KeyError, OSError, ImportError, TypeError, UnicodeError) as exc:
        result['errors'].append(str(exc))
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', required=True, type=Path, help='path to preparedness directory')
    ap.add_argument('--originals-only', action='store_true',
                    help='skip build outputs; still never grant any release PASS')
    args = ap.parse_args(argv)
    result = audit(args.root, verify_exports=not args.originals_only)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2 if result['state'] == HOLD else 3


if __name__ == '__main__':
    sys.exit(main())
