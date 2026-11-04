#!/usr/bin/env python3
"""R123: read-only source-use/citation-to-URL crosswalk for the 35-page HOLD slate.

Inputs are immutable Git blobs named in the R117 nine-head inventory, a pinned
base source-register blob and the existing unresolved human crosswalk. Outputs
are reviewer worklists only. This code does not grant safety, editorial, merchant
or release approval; it neither fetches network pages nor writes to the CMS.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit

SCHEMA = 'fv-preparedness-r117-nine-snapshot-article-source-git-custody-HOLD-v1'
OID = re.compile(r'[0-9a-f]{40}\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
EXPECTED_FRAGMENTS = {'food.json', 'health.json', 'hist-field.json', 'hist-food.json',
                      'hist-home.json', 'shelter.json', 'start.json'}

class Hold(ValueError):
    """Missing, changed or unsafe source-custody evidence."""

def need(condition, code):
    if not condition:
        raise Hold(code)

def strict_json(value):
    def unique(pairs):
        result = {}
        for key, item in pairs:
            need(key not in result, 'DUPLICATE_JSON_KEY:' + key)
            result[key] = item
        return result
    return json.loads(value, object_pairs_hook=unique)

def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def canonical_url(url):
    """Conservative equality key, NOT a redirect or a safe URL-merging policy."""
    need(type(url) is str and url, 'SOURCE_URL_REQUIRED')
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError as ex:
        raise Hold('BAD_SOURCE_URL') from ex
    need(parsed.scheme == 'https' and host and not parsed.username and not parsed.password,
         'HTTPS_HOST_REQUIRED')
    need('\\' not in url and '\n' not in url and '\r' not in url, 'UNSAFE_SOURCE_URL')
    need(port is None or 0 < port < 65536, 'BAD_SOURCE_PORT')
    host = host.lower().rstrip('.')
    need(bool(host) and not host.startswith('.'), 'BAD_SOURCE_HOST')
    authority = f'[{host}]' if ':' in host else host
    if port not in (None, 443):
        authority += ':' + str(port)
    # Path/query/fragment are intentionally NOT normalized. Their difference
    # may change the document, primary-source page or PDF section being read.
    return urlunsplit(('https', authority, parsed.path or '/', parsed.query, parsed.fragment))

def git_reader(repo):
    def fetch(oid):
        need(type(oid) is str and OID.fullmatch(oid) is not None, 'BAD_BLOB_ID')
        process = subprocess.run(['git', '-C', str(repo), 'cat-file', 'blob', oid],
                                 capture_output=True, timeout=25, check=False)
        need(process.returncode == 0, 'MISSING_GIT_BLOB:' + oid)
        return process.stdout
    return fetch

def audit(snapshot, register_oid, crosswalk, read_blob):
    need(type(snapshot) is dict and snapshot.get('schema') == SCHEMA, 'BAD_SNAPSHOT')
    need(snapshot.get('issue') == 136 and snapshot.get('business_issue') == 820, 'ISSUE_SCOPE_MISMATCH')
    gov = snapshot.get('governance', {})
    need(gov.get('release_state') == 'HOLD', 'MISSING_RELEASE_HOLD')
    for field in ('may_publish', 'may_merge', 'independent_QD_PASS',
                  'medical_safety_verified', 'merchant_offer_verified'):
        need(gov.get(field) is False, 'UNAUTHORIZED_APPROVAL:' + field)
    heads = snapshot.get('snapshots')
    need(type(heads) is list and len(heads) == 9, 'NINE_HEADS_REQUIRED')
    before, after, *contributors = heads
    need([v.get('role') for v in heads] == ['baseline', 'candidate'] + ['contributor'] * 7,
         'BAD_HEAD_ORDER')
    need({v.get('cluster') for v in contributors} == {'food', 'health', 'historical-field',
             'historical-food', 'historical-home', 'shelter', 'start-here'}, 'CLUSTERS_CHANGED')
    for head in heads:
        need(type(head.get('sha')) is str and OID.fullmatch(head['sha']) is not None,
             'BAD_COMMIT_SHA')
    bfiles, afiles = before.get('article_files'), after.get('article_files')
    need(type(bfiles) is dict and type(afiles) is dict and set(bfiles) == set(afiles),
         'ARTICLE_FILE_ROSTER_DRIFT')
    slugs = sorted(k[:-10] for k in bfiles if k.endswith('.body.html'))
    need(len(slugs) == 35 and len(set(slugs)) == 35 and
         set(bfiles) == {s + ext for s in slugs for ext in ('.body.html', '.meta.json')},
         'NOT_EXACTLY_35_ARTICLE_PAIRS')
    need(type(register_oid) is str and OID.fullmatch(register_oid) is not None,
         'BASE_REGISTER_OID_REQUIRED')
    need(type(crosswalk) is dict and crosswalk.get('status') ==
         'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED', 'CROSSWALK_NOT_HOLD')
    need(type(crosswalk.get('groups')) is list, 'CROSSWALK_GROUPS_REQUIRED')
    if 'duplicate_url_groups' in crosswalk:
        need(crosswalk['duplicate_url_groups'] == len(crosswalk['groups']),
             'CROSSWALK_GROUP_COUNT_CORRUPT')

    seen_blobs = {}
    def get(oid):
        need(type(oid) is str and OID.fullmatch(oid) is not None, 'BAD_OBJECT_ID')
        if oid not in seen_blobs:
            raw = read_blob(oid)
            need(type(raw) is bytes and blob_sha(raw) == oid, 'GIT_BLOB_IDENTITY_MISMATCH:' + oid)
            try:
                seen_blobs[oid] = raw.decode('utf-8')
            except UnicodeError as ex:
                raise Hold('NON_UTF8_GIT_BLOB:' + oid) from ex
        return seen_blobs[oid]

    registry = strict_json(get(register_oid))
    need(type(registry) is dict and type(registry.get('sources')) is list,
         'BASE_SOURCE_REGISTER_INVALID')
    def indexes(rows, origin):
        result = []
        for i, row in enumerate(rows):
            need(type(row) is dict and type(row.get('id')) is str and
                 re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', row['id']) is not None,
                 'BAD_SOURCE_ID:' + origin)
            canonical = canonical_url(row.get('url'))
            result.append({'origin': origin, 'row_index': i, 'id': row['id'],
                           'url': row['url'], 'canonical_url': canonical,
                           'verified_on': row.get('verified_on'),
                           'human_link_check': row.get('human_link_check') is True,
                           'supports': row.get('supports'), 'source': row})
        return result

    base_rows = indexes(registry['sources'], 'base')
    blocked = []
    review_rows = []
    per_version = {}
    for label, head in [('original', before), ('candidate', after)]:
        fragments = head.get('source_fragments')
        need(type(fragments) is dict and set(fragments) == EXPECTED_FRAGMENTS | {'README.md'},
             'FRAGMENT_ROSTER_CHANGED:' + label)
        source_rows = list(base_rows)
        for filename in sorted(EXPECTED_FRAGMENTS):
            data = strict_json(get(fragments[filename]))
            need(type(data) is dict and type(data.get('sources')) is list,
                 'BAD_SOURCE_FRAGMENT:' + filename)
            source_rows.extend(indexes(data['sources'], filename.removesuffix('.json')))
        by_id = defaultdict(list)
        by_url = defaultdict(list)
        for source in source_rows:
            by_id[source['id']].append(source)
            by_url[source['canonical_url']].append(source)
        per_version[label] = {'by_id': by_id, 'by_url': by_url, 'sources': source_rows}

        for sid in sorted(by_id):
            urls = sorted({s['canonical_url'] for s in by_id[sid]})
            if len(urls) > 1:
                review_rows.append({'code': 'SOURCE_ID_URL_DIVERGENCE', 'version': label,
                                    'source_id': sid, 'urls': urls, 'state': 'UNREVIEWED'})
        for url in sorted(by_url):
            variants = by_url[url]
            if len(variants) > 1:
                review_rows.append({'code': 'SHARED_URL_SOURCE_SCOPE_REVIEW', 'version':label,
                                    'canonical_url':url, 'source_ids':sorted({v['id'] for v in variants}),
                                    'origins':sorted({v['origin'] for v in variants}),
                                    'different_supports':len({v['supports'] for v in variants}) > 1,
                                    'state':'UNREVIEWED'})

    citation_totals = {}
    exposure = defaultdict(lambda: {'original': {}, 'candidate': {}})
    for label, head in [('original', before), ('candidate', after)]:
        cited_total = 0
        source_index = per_version[label]['by_id']
        for slug in slugs:
            body = get(head['article_files'][slug+'.body.html'])
            meta = strict_json(get(head['article_files'][slug+'.meta.json']))
            need(type(meta) is dict and meta.get('slug') == slug, 'ARTICLE_SLUG_CHANGED:' + slug)
            need(type(meta.get('status')) is dict and meta['status'].get('publish') == 'draft',
                 'ARTICLE_PUBLICATION_UPGRADE:' + slug)
            need(type(meta.get('safety_review')) is dict and
                 type(meta['safety_review'].get('state')) is str,
                 'SAFETY_REVIEW_MISSING:' + slug)
            use = meta.get('source_use')
            need(type(use) is dict, 'SOURCE_USE_MISSING:' + slug)
            cites = CITE.findall(body)
            need(body.count('{{cite:') == len(cites), 'MALFORMED_CITATION:' + slug)
            cited_total += len(cites)
            for sid, count in sorted(Counter(cites).items()):
                exposure[sid][label][slug] = count
                if sid not in source_index:
                    blocked.append({'code':'CITED_SOURCE_NOT_REGISTERED','version':label,
                                    'article':slug,'source_id':sid})
                else:
                    if not any(v['verified_on'] for v in source_index[sid]):
                        blocked.append({'code':'CITED_SOURCE_HAS_NO_VERIFIED_VARIANT',
                                        'version':label,'article':slug,'source_id':sid})
                explanation = use.get(sid)
                if type(explanation) is not str or not explanation.strip():
                    blocked.append({'code':'CITED_SOURCE_MISSING_ARTICLE_USE','version':label,
                                    'article':slug,'source_id':sid})
        citation_totals[label] = cited_total

    for slug in slugs:
        old = strict_json(get(bfiles[slug+'.meta.json']))
        new = strict_json(get(afiles[slug+'.meta.json']))
        if old['safety_review'].get('state') != new['safety_review'].get('state'):
            blocked.append({'code':'SAFETY_STATE_DRIFT','article':slug})
        o_use, n_use = old['source_use'], new['source_use']
        for sid in sorted(set(o_use) & set(n_use)):
            if o_use[sid] != n_use[sid]:
                review_rows.append({'code':'AUTHOR_READING_SCOPE_CHANGED','article':slug,
                                    'source_id':sid,'state':'UNREVIEWED'})

    for sid in sorted(exposure):
        old = exposure[sid]['original']
        new = exposure[sid]['candidate']
        if old != new:
            review_rows.append({'code':'CITATION_EXPOSURE_CHANGED', 'source_id':sid,
                                'before':dict(sorted(old.items())),
                                'after':dict(sorted(new.items())), 'state':'UNREVIEWED'})

    declared = {}
    for group in crosswalk['groups']:
        need(type(group) is dict and type(group.get('url')) is str, 'BAD_CROSSWALK_GROUP')
        key = canonical_url(group['url'])
        need(key not in declared, 'DUPLICATE_CROSSWALK_GROUP')
        need(group.get('review_status') == 'pending-human-source-and-reading-scope-review',
             'ILLEGAL_CROSSWALK_APPROVAL')
        declared[key] = group
    actual = {url for url, rows in per_version['candidate']['by_url'].items() if len(rows) > 1}
    for url in sorted(actual - set(declared)):
        blocked.append({'code':'UNRECORDED_SHARED_SOURCE_URL','canonical_url':url})
    for url in sorted(set(declared) - actual):
        review_rows.append({'code':'CROSSWALK_URL_NO_LONGER_SHARED','canonical_url':url,
                            'state':'UNREVIEWED'})
    for url in sorted(actual & set(declared)):
        observed = sorted((r['origin'],r['id']) for r in per_version['candidate']['by_url'][url])
        expected = sorted((v.get('origin'),v.get('source',{}).get('id'))
                          for v in declared[url].get('variants',[]))
        if observed != expected:
            blocked.append({'code':'CROSSWALK_VARIANT_ROSTER_DRIFT', 'canonical_url':url,
                            'observed':observed,'declared':expected})

    return {'state':'HOLD', 'issue':136, 'business_issue':820,
            'may_publish':False,'may_merge':False,'QD_PASS':False,
            'medical_safety_verified':False,'merchant_offer_verified':False,
            'article_count':len(slugs),'contributor_count':len(contributors),
            'blobs_read':len(seen_blobs),'candidate_source_rows':len(per_version['candidate']['sources']),
            'candidate_shared_url_groups':len(actual),'declared_shared_url_groups':len(declared),
            'citation_counts':citation_totals,'source_ids_cited':len(exposure),
            'blockers':sorted(blocked,key=lambda x:json.dumps(x,sort_keys=True)),
            'human_review_worklist':sorted(review_rows,key=lambda x:json.dumps(x,sort_keys=True)),
            'warning':'Structural custody only. All shared-source variants require human evidence, claim and safety review. No release authority.'}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--snapshots', type=Path, required=True)
    p.add_argument('--register-oid', required=True)
    p.add_argument('--crosswalk', type=Path, required=True)
    args = p.parse_args(argv)
    try:
        snap = strict_json(args.snapshots.read_text(encoding='utf-8'))
        crosswalk = strict_json(args.crosswalk.read_text(encoding='utf-8'))
        result = audit(snap, args.register_oid, crosswalk, git_reader(args.repo))
        print(json.dumps(result,sort_keys=True,indent=2))
        return 2 if result['blockers'] else 0
    except (Hold, ValueError, OSError, subprocess.SubprocessError) as err:
        print('HOLD: '+str(err),file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
