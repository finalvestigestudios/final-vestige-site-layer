#!/usr/bin/env python3
"""R171: deterministic eight-inventory / 35-article source-claim linkage gate.

Structural custody only. A source URL, automated fetch, matching citation, or
synthetic PASS never grants medical/food safety approval, QD or publication.
Always returns process status 2 (HARD HOLD), even for a valid snapshot.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r171-source-claim-crosswalk-v1'
HOLD = 'DRAFT_HARD_HOLD'
R151 = 'preparedness/docs/r151/contributor-three-way.json'
R151_SHA = '9cf386519eda970209ff6be4ff0243661cd9d996'
R161 = 'preparedness/docs/r161/body_custody.json'
R161_SHA = 'fede4222c796d92798eff7cf0dcb225c291f7d61'
XW = 'preparedness/sources/crosswalk.json'
XW_SHA = 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9'
ARTICLE_DIR = 'preparedness/content/articles'
FRAGS = ('base', 'start', 'food', 'shelter', 'health', 'hist-field', 'hist-food', 'hist-home')
SOURCES = {'base': 'preparedness/sources/register.json', **{
    name: f'preparedness/sources/fragments/{name}.json' for name in FRAGS if name != 'base'}}
SHA = re.compile(r'[0-9a-f]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def check(ok: object, error: str) -> None:
    if not ok:
        raise ValueError(error)


def blob(b: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(b)).encode('ascii') + b'\0' + b).hexdigest()


def read_pinned(root: Path, path: str, expected: str) -> bytes:
    p = root / path
    check(p.is_file() and not p.is_symlink(), 'missing/symlink source: ' + path)
    b = p.read_bytes()
    check(blob(b) == expected, 'source SHA drift: ' + path)
    return b


def valid_url(url: object) -> None:
    check(type(url) is str and 9 <= len(url) <= 500, 'source URL type/length')
    u = urlsplit(url)
    check(u.scheme == 'https' and bool(u.hostname) and
          not u.username and not u.password and not u.fragment and
          '\\' not in url and not any(ch.isspace() for ch in url),
          'source URL is not approved for structural indexing')
    check(not u.hostname.endswith('.') and '..' not in u.hostname, 'malformed source host')


def evaluate(crosswalk: dict, registers: dict, metadata: dict, legacy: dict,
             custody: dict, *, strict: bool = True) -> dict:
    """Pure function; strict=False is ONLY for offline synthetic tests."""
    check(type(crosswalk) is dict and crosswalk.get('schema_version') == 1, 'crosswalk schema drift')
    check(crosswalk.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
          'crosswalk review status escalated')
    check(type(legacy) is dict and legacy.get('schema') == 'fv-preparedness-r151-v1' and
          legacy.get('decision') == HOLD and legacy.get('qd_pass') is False and
          legacy.get('qualified_safety_review') is False, 'seven-source baseline authority drift')
    check(type(custody) is dict and custody.get('schema') == 'fv-preparedness-r161-body-custody-v1' and
          custody.get('status') == HOLD, 'body custody authority drift')
    heads = legacy.get('branch_heads')
    check(type(heads) is dict and len(heads) == 7 and
          set(heads) == set(FRAGS) - {'base'} and
          all(type(v) is str and SHA.fullmatch(v) for v in heads.values()),
          'seven contributor SHA custody lost')
    files = crosswalk.get('source_files')
    check(type(files) is list and len(files) == 8 and
          {f.get('origin') for f in files} == set(FRAGS), 'source file inventory changed')
    references = {}
    for entry in files:
        name, path, expected, count = (entry.get(k) for k in
             ('origin', 'path', 'git_blob_sha', 'count'))
        check(type(name) is str and name in SOURCES and path == SOURCES[name],
              'source file path/origin drift')
        check(type(expected) is str and SHA.fullmatch(expected), 'source file SHA malformed')
        check(type(count) is int and count > 0, 'source record count malformed')
        row = registers.get(name)
        check(type(row) is dict and set(row) == {'sha', 'sources'}, 'source inventory unavailable')
        check(row['sha'] == expected and type(row['sources']) is list and len(row['sources']) == count,
              'source inventory SHA/count drift: ' + name)
        references[name] = row['sources']
    all_records = []
    by_id, by_url = {}, {}
    for name in FRAGS:
        for index, src in enumerate(references[name]):
            check(type(src) is dict, 'source record malformed')
            sid, url = src.get('id'), src.get('url')
            check(type(sid) is str and SLUG.fullmatch(sid), 'source id malformed')
            valid_url(url)
            check(src.get('human_link_check') is False,
                  'source link validation state must be adjudicated, never self-approved')
            record = {'origin': name, 'source_file': SOURCES[name], 'row_index': index, 'source': src}
            all_records.append(record)
            by_id.setdefault(sid, []).append(record)
            by_url.setdefault(url, []).append(record)
    check(all(len({r['source']['url'] for r in variants}) == 1 for variants in by_id.values()),
          'same source identifier resolves to conflicting URLs')
    groups = crosswalk.get('groups')
    check(type(groups) is list, 'source variant groups missing')
    actual_dupe_urls = {url: variants for url, variants in by_url.items() if len(variants) > 1}
    check(len(groups) == len(actual_dupe_urls), 'source shared-URL review docket coverage mismatch')
    seen = set()
    for group in groups:
        check(type(group) is dict, 'source variant review group malformed')
        url = group.get('url')
        check(type(url) is str and url in actual_dupe_urls and url not in seen,
              'duplicate/missing shared source URL group')
        seen.add(url)
        check(group.get('review_status') == 'pending-human-source-and-reading-scope-review' and
              group.get('reviewer') is None and group.get('reviewed_on') is None and
              group.get('canonical_url') == url, 'invented source variant approval/canonical swap')
        actual = actual_dupe_urls[url]
        # Source fragments are ordered independently; crosswalk group order is NOT
        # safety-significant. Compare full records as a multiset, not as a list.
        expected = [{k: row[k] for k in ('origin', 'row_index')} |
                    {'id': row['source']['id']} for row in actual]
        canon = lambda rows: sorted(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows)
        check(type(group.get('variants')) is list and
              canon(group['variants']) == canon(actual),
              'source variants do not match exact eight original registers: ' + url)
        check(type(group.get('identities')) is list and
              canon(group['identities']) == canon(expected),
              'shared-URL identity-to-variant mismatch: ' + url)
    check(type(metadata) is dict and set(metadata) == set(custody.get('articles', {})) and
          set(metadata) == set(legacy.get('metadata_blobs', {})), '35 metadata census changed')
    routes, edges, used_ids = set(), [], set()
    for slug in sorted(metadata):
        check(SLUG.fullmatch(slug), 'article slug malformed')
        meta = metadata[slug]
        check(type(meta) is dict and meta.get('slug') == slug and
              meta.get('status', {}).get('publish') == 'draft', 'article identity/publication drift')
        section = meta.get('section')
        check(type(section) is str and SLUG.fullmatch(section), 'article section malformed')
        route = f'/preparedness/{section}/{slug}/'
        check(route not in routes, 'duplicate article route')
        routes.add(route)
        uses = meta.get('source_use')
        check(type(uses) is dict and uses, 'missing article source interpretation')
        for sid, explanation in sorted(uses.items()):
            check(type(sid) is str and sid in by_id, 'orphaned article citation ID: ' + str(sid))
            check(type(explanation) is str and len(explanation.strip()) >= 8,
                  'missing author source/claim interpretation')
            used_ids.add(sid)
            edges.append((slug, route, sid, by_id[sid][0]['source']['url']))
    check(crosswalk.get('raw_source_rows') == len(all_records) and
          crosswalk.get('unique_source_urls') == len(by_url) and
          crosswalk.get('duplicate_url_groups') == len(actual_dupe_urls) and
          crosswalk.get('duplicate_id_groups') == sum(len(v) > 1 for v in by_id.values()),
          'historical source census disagrees with actual registers')
    check(type(custody.get('article_count')) is int and
          custody.get('article_count') == len(metadata), 'body/article count disagreement')
    check(type(custody.get('article_source_relationships')) is int and
          custody['article_source_relationships'] == len(edges),
          'body/source-use link count disagreement')
    if strict:
        check(len(metadata) == 35 and len(edges) == 385 and len(routes) == 35 and
              len(all_records) == 244 and len(by_url) == 202 and
              len(actual_dupe_urls) == 32 and len(by_id) == 225,
              'source-to-claim full baseline count changed')
    receipt = hashlib.sha256(json.dumps(edges, ensure_ascii=False,
                separators=(',', ':')).encode('utf-8')).hexdigest()
    return {'schema': SCHEMA, 'state': HOLD, 'article_routes': len(routes),
            'article_source_uses': len(edges), 'source_registry_rows': len(all_records),
            'source_distinct_ids': len(by_id), 'source_distinct_urls': len(by_url),
            'shared_url_groups_pending_human_review': len(actual_dupe_urls),
            'same_id_multi_inventory_groups': sum(len(v) > 1 for v in by_id.values()),
            'article_source_link_receipt_sha256': receipt,
            'contributor_clusters_pinned': len(heads),
            'source_urls_independently_human_checked': False,
            'claim_or_medical_safety_approval': False, 'independent_qd_pass': False,
            'paid_product_verified': False, 'publication_authorized': False}


def verify(root: Path) -> dict:
    # The older gate checks all 35 complete source-cited HTML bodies, depth, states, and routes.
    legacy = json.loads(read_pinned(root, R151, R151_SHA))
    custody = json.loads(read_pinned(root, R161, R161_SHA))
    crosswalk = json.loads(read_pinned(root, XW, XW_SHA))
    module_path = root / 'preparedness/tools/r161_body_custody_gate.py'
    check(module_path.is_file() and not module_path.is_symlink(), 'R161 source gate unavailable')
    spec = importlib.util.spec_from_file_location('r161_custody', module_path)
    check(spec is not None and spec.loader is not None, 'R161 source gate import unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    custody_result = module.verify(root)
    check(custody_result.get('state') == HOLD and
          custody_result.get('articles') == 35 and
          custody_result.get('citations') == 2000 and
          custody_result.get('source_uses') == 385 and
          custody_result.get('independent_qd_pass') is False,
          'R161 underlying citation/body custody failed')
    inv = {}
    for origin, path in SOURCES.items():
        file_entry = next((f for f in crosswalk['source_files'] if f['origin'] == origin), None)
        check(file_entry is not None, 'source file entry absent')
        raw = read_pinned(root, path, file_entry['git_blob_sha'])
        inv[origin] = {'sha': file_entry['git_blob_sha'], 'sources': json.loads(raw)['sources']}
    metas = {}
    for slug, sha in legacy['metadata_blobs'].items():
        metas[slug] = json.loads(read_pinned(root, f'{ARTICLE_DIR}/{slug}.meta.json', sha))
    return evaluate(crosswalk, inv, metas, legacy, custody)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path('.'))
    args = ap.parse_args(argv)
    try:
        result = verify(args.repo.resolve(strict=True))
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError, UnicodeError) as ex:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'error': str(ex), 'publication_authorized': False}
    print(json.dumps(result, sort_keys=True))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
