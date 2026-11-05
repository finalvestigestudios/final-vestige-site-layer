#!/usr/bin/env python3
"""R137: custody-bound, author-scoped Preparedness source adjudication dossier.

Read only. This does NOT approve guidance, qualify reviewers, publish, or authorize sales.
Requires the immutable R133 article/source corpus and exact 35/2,000/244/32 baseline.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, urlunsplit

HOLD = 'HOLD_QUALIFIED_SOURCE_AND_SAFETY_REVIEW_REQUIRED'
CITE = re.compile(r'\{\{cite:([a-z0-9][a-z0-9-]*)\}\}')
COUNTS = {'articles': 35, 'citations': 2000, 'sources': 244,
          'literal_urls': 202, 'aliases': 201, 'groups': 32, 'files': 80}


class ReviewHold(ValueError):
    pass


def check(truth: bool, code: str) -> None:
    if not truth:
        raise ReviewHold(code)


def digest(blob: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(blob)).encode() + b'\0' + blob).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(url: str) -> str:
    """Only terminal slash parity. Never merge domains, schemes, query strings or scopes."""
    check(isinstance(url, str) and url.startswith('https://'), 'SOURCE_URL_NOT_HTTPS')
    p = urlsplit(url)
    check(bool(p.hostname) and not p.username and not p.password and not p.fragment,
          'SOURCE_URL_MALFORMED')
    return urlunsplit((p.scheme, p.netloc, (p.path or '/').rstrip('/') or '/', p.query, ''))


def witness(value) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode()).hexdigest()


def audit(repo: Path, *, expected=COUNTS) -> dict:
    prep = repo / 'preparedness'
    frozen = load(prep / 'docs/r133/locked_files.json')
    check(frozen.get('release_status') == 'DRAFT_HUMAN_REVIEW_HOLD', 'NOT_FROZEN_DRAFT')
    for key in ('may_publish', 'qd_pass', 'medical_safety_verified', 'merchant_offer_verified'):
        check(frozen.get(key) is False, 'FORGED_FROZEN_GATE:' + key)
    entries = frozen.get('files')
    check(isinstance(entries, list) and len(entries) == expected['files'], 'FROZEN_FILES_DRIFT')
    paths = [e.get('path') for e in entries]
    check(len(set(paths)) == len(paths), 'DUPLICATE_FROZEN_PATH')
    for entry in entries:
        name, sha = entry['path'], entry['blob_sha']
        check(isinstance(name, str) and name.startswith('preparedness/') and
              '..' not in Path(name).parts and isinstance(sha, str) and
              bool(re.fullmatch('[a-f0-9]{40}', sha)), 'MALFORMED_CUSTODY_ENTRY')
        p = repo / name
        check(p.is_file() and digest(p.read_bytes()) == sha, 'GIT_BLOB_CUSTODY_DRIFT:' + name)
    body_names = sorted((prep / 'content/articles').glob('*.body.html'))
    meta_names = sorted((prep / 'content/articles').glob('*.meta.json'))
    check(len(body_names) == len(meta_names) == expected['articles'], 'ARTICLE_COUNT_DRIFT')
    check({p.relative_to(repo).as_posix() for p in body_names + meta_names} ==
          {n for n in paths if n.endswith(('.body.html', '.meta.json'))}, 'ARTICLE_PATH_DRIFT')
    taxonomy = load(prep / 'taxonomy.json')
    slate = taxonomy.get('slate')
    check(isinstance(slate, list) and len(slate) == expected['articles'] and
          len({x.get('slug') for x in slate}) == expected['articles'], 'TAXONOMY_ROUTE_COLLISION')
    cross = load(prep / 'sources/crosswalk.json')
    check(cross.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
          'CROSSWALK_APPROVAL_FORGERY')
    source_files = cross.get('source_files')
    check(isinstance(source_files, list) and len(source_files) == 8, 'SOURCE_REGISTER_DRIFT')
    register = {}
    all_rows = []
    for spec in source_files:
        origin, file = spec['origin'], spec['path']
        check(origin not in register and file in paths, 'SOURCE_FILE_UNBOUND')
        records = load(repo / file)['sources']
        check(len(records) == spec['count'], 'SOURCE_REGISTER_COUNT_DRIFT:' + origin)
        check(digest((repo / file).read_bytes()) == spec['git_blob_sha'],
              'SOURCE_REGISTER_BLOB_DRIFT:' + origin)
        check(len({r['id'] for r in records}) == len(records), 'DUPLICATE_AUTHOR_SOURCE_ID')
        register[origin] = records
        for i, source in enumerate(records):
            all_rows.append({'origin': origin, 'source_file': file,
                             'row_index': i, 'source': source})
    check(len(all_rows) == cross.get('raw_source_rows') == expected['sources'],
          'SOURCE_ROW_CENSUS_DRIFT')
    byalias = defaultdict(list)
    for row in all_rows:
        byalias[canonical(row['source']['url'])].append(row)
    check(len({r['source']['url'] for r in all_rows}) == expected['literal_urls'] and
          len(byalias) == expected['aliases'], 'SOURCE_URL_CENSUS_DRIFT')
    repeated = {url: rows for url, rows in byalias.items() if len(rows) > 1}
    check(len(repeated) == expected['groups'] and len(cross.get('groups', [])) ==
          expected['groups'], 'SHARED_GROUP_COUNT_DRIFT')
    crossgroups = {}
    for group in cross['groups']:
        key = canonical(group['url'])
        check(key in repeated and key not in crossgroups, 'GROUP_ALIAS_MISMATCH')
        check(group.get('review_status') == 'pending-human-source-and-reading-scope-review' and
              group.get('reviewer') is None and group.get('reviewed_on') is None,
              'UNAUTHORIZED_SHARED_SOURCE_APPROVAL')
        actual = repeated[key]
        variants = group.get('variants', [])
        check(len(variants) == len(actual), 'MISSING_AUTHOR_SOURCE_VARIANT')
        identities = group.get('identities', [])
        check(len(identities) == len(actual), 'MISSING_SOURCE_IDENTITY')
        indexed = {(r['origin'], r['row_index']): r for r in actual}
        observed = set()
        for v in variants:
            index = (v.get('origin'), v.get('row_index'))
            check(index in indexed and index not in observed, 'WRONG_OR_DUPLICATE_VARIANT')
            source = indexed[index]
            check(v.get('source_file') == source['source_file'] and
                  v.get('source') == source['source'], 'AUTHOR_SCOPE_OR_SOURCE_EXPLANATION_DRIFT')
            observed.add(index)
        check({(i['origin'], i['row_index'], i['id']) for i in identities} ==
              {(r['origin'], r['row_index'], r['source']['id']) for r in actual},
              'GROUP_IDENTITY_DRIFT')
        crossgroups[key] = group
    check(set(crossgroups) == set(repeated), 'UNCROSSWALKED_SOURCE_ALIAS')
    byid = {origin: {s['id']: s for s in items} for origin, items in register.items()}
    exposure = defaultdict(list)
    article_rows = []
    total = 0
    slugs = set()
    for mp in meta_names:
        m = load(mp)
        slug = m.get('slug')
        check(slug == mp.name[:-10] and slug not in slugs, 'ARTICLE_SLUG_DRIFT')
        slugs.add(slug)
        origin = cross['article_origins'].get(slug)
        check(origin in register, 'UNMAPPED_ARTICLE_ORIGIN:' + slug)
        st = m.get('status') or {}
        check(st.get('publish') == 'draft' and st.get('editorial') == 'drafted',
              'UNAUTHORIZED_ARTICLE_RELEASE:' + slug)
        s = m.get('safety_review') or {}
        check(s.get('state') in ('pending', 'not-required', 'approved'),
              'MALFORMED_HISTORICAL_SAFETY_STATE')  # original frozen blob governs exact value
        body = (prep / 'content/articles' / (slug + '.body.html')).read_text(encoding='utf-8')
        citations = CITE.findall(body)
        total += len(citations)
        scopes = m.get('source_use')
        check(isinstance(scopes, dict) and set(scopes) == set(citations),
              'MISSING_AUTHOR_READING_SCOPE:' + slug)
        for sid in sorted(scopes):
            actual_origin = origin if sid in byid[origin] else 'base'
            source = byid[actual_origin].get(sid)
            check(source is not None and isinstance(scopes[sid], str) and
                  bool(scopes[sid].strip()), 'UNRESOLVED_AUTHOR_CITATION:' + slug + ':' + sid)
            key = canonical(source['url'])
            if key in crossgroups:
                exposure[(key, actual_origin, sid)].append({
                    'article_slug': slug, 'citation_id': sid,
                    'literal_url': source['url'], 'author_reading_scope': scopes[sid],
                    'citation_occurrences': citations.count(sid)})
        article_rows.append({'slug': slug, 'origin': origin, 'citation_occurrences': len(citations),
                             'source_use_ids': len(scopes), 'status': 'DRAFT_HOLD'})
    check(slugs == {x['slug'] for x in slate} == set(cross['article_origins']),
          'SLATE_OR_ARTICLE_ORIGIN_DRIFT')
    check(total == expected['citations'] == frozen['expected_citation_occurrences'],
          'CITATION_OCCURRENCE_DRIFT')
    dossiers = []
    for n, (key, group) in enumerate(sorted(crossgroups.items()), 1):
        variants = []
        for variant in sorted(group['variants'], key=lambda v: (v['origin'], v['source']['id'])):
            source = variant['source']
            references = sorted(exposure.get((key, variant['origin'], source['id']), []),
                                key=lambda x: x['article_slug'])
            variants.append({'origin': variant['origin'], 'id': source['id'],
                             'source_file': variant['source_file'], 'row_index': variant['row_index'],
                             'literal_url': source['url'], 'publisher': source.get('publisher'),
                             'supports': source.get('supports'), 'notes': source.get('notes'),
                             'human_link_check': source.get('human_link_check'),
                             'article_reading_scopes': references,
                             'uncited_variant_not_an_approval': not bool(references)})
        row = {'group_index': n, 'review_alias': key,
               'status': 'UNREVIEWED_HUMAN_REQUIRED',
               'variants': variants,
               'reviewer_instruction': 'Compare actual source passages and every author-scoped reading; preserve differences. No medical or QD approval.'}
        row['witness_sha256'] = witness(row)
        dossiers.append(row)
    return {'status': HOLD, 'may_publish': False, 'qd_pass': False,
            'medical_safety_verified': False, 'merchant_offer_verified': False,
            'candidate_parent': frozen['candidate_parent'],
            'frozen_manifest_sha256': witness(frozen),
            'stats': {'frozen_files': len(entries), 'articles': len(slugs),
                      'citations': total, 'source_rows': len(all_rows),
                      'literal_source_urls': expected['literal_urls'],
                      'review_aliases': len(byalias), 'shared_groups': len(dossiers),
                      'author_source_uses': sum(r['source_use_ids'] for r in article_rows),
                      'uncited_group_variants': sum(not v['article_reading_scopes']
                                                     for g in dossiers for v in g['variants'])},
            'articles': sorted(article_rows, key=lambda a: a['slug']),
            'source_group_dossiers': dossiers,
            'warning': 'Structural provenance is NOT scientific source verification. All 32 groups and safety passages remain HUMAN HOLD.'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path('.'))
    args = ap.parse_args(argv)
    try:
        print(json.dumps(audit(args.repo), indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    except (ReviewHold, KeyError, OSError, TypeError, ValueError, UnicodeError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
