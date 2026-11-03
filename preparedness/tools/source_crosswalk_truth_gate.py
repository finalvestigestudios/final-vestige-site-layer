#!/usr/bin/env python3
"""R17: exact source-crosswalk custody with explicit provenance-alias disclosure.

A structural/audit tool, NOT a source-fact checker. All results remain HOLD.
No repository writes, network access, publishing or automatic review state changes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

SOURCE_PATHS = {
    'base': 'preparedness/sources/register.json',
    'start': 'preparedness/sources/fragments/start.json',
    'shelter': 'preparedness/sources/fragments/shelter.json',
    'food': 'preparedness/sources/fragments/food.json',
    'hist-food': 'preparedness/sources/fragments/hist-food.json',
    'health': 'preparedness/sources/fragments/health.json',
    'hist-home': 'preparedness/sources/fragments/hist-home.json',
    'hist-field': 'preparedness/sources/fragments/hist-field.json',
}
AUTHOR_HEADS = {
    'base': 'ee591e2df5de08aea7603fc4cbf3c5249361e119',
    'start': '2122d856fce9f64887c16df3d52e64be9f59a55b',
    'shelter': '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
    'food': '4b009361277ea1d4617b368f5d45104c7318b284',
    'hist-food': '2acf65ca3efa9b4b5db7976f379b9ea693be43a4',
    'health': 'd2212d0ca0750817d3929865d3069835980faf20',
    'hist-home': 'f654e600f89c321a480dd8f055be4d13d0673490',
    'hist-field': 'a5ce8a62f168db05c95232e3eb385dccd0d19e7f',
}
# The integration's crosswalk currently describes the synthetic QA fixture PR
# #169 as the food *source head*, even though the original Claude food branch
# is a distinct SHA. The fragment Git blob matches at both heads, but the
# provenance label must not be silently misrepresented as an author commit.
KNOWN_NONAUTHOR_ALIAS = {
    'food': 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
}
CROSSWALK = 'preparedness/sources/crosswalk.json'
# Existing original author instructions are documentation, not a ninth inventory.
# Keep their exact Git blob pinned; never silently discard or rewrite them.
FRAGMENT_README = 'preparedness/sources/fragments/README.md'
FRAGMENT_README_GIT_BLOB = 'cec167dd6acaf9f6e92e87a61fa9aeacdad151a5'
PENDING = 'pending-human-source-and-reading-scope-review'
# Stage 3b (2026-11-03): integrated candidate census (was 224/186/30/15/15); see the
# stage 3b ledger. The 20 added rows are all read rows, so unread placeholders stay 15.
EXPECTED = dict(source_rows=244, unique_urls=202, shared_urls=32,
                duplicate_id_groups=15, unread_placeholders=15)


class CustodyError(ValueError):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise CustodyError(message)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha256(obj: object) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def file_at(root: Path, relative: str, *, limit: int = 3_000_000) -> bytes:
    path = root / relative
    need(root.is_dir() and not root.is_symlink(), 'invalid repository root')
    need(path.is_file() and not path.is_symlink() and
         path.resolve().is_relative_to(root.resolve()),
         'missing, linked or out-of-tree file: ' + relative)
    b = path.read_bytes()
    need(0 < len(b) <= limit, 'invalid source file size: ' + relative)
    return b


def checked_json(raw: bytes, label: str) -> dict:
    try:
        obj = json.loads(raw.decode('utf-8'))
    except (ValueError, UnicodeError) as exc:
        raise CustodyError('invalid JSON: ' + label) from exc
    need(type(obj) is dict, 'JSON object required: ' + label)
    return obj


def safe_url(url: str) -> None:
    need(type(url) is str and len(url) < 2048 and
         not any(ord(x) <= 32 for x in url) and '\\' not in url,
         'invalid source URL bytes')
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise CustodyError('invalid source URL authority') from exc
    need(parts.scheme == 'https' and bool(parts.hostname) and
         parts.username is None and parts.password is None and
         port in (None, 443) and '@' not in parts.netloc and
         not parts.fragment and not url.startswith('https:////'),
         'invalid source URL destination')


def key(origin: str, idx: int, row: dict) -> tuple[str, int, str]:
    ident = row.get('id')
    need(type(ident) is str and bool(ident), 'missing source id')
    return origin, idx, ident


def audit(root: Path, *, expected: dict | None = None,
          author_heads: dict | None = None,
          known_aliases: dict | None = None) -> dict:
    expected = EXPECTED if expected is None else expected
    author_heads = AUTHOR_HEADS if author_heads is None else author_heads
    known_aliases = KNOWN_NONAUTHOR_ALIAS if known_aliases is None else known_aliases
    need(set(author_heads) == set(SOURCE_PATHS), 'incomplete author head allowlist')
    root = root.resolve(strict=True)
    cw = checked_json(file_at(root, CROSSWALK), CROSSWALK)
    need(cw.get('schema_version') == 1, 'crosswalk version drift')
    need(cw.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
         'unexpected source review state')
    for field in ('may_publish', 'qualified_safety_clearance', 'human_source_review_complete'):
        need(cw.get(field) is not True, 'crosswalk attempts to grant approval: ' + field)
    origin_heads = cw.get('source_head_commits')
    need(type(origin_heads) is dict and set(origin_heads) == set(author_heads),
         'crosswalk source head origin mismatch')
    aliases = []
    for origin, author_sha in author_heads.items():
        recorded = origin_heads[origin]
        need(type(recorded) is str and len(recorded) == 40, 'bad source head SHA: ' + origin)
        if recorded == author_sha:
            continue
        need(origin in known_aliases and recorded == known_aliases[origin],
             'unexpected provenance head drift: ' + origin)
        aliases.append({'origin': origin, 'recorded_sha': recorded,
                        'actual_author_sha': author_sha,
                        'status': 'KNOWN_NONAUTHOR_QA_FIXTURE_HEAD_REQUIRES_RECONCILIATION',
                        'independent_live_ref_check': 'REQUIRED'})

    listed = cw.get('source_files')
    need(type(listed) is list and len(listed) == len(SOURCE_PATHS),
         'missing or extra source file records')
    by_origin = {}
    for record in listed:
        need(type(record) is dict and record.get('origin') in SOURCE_PATHS,
             'unknown source origin')
        origin = record['origin']
        need(origin not in by_origin and record.get('path') == SOURCE_PATHS[origin],
             'duplicate or incorrect source file path: ' + origin)
        by_origin[origin] = record
    need(set(by_origin) == set(SOURCE_PATHS), 'source file coverage incomplete')
    fragment_dir = root / 'preparedness/sources/fragments'
    need(fragment_dir.is_dir() and not fragment_dir.is_symlink(), 'source fragments dir missing')
    entries = list(fragment_dir.iterdir())
    need(all(p.is_file() and not p.is_symlink() for p in entries),
         'linked or non-file source fragment directory entry')
    observed_files = {p.name for p in entries}
    expected_json = {Path(p).name for o, p in SOURCE_PATHS.items() if o != 'base'}
    # The original tracked README.md sits alongside the seven contributor JSON
    # fragments. It does not contain source rows and must never be counted as
    # an eighth fragment. Allow no other extras, including hidden/temp files.
    allowed_with_documentation = expected_json | {Path(FRAGMENT_README).name}
    if expected == EXPECTED:
        # Frozen full integrated archive must retain its original instructions.
        need(observed_files == allowed_with_documentation,
             'original source fragment README missing or unexpected inventory entry')
    else:
        # Smaller synthetic fixtures intentionally contain JSON fragments only.
        need(observed_files in (expected_json, allowed_with_documentation),
             'unregistered fragment file present or source fragment missing')
    if Path(FRAGMENT_README).name in observed_files:
        need(git_blob(file_at(root, FRAGMENT_README)) == FRAGMENT_README_GIT_BLOB,
             'original source fragment instructions drift')

    rows = []
    urls: dict[str, list[tuple[tuple[str, int, str], dict]]] = defaultdict(list)
    ids: Counter[str] = Counter()
    id_urls: dict[str, set[str]] = defaultdict(set)
    for origin, path in SOURCE_PATHS.items():
        raw = file_at(root, path)
        record = by_origin[origin]
        need(git_blob(raw) == record.get('git_blob_sha'),
             'source record blob drift: ' + origin)
        src = checked_json(raw, path).get('sources')
        need(type(src) is list and len(src) == record.get('count'),
             'source row count drift: ' + origin)
        for idx, row in enumerate(src):
            need(type(row) is dict, 'non-object source row')
            ident = key(origin, idx, row)
            safe_url(row.get('url'))
            need(row.get('human_link_check') is False,
                 'human link review status requires independent review receipt')
            need(row.get('verified_on') is None or type(row.get('verified_on')) is str,
                 'invalid machine-read date')
            ids[row['id']] += 1
            id_urls[row['id']].add(row['url'])
            urls[row['url']].append((ident, row))
            rows.append((ident, row))
    need(all(len(v) == 1 for v in id_urls.values()),
         'one source id assigned conflicting URLs')
    need(len(rows) == expected['source_rows'], 'source row inventory drift')
    need(len(urls) == expected['unique_urls'], 'distinct source URL inventory drift')
    shared = {url: variants for url, variants in urls.items() if len(variants) > 1}
    need(len(shared) == expected['shared_urls'], 'shared source URL inventory drift')
    need(sum(n > 1 for n in ids.values()) == expected['duplicate_id_groups'],
         'duplicate source ID inventory drift')
    need(sum(row.get('verified_on') is None for _, row in rows) ==
         expected['unread_placeholders'], 'unread placeholder inventory drift')
    for fld, value in [('raw_source_rows', 'source_rows'),
                       ('unique_source_urls', 'unique_urls'),
                       ('duplicate_url_groups', 'shared_urls'),
                       ('duplicate_id_groups', 'duplicate_id_groups')]:
        need(cw.get(fld) == expected[value], 'crosswalk count drift: ' + fld)
    groups = cw.get('groups')
    need(type(groups) is list and len(groups) == len(shared),
         'crosswalk shared group count drift')
    observed_groups = set()
    queue = []
    for group in groups:
        need(type(group) is dict, 'malformed shared-source group')
        url = group.get('url')
        need(type(url) is str and url in shared and url not in observed_groups,
             'untracked or duplicated shared-source group')
        observed_groups.add(url)
        need(group.get('canonical_url') == url, 'source URL redirected or silently canonicalized')
        need(group.get('review_status') == PENDING and
             group.get('reviewer') is None and group.get('reviewed_on') is None,
             'shared-source group review cannot be silently approved')
        present = {identity: row for identity, row in shared[url]}
        identities = group.get('identities')
        variants = group.get('variants')
        need(type(identities) is list and type(variants) is list and
             len(identities) == len(variants) == len(present),
             'incomplete shared source variants')
        recorded_ids = set()
        for ident in identities:
            need(type(ident) is dict, 'non-object source identity')
            identity = ident.get('origin'), ident.get('row_index'), ident.get('id')
            need(identity in present and identity not in recorded_ids,
                 'crosswalk identity mismatch')
            recorded_ids.add(identity)
        recorded_variants = set()
        for variant in variants:
            need(type(variant) is dict and type(variant.get('source')) is dict,
                 'malformed source variant')
            source = variant['source']
            identity = (variant.get('origin'), variant.get('row_index'), source.get('id'))
            need(identity in present and identity not in recorded_variants,
                 'source variant identity mismatch')
            need(variant.get('source_file') == SOURCE_PATHS[identity[0]],
                 'source variant file attribution mismatch')
            need(canonical(source) == canonical(present[identity]),
                 'crosswalk source note/reading-depth drift: '+str(identity))
            recorded_variants.add(identity)
        need(recorded_ids == recorded_variants == set(present),
             'source identity coverage gap')
        observations = [row for _k, row in shared[url]]
        queue.append({'url': url,
                      'identity_count': len(present),
                      'variant_fingerprint': sha256(sorted([{'id': k, 'source': row}
                                                           for k, row in present.items()],
                                                          key=lambda v: str(v['id']))),
                      'origins': sorted({i[0] for i in present}),
                      'has_unread_placeholder': any(v.get('verified_on') is None for v in observations),
                      'distinct_machine_use_explanations': len({v.get('supports') or '' for v in observations}),
                      'human_review_status': 'PENDING',
                      'qualified_safety_review': False})
    need(observed_groups == set(shared), 'shared-source crosswalk coverage gap')
    queue.sort(key=lambda item: item['url'])
    result = {
        'schema_version': 1,
        'release_state': 'HOLD', 'may_publish': False,
        'article_claim_accuracy_verified': False,
        'qualified_safety_clearance': False,
        'human_source_reviews_complete': False,
        'source_row_count': len(rows),
        'unique_literal_urls': len(urls),
        'unresolved_shared_url_groups': len(shared),
        'unread_source_placeholders': sum(r.get('verified_on') is None for _, r in rows),
        'duplicate_source_id_groups': sum(n > 1 for n in ids.values()),
        'crosswalk_git_blob_sha': git_blob(file_at(root, CROSSWALK)),
        'fragment_readme_git_blob_sha': (
            FRAGMENT_README_GIT_BLOB if Path(FRAGMENT_README).name in observed_files else None),
        'non_author_source_head_aliases': aliases,
        'source_group_review_queue': queue,
    }
    result['audit_fingerprint'] = sha256(result)
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Read-only exact source/crosswalk custody: always HOLD')
    ap.add_argument('--repo-root', default='.')
    args = ap.parse_args(argv)
    try:
        result = audit(Path(args.repo_root))
    except (CustodyError, OSError, ValueError) as exc:
        print(json.dumps({'release_state': 'HOLD', 'may_publish': False,
                          'integrity_check': 'FAILED', 'error': str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0  # structural success is NOT a release/publishing clearance


if __name__ == '__main__':
    raise SystemExit(main())
