#!/usr/bin/env python3
"""R319: read-only three-way source custody, not a publication or safety approval.

The signed source tree inventory compares R317 against the two later Shelter
branches. Differences remain human review items; no automatic merges occur.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = 'fv-preparedness-r319-three-way-source-custody-v1'
MANIFEST_PATH = 'preparedness/audits/r319_three_way_custody_manifest.json'
BASELINE = {'ref': 'automation/prep-r317-test-source-write-sentinel-20261112',
            'sha': '0335416a3b658f5f626489c428aa61e8890bf90d'}
BRANCHES = {
    'continuation': {'ref': 'claude/prep-shelter-continuation',
                     'sha': 'ac8625faf30dd5538fadc31e06cb5a2cea1defae'},
    'followup': {'ref': 'claude/prep-shelter-followup-evidence',
                 'sha': '6a5998ead97eca997e573ce8d3ceacf1c6aabad4'},
}
EXPECTED = {'article_bodies': 35, 'article_metadata': 35, 'tool_bodies': 6,
            'tool_metadata': 6, 'total_records': 82, 'integrated_only': 54,
            'identical': 13, 'review_required': 15,
            'changed_bodies': 6, 'changed_metadata': 9}
SOURCE_PATH = re.compile(r'^preparedness/content/(articles|tools)/([a-z0-9]+(?:-[a-z0-9]+)*)\.(body\.html|meta\.json)$')
GIT_SHA = re.compile(r'^[0-9a-f]{40}$')
ALLOWED_DISPOSITIONS = {'INTEGRATED_ONLY', 'IDENTICAL', 'HUMAN_REVIEW_REQUIRED'}
SAFETY_CRITICAL = {'family-communication-plan', 'shelter-or-evacuate',
                   'outage-heat-cold-generators', 'reunification-plan',
                   'making-water-safer', 'homemade-water-filters'}


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def safe_bytes(root: Path, rel: str) -> bytes | None:
    if not SOURCE_PATH.fullmatch(rel):
        return None
    try:
        root = root.absolute()
        if root.is_symlink():
            return None
        p = root
        for part in Path(rel).parts:
            p = p / part
            if p.is_symlink():
                return None
        return p.read_bytes() if p.is_file() else None
    except (OSError, RuntimeError, ValueError):
        return None


def _source_ref(value: object) -> bool:
    return (isinstance(value, dict) and set(value) == {'sha', 'size'}
            and isinstance(value['sha'], str) and bool(GIT_SHA.fullmatch(value['sha']))
            and type(value['size']) is int and value['size'] >= 0)


def validate_manifest(manifest: object, root: Path | None = None) -> dict:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD', 'errors': ['INVALID_MANIFEST'],
                'source_safety_qd_approved': False, 'publishing_authorized': False}
    if manifest.get('schema') != SCHEMA: errors.append('SCHEMA_MISMATCH')
    if manifest.get('baseline') != BASELINE: errors.append('BASELINE_SHA_OR_REF_DRIFT')
    if manifest.get('branches') != BRANCHES: errors.append('CONTRIBUTOR_SHA_OR_REF_DRIFT')
    if manifest.get('expected') != EXPECTED: errors.append('EXPECTED_SOURCE_COUNTS_DRIFT')
    if manifest.get('release') != {'publication_authorized': False, 'qualified_safety_approved': False,
                                  'independent_qd_pass': False, 'paid_conversion_verified': False}:
        errors.append('INVALID_RELEASE_HOLD')
    rows = manifest.get('records')
    if not isinstance(rows, list):
        rows = []; errors.append('MISSING_SOURCE_RECORDS')
    counts = {k: 0 for k in ('article_bodies', 'article_metadata', 'tool_bodies',
                              'tool_metadata', 'integrated_only', 'identical', 'review_required',
                              'changed_bodies', 'changed_metadata')}
    slugs: dict[str, set[str]] = {'articles': set(), 'tools': set()}
    names: set[str] = set(); required_review: list[str] = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or set(r) != {'path', 'integrated', 'continuation', 'followup', 'disposition'}:
            errors.append('INVALID_RECORD_SHAPE:' + str(i)); continue
        path = r['path']
        m = SOURCE_PATH.fullmatch(path) if isinstance(path, str) else None
        if not m:
            errors.append('INVALID_SOURCE_PATH:' + str(i)); continue
        if path in names: errors.append('DUPLICATE_SOURCE_PATH:' + path)
        names.add(path)
        family, slug, extension = m.groups()
        slugs[family].add(slug)
        kind = ('article' if family == 'articles' else 'tool') + ('_bodies' if extension == 'body.html' else '_metadata')
        counts[kind] += 1
        if not _source_ref(r['integrated']):
            errors.append('INVALID_INTEGRATED_BLOB:' + path); continue
        branches_ok = all(x is None or _source_ref(x) for x in (r['continuation'], r['followup']))
        if not branches_ok:
            errors.append('INVALID_CONTRIBUTOR_BLOB:' + path); continue
        forks = [x for x in (r['continuation'], r['followup']) if x is not None]
        derived = ('INTEGRATED_ONLY' if not forks else 'IDENTICAL' if all(
            x['sha'] == r['integrated']['sha'] and x['size'] == r['integrated']['size'] for x in forks)
                   else 'HUMAN_REVIEW_REQUIRED')
        if r['disposition'] != derived or r['disposition'] not in ALLOWED_DISPOSITIONS:
            errors.append('MISCLASSIFIED_CONFLICT:' + path)
        count_key = {'INTEGRATED_ONLY': 'integrated_only', 'IDENTICAL': 'identical',
                     'HUMAN_REVIEW_REQUIRED': 'review_required'}[derived]
        counts[count_key] += 1
        if derived == 'HUMAN_REVIEW_REQUIRED':
            required_review.append(path)
            counts['changed_bodies' if extension == 'body.html' else 'changed_metadata'] += 1
        if root is not None:
            raw = safe_bytes(root, path)
            if raw is None:
                errors.append('MISSING_OR_LINKED_INTEGRATED_SOURCE:' + path)
            elif blob(raw) != r['integrated']['sha'] or len(raw) != r['integrated']['size']:
                errors.append('SOURCE_CONTENT_CHANGED_REQUIRES_NEW_REVIEW:' + path)
    if len(rows) != EXPECTED['total_records']:
        errors.append('SOURCE_RECORD_TOTAL_DRIFT')
    for key, actual in counts.items():
        if actual != EXPECTED[key]: errors.append('COUNT_DRIFT:' + key)
    if len(slugs['articles']) != 35 or len(slugs['tools']) != 6:
        errors.append('ARTICLE_OR_TOOL_SLUG_COUNT_DRIFT')
    for family, slugs_in_family in slugs.items():
        for slug in slugs_in_family:
            body = f'preparedness/content/{family}/{slug}.body.html'
            meta = f'preparedness/content/{family}/{slug}.meta.json'
            if body not in names or meta not in names:
                errors.append('MISSING_BODY_OR_METADATA_PAIR:' + family + '/' + slug)
    if root is not None:
        for family in ('articles', 'tools'):
            directory = root / 'preparedness' / 'content' / family
            if not directory.is_dir() or directory.is_symlink():
                errors.append('MISSING_OR_LINKED_SOURCE_DIRECTORY:' + family); continue
            actual = {f'preparedness/content/{family}/{p.name}' for p in directory.iterdir()
                      if p.name.endswith(('.body.html', '.meta.json'))}
            if actual != {p for p in names if p.startswith('preparedness/content/' + family + '/')}:
                errors.append('UNREVIEWED_ADDED_OR_REMOVED_SOURCE:' + family)
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'source_rows': len(rows),
            'human_review_required': sorted(required_review),
            'review_required_count': len(required_review),
            'critical_review_candidates': sorted(set(SOURCE_PATH.fullmatch(p).group(2)
                for p in required_review if SOURCE_PATH.fullmatch(p)) & SAFETY_CRITICAL),
            'source_safety_qd_approved': False, 'publishing_authorized': False,
            'paid_conversion_verified': False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        manifest_path = args.root / MANIFEST_PATH
        if manifest_path.is_symlink(): raise ValueError('manifest is linked')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        result = validate_manifest(manifest, args.root)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'errors': ['AUTHENTIC_MANIFEST_OR_CHECKOUT_UNAVAILABLE'],
                  'source_safety_qd_approved': False, 'publishing_authorized': False,
                  'paid_conversion_verified': False}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result['state'] == 'INVALID_HARD_HOLD' else 2

if __name__ == '__main__': raise SystemExit(main())
