#!/usr/bin/env python3
"""R61 PRIVATE HOLD: unreviewed two-version contributor citation/source lineage.

R60 verifies Git provenance; this module preserves old/new reading depth and
citation positions for human adjudication, never edits or rebaselines evidence.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'r61-private-contributor-two-version-lineage-v1'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SHA = re.compile(r'[0-9a-f]{64}\Z')
HOLD_FIELDS = ('may_publish', 'independent_QD_approval', 'qualified_safety_clearance',
               'human_source_links_verified')
MAX_BYTES = 2_000_000

class LineageHold(ValueError):
    """Original or newly observed evidence cannot be reconciled safely."""

def need(value, reason):
    if not value:
        raise LineageHold(reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def module(name):
    path = Path(__file__).with_name(name)
    need(path.is_file() and not path.is_symlink(), 'required frozen gate missing: ' + name)
    spec = importlib.util.spec_from_file_location('r61_dependency_' + name.replace('.', '_'), path)
    need(spec and spec.loader, 'invalid gate module')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def strict_json(data):
    def pairs(items):
        result = {}
        for key, val in items:
            need(key not in result, 'duplicate key in source/metadata JSON')
            result[key] = val
        return result
    def reject_constant(x):
        raise LineageHold('nonstandard JSON number: ' + x)
    return json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=reject_constant)

def tokens(html):
    need(type(html) is str, 'citation body not UTF-8 text')
    hits = list(CITE.finditer(html))
    need(html.count('{{cite:') == len(hits), 'malformed citation token')
    return [{'source_id': m.group(1), 'offset_codepoints': m.start(),
             'unabridged_local_context': html[max(0, m.start()-180):min(len(html),m.end()+240)]}
            for m in hits]

def source_rows(fragment, cluster):
    need(type(fragment) is dict and type(fragment.get('sources')) is list,
         cluster + ': missing original source inventory')
    seen = set()
    rows = []
    for row in fragment['sources']:
        need(type(row) is dict and type(row.get('id')) is str and row['id'] and
             row['id'] not in seen, cluster + ': missing or repeated source ID')
        seen.add(row['id'])
        rows.append(row)
    return rows

def prepare(manifest, drift, lookup, read, *, expected=(7, 29, 72)):
    """R60 report MUST have been regenerated from exact Git objects first.

    Source records and article versions are never merged or promoted. The
    current branch version is an unreviewed proposal, not an integrated edit.
    """
    gate = module('r60_contributor_provenance_drift_docket.py')
    need(type(expected) is tuple and expected == (7,29,72), 'frozen census required')
    need(type(manifest) is dict and type(drift) is dict and
         drift.get('schema') == gate.SCHEMA and drift.get('release_state') == 'HOLD' and
         drift.get('machine_only') is True and
         all(drift.get(k) is False for k in HOLD_FIELDS) and
         drift.get('existing_R14_exception_remains_open') is True and
         drift.get('frozen_manifest_blob_sha') == gate.R14_BLOB and
         drift.get('fingerprint_sha256') == digest({k:v for k,v in drift.items()
                                                   if k != 'fingerprint_sha256'}),
         'untrusted or falsely approved R60 input')
    entries = manifest.get('branches')
    need(type(entries) is list and len(entries) == expected[0] and
         sum(len(e['files']) for e in entries) == expected[2],
         'seven frozen contributors or 72 original evidence files missing')
    observed = {e['name']: e['contributor_commit_sha'] for e in entries}
    need(len(observed) == expected[0], 'duplicate frozen cluster')
    for moved in drift.get('moved_contributor_heads', []):
        name = moved.get('cluster')
        need(name in observed and moved.get('frozen_commit_sha') == observed[name] and
             moved.get('observed_commit_sha') != observed[name],
             'untrusted moved contributor identity')
        observed[name] = moved['observed_commit_sha']
    changes = drift.get('changed_files')
    need(type(changes) is list and drift.get('changed_file_count') == len(changes),
         'incomplete contributor Git file delta')
    changed = {}
    for row in changes:
        key = (row['cluster'], row['path'])
        need(key not in changed and row['cluster'] in observed and
             row.get('human_provenance_review_state') == 'NOT_REVIEWED' and
             row.get('classification_NOT_APPROVAL') in (
                 'ADDED','DELETED','LINE_ENDINGS_ONLY','CONTENT_OR_SOURCE_ID_CHANGE'),
             'duplicate changed path or claimed review')
        changed[key] = row

    def load(cluster, frozen_sha, live_sha, frozen_blobs, path, version):
        commit = frozen_sha if version == 'frozen' else live_sha
        row = changed.get((cluster,path))
        original_oid = frozen_blobs.get(path)
        need(original_oid is not None, 'untracked frozen evidence path')
        oid = original_oid if version == 'frozen' else (row['observed_blob_sha'] if row else original_oid)
        need(type(oid) is str and re.fullmatch(r'[a-f0-9]{40}',oid),
             'deleted/nonregular frozen evidence cannot be silently used: ' + path)
        need(lookup(commit,path) == oid, 'Git object does not match R60 custody: ' + path)
        raw = read(commit,path)
        need(type(raw) is bytes and len(raw) <= MAX_BYTES and gate.blob_sha(raw) == oid,
             'untrusted Git file bytes: ' + path)
        if row:
            name = 'frozen' if version == 'frozen' else 'observed'
            need(row[name+'_blob_sha'] == oid and row[name+'_sha256'] == sha256(raw),
                 'R60 old/new file bytes disagree: ' + path)
        return raw, oid

    registry = {'frozen': defaultdict(list), 'observed': defaultdict(list)}
    inventories, articles = [], []
    for entry in sorted(entries, key=lambda e:e['name']):
        group, old = entry['name'], entry['contributor_commit_sha']
        new = observed[group]
        originals = {v['path']:v['contributor_blob_sha'] for v in entry['files']}
        need(len(originals) == len(entry['files']), 'duplicate frozen path')
        fragment = f'preparedness/sources/fragments/{group}.json'
        pairs = {}
        for v, commit in (('frozen',old),('observed',new)):
            raw, oid = load(group,old,new,originals,fragment,v)
            sources = source_rows(strict_json(raw),group)
            pairs[v] = {'blob_sha':oid,'sha256':sha256(raw),'sources':sources}
            for source in sources:
                registry[v][source['id']].append({'cluster':group,
                    'source_record_sha256':digest(source)})
        before = {x['id']:x for x in pairs['frozen']['sources']}
        after = {x['id']:x for x in pairs['observed']['sources']}
        inventories.append({'cluster':group, 'frozen_commit':old,
            'observed_commit':new, 'frozen_fragment_sha256':pairs['frozen']['sha256'],
            'observed_fragment_sha256':pairs['observed']['sha256'],
            'original_source_record_count':len(before),
            'observed_source_record_count':len(after),
            'added_source_ids_NOT_APPROVED':sorted(after.keys()-before.keys()),
            'removed_source_ids_NOT_ALIASED':sorted(before.keys()-after.keys()),
            'modified_same_id_source_records_NOT_APPROVED':sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
            'all_original_reading_records_UNABRIDGED':pairs['frozen']['sources'],
            'all_observed_reading_records_UNABRIDGED_UNVERIFIED':pairs['observed']['sources'],
            'review_state':'NOT_REVIEWED'})
        body_paths = sorted(p for p in originals if p.endswith('.body.html'))
        for path in body_paths:
            slug = path.split('/')[-1].removesuffix('.body.html')
            metadata = path.removesuffix('.body.html') + '.meta.json'
            versions = {}
            for version in ('frozen','observed'):
                raw, oid = load(group,old,new,originals,path,version)
                meta, moid = load(group,old,new,originals,metadata,version)
                obj = strict_json(meta)
                need(type(obj) is dict and obj.get('slug') == slug and
                     type(obj.get('source_use')) is dict,
                     'article metadata/source-use malformed: ' + slug)
                html = raw.decode('utf-8')
                citations = tokens(html)
                versions[version] = {'body_git_blob_sha':oid,'body_sha256':sha256(raw),
                    'metadata_git_blob_sha':moid,'metadata_sha256':sha256(meta),
                    'status_as_recorded_NOT_REVIEWED':obj.get('status'),
                    'safety_review_as_recorded_NOT_CLEARED':obj.get('safety_review'),
                    'full_source_use_mapping_UNABRIDGED':obj['source_use'],
                    'citation_occurrences_in_original_order':citations,
                    'full_article_html_WHEN_MODIFIED':None}
                # Retain both complete versions for changed bodies; no lost depth.
                if (group,path) in changed:
                    versions[version]['full_article_html_WHEN_MODIFIED'] = html
            old_tokens = versions['frozen']['citation_occurrences_in_original_order']
            new_tokens = versions['observed']['citation_occurrences_in_original_order']
            changed_body = versions['frozen']['body_git_blob_sha'] != versions['observed']['body_git_blob_sha']
            changed_meta = versions['frozen']['metadata_git_blob_sha'] != versions['observed']['metadata_git_blob_sha']
            articles.append({'cluster':group,'slug':slug,
                'changed_body_requires_claim_context_review':changed_body,
                'changed_metadata_requires_provenance_review':changed_meta,
                'citation_tokens_before':len(old_tokens),'citation_tokens_after':len(new_tokens),
                'original_citation_id_counts':dict(sorted(Counter(t['source_id'] for t in old_tokens).items())),
                'observed_citation_id_counts_UNVERIFIED':dict(sorted(Counter(t['source_id'] for t in new_tokens).items())),
                'citation_sequence_exactly_equal_NOT_CLAIM_APPROVAL':
                    [t['source_id'] for t in old_tokens] == [t['source_id'] for t in new_tokens],
                'versions':versions,'review_state':'NOT_REVIEWED'})
    need(len(articles) == expected[1] and len(inventories) == expected[0],
         '29 contributor articles or seven source fragments lost')
    for row in articles:
        for version in ('frozen','observed'):
            for citation in row['versions'][version]['citation_occurrences_in_original_order']:
                sid = citation['source_id']
                candidates = registry[version].get(sid,[])
                citation['candidate_contributor_readings_NOT_CLAIM_SUPPORT'] = list(candidates)
                citation['outside_seven_clusters_must_check_full_R58'] = not bool(candidates)
                citation['human_claim_support_state'] = 'NOT_REVIEWED'
    result = {'schema':SCHEMA,'issue':136,'release_state':'HOLD','machine_only':True,
        'frozen_manifest_blob_sha':gate.R14_BLOB,
        'parent_R60_fingerprint_sha256':drift['fingerprint_sha256'],
        'counts':{'clusters':len(inventories),'original_contributor_articles':len(articles),
            'frozen_evidence_paths':sum(len(e['files']) for e in entries),
            'contributor_heads_moved':len(drift['moved_contributor_heads']),
            'changed_preparedness_files':len(changes),
            'articles_with_body_changes':sum(x['changed_body_requires_claim_context_review'] for x in articles),
            'articles_with_metadata_changes':sum(x['changed_metadata_requires_provenance_review'] for x in articles),
            'old_citation_occurrences':sum(x['citation_tokens_before'] for x in articles),
            'observed_citation_occurrences_UNVERIFIED':sum(x['citation_tokens_after'] for x in articles)},
        'source_inventories_BOTH_VERSIONS_UNREVIEWED':inventories,
        'per_article_citation_and_context_lineage_NOT_REVIEWED':articles,
        'unreviewed_git_file_change_docket':changes,
        'other_six_integrated_articles_OUTSIDE_R14_SCOPE':6,
        'complete_35_article_1959_occurrence_R58_custody_unchanged_NOT_REVALIDATED_HERE':True,
        'existing_R14_exception_remains_open':True,
        'limitations':('Git custody and old/new reading depth are preserved, not corroborated. '
            'The R58 complete 35-article citation census and water tool remain separately gated. '
            'Shared source IDs or repeated URLs are never merged or silently aliased. '
            'Neither historical research nor modern emergency/medical guidance is cleared.'),
        **{k:False for k in HOLD_FIELDS}}
    result['fingerprint_sha256'] = digest(result)
    return result

def verify(original, *args, **kwargs):
    need(type(original) is dict and original == prepare(*args, **kwargs),
         'two-version lineage differs from independently regenerated evidence')
    return True

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=ROOT.parent)
    p.add_argument('--remote',default='origin')
    p.add_argument('--summary',action='store_true')
    opts = p.parse_args(argv)
    gate = module('r60_contributor_provenance_drift_docket.py')
    root = opts.repo_root.resolve()
    need(re.fullmatch('[A-Za-z0-9_-]+',opts.remote), 'untrusted remote')
    raw = gate.MANIFEST.read_bytes()
    need(gate.blob_sha(raw) == gate.R14_BLOB,'frozen R14 evidence changed')
    manifest = strict_json(raw)
    original = module('cluster_git_parity_gate.py')
    def frozen_check(doc):
        frozen = {original.BRANCHES[e['name']]:e['contributor_commit_sha'] for e in doc['branches']}
        original.check_manifest(doc,lambda sha,path:original.git_blob(root,sha,path),
                                lambda branch:frozen.get(branch),integrated_head=original.R14_SHA)
    heads = {group:gate.git(root,'rev-parse','--verify',
                    f'refs/remotes/{opts.remote}/{branch}^{{commit}}',limit=200).decode().strip()
             for group,branch in original.BRANCHES.items()}
    drift = gate.report(manifest,heads,lambda a,b:gate.git_changed(root,a,b),
                        lambda sha,path:gate.git_blob(root,sha,path),
                        lambda sha,path:gate.git_read(root,sha,path),frozen_check,
                        original.BRANCHES)
    result = prepare(manifest,drift,lambda sha,path:gate.git_blob(root,sha,path),
                     lambda sha,path:gate.git_read(root,sha,path))
    output = ({'schema':SCHEMA,'release_state':'HOLD','may_publish':False,
               'counts':result['counts'],'fingerprint_sha256':result['fingerprint_sha256']}
              if opts.summary else result)
    print(json.dumps(output,sort_keys=True,ensure_ascii=False,indent=2))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (LineageHold,ValueError,KeyError,TypeError,UnicodeError,OSError) as exc:
        print('R61 PRIVATE EVIDENCE HOLD: '+str(exc))
        raise SystemExit(2)
