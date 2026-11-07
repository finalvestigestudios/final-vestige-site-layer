#!/usr/bin/env python3
"""Offline proof that frozen Preparedness blobs occur at their claimed branch paths.

Structural custody only: never a source, medical, QD, commercial or publish PASS.
No repository files are changed. Requires a trusted checkout with all seven
Claude commit objects, or an explicitly injected synthetic branch-tree fixture.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1'
REPORT_SCHEMA = 'fv-preparedness-r201-branch-path-witness-custody-v1'
MANIFEST_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
HEADS = {
    'start': '2122d856fce9f64887c16df3d52e64be9f59a55b',
    'shelter': '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
    'food': 'f911ff7a655de8d81535ea86ec3d65a49ee76648',
    'health': 'd5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
    'hist-field': '4e5caf812727953aa45e3bda2d382f2c67b6a09c',
    'hist-food': '67e116e536c7410bed30f8f3b1bb8c166f3c223d',
    'hist-home': '7504a5f099594d635e3dd7332a33a2e1346c43a2',
}
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
ARTICLE_DIR = 'preparedness/content/articles/'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
OID = re.compile(r'[0-9a-f]{40}\Z')

class CustodyError(ValueError):
    pass

def demand(condition, message):
    if not condition:
        raise CustodyError(message)

def blob_oid(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def strict_json(data):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            demand(key not in out, 'duplicate JSON key: ' + key)
            out[key] = value
        return out
    def no_constant(value):
        raise CustodyError('non-JSON constant: ' + value)
    return json.loads(data.decode('utf-8'), object_pairs_hook=unique, parse_constant=no_constant)

def branch_tree(repo, sha):
    """Get Git-owned mode/type/OID for all article paths at an exact commit."""
    demand(bool(OID.fullmatch(sha)), 'unsafe branch SHA')
    proc = subprocess.run(['git', 'ls-tree', '-r', '-z', sha, '--', ARTICLE_DIR],
                          cwd=repo, check=True, timeout=30,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    entries = {}
    for record in proc.stdout.split(b'\0'):
        if not record:
            continue
        head, sep, name = record.partition(b'\t')
        demand(bool(sep), 'malformed git tree entry')
        fields = head.decode('ascii').split(' ')
        demand(len(fields) == 3, 'malformed git mode/type/OID')
        mode, kind, oid = fields
        path = name.decode('utf-8')
        demand(path not in entries, 'duplicate git tree path')
        entries[path] = (mode, kind, oid)
    return entries

def check(manifest, trees, *, strict=True):
    """Verify every declared owner and inherited witness against actual path OIDs."""
    report = {'schema': REPORT_SCHEMA, 'issue': 136, 'conversion_issue': 820,
              'state': INVALID, 'publication_authorized': False,
              'independent_qd_pass': False, 'human_source_approved': False,
              'medical_safety_verified': False, 'merchant_offer_verified': False,
              'verified_paid_orders': None, 'realized_net_revenue': None,
              'summary': {}, 'evidence': [], 'errors': []}
    try:
        demand(type(manifest) is dict and manifest.get('schema') == SCHEMA,
               'wrong R200 manifest schema')
        demand(manifest.get('issue') == 136 and manifest.get('conversion_issue') == 820,
               'issue governance drift')
        demand(manifest.get('state') == HOLD, 'non-hold manifest state')
        for name in ('publication_authorized','independent_qd_pass',
                     'human_source_approved','medical_safety_verified',
                     'merchant_offer_verified'):
            demand(manifest.get(name) is False, 'unsupported approval: ' + name)
        demand(manifest.get('verified_paid_orders') is None and
               manifest.get('realized_net_revenue') is None, 'unsupported revenue claim')
        demand(manifest.get('branch_heads') == HEADS, 'branch head identity drift')
        demand(type(trees) is dict and set(trees) == set(HEADS),
               'missing or unexpected branch tree')
        rows = manifest.get('articles')
        demand(type(rows) is list and (len(rows) == 35 if strict else len(rows) > 0),
               'missing full 35-article roster')
        demand(manifest.get('artifact_count') == len(rows) and
               manifest.get('export_target_count_with_six_tools') == len(rows) + 6,
               'article/tool target census mismatch')
        slugs = set(); routes = set(); n_paths = 0; inherited = 0
        for n, row in enumerate(rows, 1):
            demand(type(row) is dict and row.get('n') == n,
                   'misordered source roster')
            slug = row.get('slug')
            demand(type(slug) is str and bool(SLUG.fullmatch(slug)) and slug not in slugs,
                   'unsafe or duplicate article slug')
            slugs.add(slug)
            route = row.get('route')
            section = row.get('section')
            demand(type(section) is str and bool(SLUG.fullmatch(section)) and
                   route == f'/preparedness/{section}/{slug}/' and route not in routes,
                   'duplicate or altered canonical route: ' + slug)
            routes.add(route)
            owner = row.get('source_cluster')
            witnesses = row.get('also_in')
            demand(owner in HEADS and row.get('branch_sha') == HEADS[owner] and
                   type(witnesses) is list and bool(witnesses) and witnesses[0] == owner and
                   len(witnesses) == len(set(witnesses)) and set(witnesses) <= set(HEADS),
                   'invalid cluster owner/witness list: ' + slug)
            demand(all(type(k) is str and bool(OID.fullmatch(row.get(k,'')))
                       for k in ('body_oid','meta_oid')),
                   'invalid frozen blob identity: ' + slug)
            for key in witnesses:
                if key != owner:
                    inherited += 1
                for suffix, field in (('body.html','body_oid'),('meta.json','meta_oid')):
                    path = ARTICLE_DIR + slug + '.' + suffix
                    entry = trees[key].get(path)
                    demand(type(entry) is tuple and len(entry) == 3,
                           'missing path witness: ' + key + '/' + path)
                    mode, kind, actual = entry
                    demand(mode == '100644' and kind == 'blob' and actual == row[field],
                           'branch path/OID/type mismatch: ' + key + '/' + path)
                    n_paths += 1
                report['evidence'].append({'article': slug, 'branch': key,
                    'commit': HEADS[key], 'body_oid': row['body_oid'],
                    'meta_oid': row['meta_oid'], 'relationship':
                        'owner' if key == owner else 'inherited-identical',
                    'state': 'FROZEN_PATH_MATCH_NOT_SAFETY_APPROVAL'})
        if strict:
            demand(len(rows) == 35 and n_paths == 142 and inherited == 36,
                   'frozen 35-article/71-witness census drift')
        report['summary'] = {'articles': len(rows), 'unique_routes': len(routes),
                             'branch_heads': len(HEADS), 'article_branch_witnesses':
                             len(report['evidence']), 'inherited_witnesses': inherited,
                             'verified_git_paths': n_paths}
        report['state'] = HOLD
    except (CustodyError, KeyError, TypeError, UnicodeError, AttributeError) as exc:
        report['evidence'] = []
        report['errors'] = [str(exc)[:360]]
    return report

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default='.')
    ap.add_argument('--report')
    opts = ap.parse_args(argv)
    root = Path(opts.repo).resolve()
    try:
        raw = (root / 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json').read_bytes()
        demand(blob_oid(raw) == MANIFEST_OID, 'R200 independent manifest Git identity changed')
        manifest = strict_json(raw)
        trees = {name: branch_tree(root, sha) for name, sha in HEADS.items()}
        result = check(manifest, trees)
    except (CustodyError, OSError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired, ValueError) as exc:
        result = {'schema': REPORT_SCHEMA, 'state': INVALID,
                  'publication_authorized': False, 'independent_qd_pass': False,
                  'errors': [str(exc)[:360]]}
    payload = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + '\n'
    if opts.report:
        Path(opts.report).write_text(payload, encoding='utf-8')
    else:
        print(payload, end='')
    return 2 if result['state'] == HOLD else 3

if __name__ == '__main__':
    raise SystemExit(main())
