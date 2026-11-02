#!/usr/bin/env python3
"""R60 PRIVATE HOLD: examine moved contributor Git objects; never rebaseline R14.

A deterministic discrepancy dossier, NOT source verification or approval.
Read-only; no network, WordPress/CMS/navigation or public output writes.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'r60-frozen-seven-cluster-drift-review-v1'
R14_BLOB = '83263d772fe19fb04d21387a8d051797cc6493c0'
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json'
SHA = re.compile(r'[0-9a-f]{40}\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
MAX_FILE = 2_000_000
MAX_CHANGED = 200


class DriftHold(ValueError):
    """Cannot safely substantiate a contributor drift report."""


def need(test, message):
    if not test:
        raise DriftHold(message)


def valid_path(path):
    return (isinstance(path, str) and path.startswith('preparedness/')
            and '\\' not in path and '\x00' not in path
            and all(p not in ('', '.', '..') for p in path.split('/'))
            and len(path) <= 320)


def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def source_ids(data):
    obj = json.loads(data.decode('utf-8'))
    need(type(obj) is dict and type(obj.get('sources')) is list,
         'invalid contributor source fragment')
    out = {}
    for row in obj['sources']:
        need(type(row) is dict and type(row.get('id')) is str
             and row['id'] not in out, 'invalid or repeated source ID')
        out[row['id']] = row
    return out


def differences(old, new, path):
    """High-signal structured clues; never assert evidence/claim correctness."""
    clues = {}
    if path.endswith('.body.html'):
        a = Counter(CITE.findall(old.decode('utf-8')))
        b = Counter(CITE.findall(new.decode('utf-8')))
        clues['citation_added_occurrences'] = dict(sorted((b-a).items()))
        clues['citation_removed_occurrences'] = dict(sorted((a-b).items()))
        clues['citation_total_before'] = sum(a.values())
        clues['citation_total_after'] = sum(b.values())
    if path.endswith('.meta.json'):
        a, b = json.loads(old.decode('utf-8')), json.loads(new.decode('utf-8'))
        need(type(a) is dict and type(b) is dict, 'non-object article metadata')
        au, bu = a.get('source_use', {}), b.get('source_use', {})
        need(type(au) is dict and type(bu) is dict, 'invalid source-use mapping')
        clues['source_use_added'] = sorted(bu.keys()-au.keys())
        clues['source_use_removed'] = sorted(au.keys()-bu.keys())
        clues['source_use_modified'] = sorted(k for k in au.keys() & bu.keys() if au[k] != bu[k])
        clues['safety_review_changed'] = a.get('safety_review') != b.get('safety_review')
        clues['publication_status_changed'] = a.get('status') != b.get('status')
        clues['article_slug_changed'] = a.get('slug') != b.get('slug')
        clues['other_metadata_changed'] = [k for k in sorted(a.keys() | b.keys())
                                           if a.get(k) != b.get(k) and k not in
                                           ('source_use', 'safety_review', 'status')]
    if re.fullmatch(r'preparedness/sources/fragments/[a-z-]+\.json', path):
        a, b = source_ids(old), source_ids(new)
        clues['source_ids_added'] = sorted(b.keys()-a.keys())
        clues['source_ids_removed'] = sorted(a.keys()-b.keys())
        clues['source_ids_modified'] = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        clues['human_link_checks_before'] = sum(x.get('human_link_check') is True for x in a.values())
        clues['human_link_checks_after'] = sum(x.get('human_link_check') is True for x in b.values())
    return clues


def report(manifest, observed_heads, changed_paths, lookup_blob, read_blob,
           frozen_check, branches):
    """Pure injection-friendly scanner; frozen_check MUST run R15 on real Git objects.

    `changed_paths` and Git object readers are independent witnesses; a missing
    diff entry for a changed frozen path fails closed. No refs are updated.
    """
    frozen_check(manifest)
    need(type(manifest) is dict and manifest.get('release_state') == 'HOLD'
         and manifest.get('may_publish') is False and
         manifest.get('independent_human_source_checks_verified') == 0,
         'frozen manifest attempts release or source approval')
    records = manifest.get('branches')
    need(type(records) is list and set(branches) == {r.get('name') for r in records}
         and len(records) == len(branches) == 7,
         'not the original seven contributor clusters')
    need(type(observed_heads) is dict and set(observed_heads) == set(branches),
         'missing or extra observed contributor head')
    rows, moved, count = [], [], 0
    for entry in sorted(records, key=lambda x: x['name']):
        group, frozen = entry['name'], entry['contributor_commit_sha']
        live = observed_heads[group]
        need(all(type(x) is str and SHA.fullmatch(x) for x in (frozen, live)),
             group + ': invalid exact commit SHA')
        scope = {x['path']: x['contributor_blob_sha'] for x in entry['files']}
        need(len(scope) == len(entry['files']), group + ': repeated frozen evidence path')
        paths = changed_paths(frozen, live) if frozen != live else []
        need(type(paths) is list and len(paths) <= MAX_CHANGED and
             len(set(paths)) == len(paths) and all(valid_path(p) for p in paths),
             group + ': invalid or out-of-scope changed-path list')
        paths = sorted(paths)
        # An independent per-path tree lookup prevents incomplete/dropped diffs.
        for path, oid in scope.items():
            need(lookup_blob(frozen, path) == oid,
                 group + ': original frozen Git blob changed or disappeared: ' + path)
            current_oid = lookup_blob(live, path)
            need((current_oid != oid) == (path in paths),
                 group + ': changed frozen path omitted or falsely claimed: ' + path)
        if live != frozen:
            moved.append({'cluster': group, 'frozen_commit_sha': frozen,
                          'observed_commit_sha': live})
        for path in paths:
            old_id, new_id = lookup_blob(frozen, path), lookup_blob(live, path)
            need(old_id != new_id and (old_id is None or SHA.fullmatch(old_id))
                 and (new_id is None or SHA.fullmatch(new_id)),
                 'changed path lacks valid distinct Git blob identities: ' + path)
            original = read_blob(frozen, path) if old_id else b''
            current = read_blob(live, path) if new_id else b''
            need(type(original) is bytes and type(current) is bytes and
                 len(original) <= MAX_FILE and len(current) <= MAX_FILE and
                 (old_id is None or blob_sha(original) == old_id) and
                 (new_id is None or blob_sha(current) == new_id),
                 'actual Git blob bytes do not substantiate recorded identity: ' + path)
            normalized_equal = (old_id is not None and new_id is not None and
                                original.replace(b'\r\n', b'\n') ==
                                current.replace(b'\r\n', b'\n'))
            label = ('ADDED' if old_id is None else 'DELETED' if new_id is None
                     else 'LINE_ENDINGS_ONLY' if normalized_equal
                     else 'CONTENT_OR_SOURCE_ID_CHANGE')
            clues = differences(original, current, path) if old_id and new_id and not normalized_equal else {}
            rows.append({'cluster': group, 'path': path,
                         'in_frozen_72_path_scope': path in scope,
                         'frozen_blob_sha': old_id, 'observed_blob_sha': new_id,
                         'frozen_sha256': sha256(original) if old_id else None,
                         'observed_sha256': sha256(current) if new_id else None,
                         'normalized_line_endings_equivalent': normalized_equal,
                         'classification_NOT_APPROVAL': label,
                         'source_and_citation_change_clues_NOT_VERIFIED': clues,
                         'human_provenance_review_state': 'NOT_REVIEWED'})
            count += 1
    result = {
        'schema': SCHEMA, 'issue': 136, 'frozen_manifest_blob_sha': R14_BLOB,
        'release_state': 'HOLD', 'machine_only': True,
        'checked_clusters': 7, 'moved_contributor_heads': moved,
        'changed_file_count': count, 'changed_files': rows,
        'existing_R14_exception_remains_open': True,
        'human_source_links_verified': False,
        'qualified_safety_clearance': False,
        'independent_QD_approval': False, 'may_publish': False,
        'limitations': ('Git-object and source-ID change triage only. Remote-tracking refs '
                        'represent the checkout fetch, not proof of remote freshness. '
                        'No source link, evidence assertion, hazard/medical advice, '
                        'QD approval or article is cleared for publication.')}
    result['fingerprint_sha256'] = sha256(canonical(result))
    return result


def verify_report(original, *args, **kwargs):
    need(type(original) is dict and original == report(*args, **kwargs),
         'drift review dossier differs from independently regenerated evidence')
    return True


def git(root, *args, limit=MAX_FILE + 1000):
    try:
        p = subprocess.run(['git', '-C', str(root), *args], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise DriftHold('read-only Git operation unavailable') from e
    need(p.returncode == 0 and len(p.stdout) <= limit,
         'Git object/ref unavailable, oversized, or not safely readable')
    return p.stdout


def git_blob(root, sha, path):
    need(type(sha) is str and SHA.fullmatch(sha) and valid_path(path),
         'untrusted Git object reference or path')
    raw = git(root, 'ls-tree', '-z', sha, '--', path, limit=800)
    if not raw:
        return None
    need(raw.count(b'\x00') == 1, 'ambiguous Git tree entry')
    prefix, found = raw.rstrip(b'\x00').split(b'\t', 1)
    mode, typ, oid = prefix.decode('ascii').split(' ')
    need(found.decode('utf-8') == path and mode == '100644' and
         typ == 'blob' and SHA.fullmatch(oid), 'nonregular/malformed Git blob')
    return oid


def git_read(root, sha, path):
    need(SHA.fullmatch(sha) and valid_path(path), 'invalid Git blob request')
    return git(root, 'show', sha + ':' + path)


def git_changed(root, old, new):
    need(SHA.fullmatch(old) and SHA.fullmatch(new), 'invalid comparison commit')
    raw = git(root, 'diff', '--name-only', '-z', '--no-renames', old, new,
              '--', 'preparedness/', limit=80_000)
    names = [p.decode('utf-8') for p in raw.split(b'\0') if p]
    need(len(names) <= MAX_CHANGED and len(names) == len(set(names)),
         'ambiguous or oversized contributor changed-file inventory')
    return names


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', type=Path, default=ROOT.parent)
    p.add_argument('--remote', default='origin')
    p.add_argument('--summary', action='store_true')
    args = p.parse_args(argv)
    root = args.repo_root.resolve()
    need(re.fullmatch('[A-Za-z0-9_-]+', args.remote), 'invalid remote name')
    need(MANIFEST.is_file() and not MANIFEST.is_symlink(), 'frozen manifest unavailable')
    raw = MANIFEST.read_bytes()
    need(blob_sha(raw) == R14_BLOB, 'R14 frozen manifest Git blob has changed')
    manifest = json.loads(raw.decode('utf-8'))
    spec = importlib.util.spec_from_file_location('r60_original_r15',
                                                 ROOT / 'tools/cluster_git_parity_gate.py')
    need(spec and spec.loader, 'R15 independent frozen parity checker unavailable')
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    def frozen_check(doc):
        known = {gate.BRANCHES[e['name']]: e['contributor_commit_sha'] for e in doc['branches']}
        gate.check_manifest(doc, lambda sha, path: gate.git_blob(root, sha, path),
                            lambda branch: known.get(branch), integrated_head=gate.R14_SHA)
    heads = {name: git(root, 'rev-parse', '--verify',
                       f'refs/remotes/{args.remote}/{branch}^{{commit}}', limit=200)
             .decode('ascii').strip()
             for name, branch in gate.BRANCHES.items()}
    output = report(manifest, heads, lambda a, b: git_changed(root, a, b),
                    lambda sha, path: git_blob(root, sha, path),
                    lambda sha, path: git_read(root, sha, path),
                    frozen_check, gate.BRANCHES)
    if args.summary:
        print(json.dumps({k: output[k] for k in ('release_state', 'checked_clusters',
              'moved_contributor_heads', 'changed_file_count', 'fingerprint_sha256')},
              indent=2))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    return 0  # a successful *dossier* does not mean the R15 publish gate passes


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (DriftHold, ValueError, KeyError, UnicodeError) as e:
        print('R60 EVIDENCE HOLD: ' + str(e))
        raise SystemExit(2)
