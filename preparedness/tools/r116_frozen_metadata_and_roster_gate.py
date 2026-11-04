#!/usr/bin/env python3
"""R116. Freeze original Preparedness metadata bytes and article-file roster.

The 35 contributor-authored article bodies are separately pinned by R115. This
additional immutable inventory rejects changes to citation reading scopes,
warning/review text, per-article safety state, and accidental extra source files.
Comparing Git blob identity is *not* a factual, safety, merchant or QD approval.
Read-only; fail closed; no CMS/network operations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r116-exact-metadata-blob-and-roster-HOLD-v1'
R115_SCHEMA = 'fv-preparedness-r115-35-article-frozen-read-census-NOT-SAFETY-v1'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
BLOB = re.compile(r'[0-9a-f]{40}\Z')
CITE = re.compile(rb'\{\{cite:([a-z0-9-]+)\}\}')

class IntegrityHold(ValueError):
    pass

def require(test, code):
    if not test:
        raise IntegrityHold(code)

def git_blob(data):
    require(type(data) is bytes, 'INPUT_NOT_BYTES')
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def strict_json(raw):
    def no_duplicates(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise IntegrityHold('DUPLICATE_JSON_KEY')
            out[k] = v
        return out
    try:
        return json.loads(raw, object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrityHold('INVALID_METADATA_JSON') from exc

def audit(manifest, r115, metadata, body_names):
    """Pure structural check. metadata maps slug -> raw JSON bytes.

    body_names is the complete set of existing *.body.html stems in the directory.
    Caller checks symlinks and obtains both inventories from filesystem.
    """
    require(type(manifest) is dict and manifest.get('schema') == SCHEMA,
            'UNKNOWN_FROZEN_METADATA_MANIFEST')
    require(manifest.get('release_state') == 'HOLD' and
            manifest.get('may_publish') is False and
            manifest.get('independent_QD_PASS') is False and
            manifest.get('medical_safety_verified') is False,
            'INVALID_MANIFEST_GOVERNANCE')
    require(type(r115) is dict and r115.get('schema') == R115_SCHEMA and
            r115.get('release_state') == 'HOLD' and
            r115.get('may_publish') is False,
            'R115_EVIDENCE_NOT_HELD')
    ref = manifest.get('reference_commit')
    require(type(ref) is str and BLOB.fullmatch(ref) and
            ref == r115.get('reference_commit'),
            'FROZEN_REFERENCE_COMMIT_MISMATCH')
    frozen = manifest.get('metadata_rows_NOT_APPROVED')
    old = r115.get('rows_NOT_APPROVED')
    require(type(frozen) is list and len(frozen) == 35 and
            type(old) is list and len(old) == 35 and
            manifest.get('metadata_count') == 35 and
            manifest.get('original_article_body_count') == 35,
            'INCOMPLETE_35_ARTICLE_CENSUS')
    old_slugs = [r.get('slug') for r in old if type(r) is dict]
    slugs = [r.get('slug') for r in frozen if type(r) is dict]
    require(len(old_slugs) == len(slugs) == 35 and
            len(set(old_slugs)) == len(set(slugs)) == 35 and
            all(type(s) is str and SLUG.fullmatch(s) for s in slugs),
            'DUPLICATE_OR_UNSAFE_SLUG')
    require(slugs == old_slugs and
            [r.get('n') for r in frozen] == [r.get('n') for r in old] and
            [r.get('n') for r in frozen] == list(range(1,36)),
            'FROZEN_READING_ORDER_CHANGED')
    require(type(metadata) is dict and set(metadata) == set(slugs) and
            type(body_names) in (set, frozenset) and body_names == set(slugs),
            'EXTRA_MISSING_OR_ORPHAN_ARTICLE_FILES')
    all_sources = 0
    counts = {'pending': 0, 'approved': 0, 'not-required': 0}
    for fresh, historical in zip(frozen, old):
        slug = fresh['slug']
        oid = fresh.get('metadata_git_blob_oid')
        require(type(oid) is str and BLOB.fullmatch(oid),
                'INVALID_FROZEN_METADATA_BLOB')
        raw = metadata[slug]
        require(type(raw) is bytes, 'INPUT_NOT_BYTES')
        require(git_blob(raw) == oid,
                'ORIGINAL_METADATA_CHANGED_REVIEW_REQUIRED_' + slug)
        data = strict_json(raw)
        require(type(data) is dict and data.get('slug') == slug and
                data.get('section') == historical.get('section') and
                data.get('track') == historical.get('track'),
                'METADATA_AUTHOR_IDENTITY_CHANGED_' + slug)
        st = data.get('status')
        require(type(st) is dict and st.get('publish') == 'draft',
                'UNAUTHORIZED_PUBLICATION_STATE_' + slug)
        safety = data.get('safety_review')
        require(type(safety) is dict and safety.get('state') in counts,
                'UNEXPECTED_SAFETY_STATE_' + slug)
        counts[safety['state']] += 1
        use = data.get('source_use')
        require(type(use) is dict and len(use) == historical.get('distinct_author_scoped_source_ids') and
                all(type(k) is str and SLUG.fullmatch(k) and type(v) is str and v.strip()
                    for k, v in use.items()),
                'AUTHOR_SOURCE_USE_SCOPE_CHANGED_' + slug)
        all_sources += len(use)
    require(counts == r115.get('self_reported_safety_metadata_counts'),
            'SAFETY_STATE_CENSUS_DRIFT')
    require(all_sources == r115.get('article_scoped_source_id_total_NOT_GLOBAL_UNIQUE'),
            'AUTHOR_SOURCE_USE_TOTAL_DRIFT')
    return {'schema': SCHEMA, 'issue': 136, 'business_issue': 820,
            'original_metadata_git_blobs_verified': 35,
            'paired_article_bodies_in_inventory': 35,
            'article_scoped_source_use_ids_NOT_GLOBAL_UNIQUE': all_sources,
            'historic_self_reported_safety_states_NOT_APPROVALS': counts,
            'modified_original_metadata': 0, 'orphan_or_extra_article_files': 0,
            'human_source_accuracy_verified': False, 'medical_safety_verified': False,
            'merchant_offer_verified': False, 'independent_QD_PASS': False,
            'may_publish': False, 'may_merge': False, 'release_state': 'HOLD'}

def audit_checkout(repo_root):
    prep = Path(repo_root) / 'preparedness'
    article_dir = prep / 'content' / 'articles'
    with (prep / 'docs/R116_FROZEN_35_METADATA_BLOB_CENSUS.json').open('rb') as f:
        manifest = strict_json(f.read())
    with (prep / 'docs/R115_FROZEN_ALL_35_AUTHOR_BODY_CENSUS.json').open('rb') as f:
        r115 = strict_json(f.read())
    require(article_dir.is_dir() and not article_dir.is_symlink(),
            'INVALID_ARTICLE_DIRECTORY')
    meta_paths = sorted(article_dir.glob('*.meta.json'))
    body_paths = sorted(article_dir.glob('*.body.html'))
    for path in meta_paths + body_paths:
        require(path.is_file() and not path.is_symlink(), 'UNSAFE_ARTICLE_FILE_ENTRY')
    meta = {p.name[:-len('.meta.json')]: p.read_bytes() for p in meta_paths}
    bodies = {p.name[:-len('.body.html')] for p in body_paths}
    require(len(meta) == len(meta_paths) and len(bodies) == len(body_paths),
            'DUPLICATE_FILE_STEMS')
    return audit(manifest, r115, meta, bodies)

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--repo-root', default='.')
    args = p.parse_args()
    try:
        print(json.dumps(audit_checkout(args.repo_root), sort_keys=True, indent=2))
        return 0  # Passing *inventory* never means content/safety/commerce approval.
    except (IntegrityHold, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'schema': SCHEMA, 'integrity': 'FAILED_CLOSED',
                          'reason': str(exc), 'may_publish': False,
                          'release_state': 'HOLD'}, sort_keys=True))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
