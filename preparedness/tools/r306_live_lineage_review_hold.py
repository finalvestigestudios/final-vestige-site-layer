#!/usr/bin/env python3
"""Read-only, fail-closed 35-article lineage and route crosswalk check.

Pinned upstream R200 + R305, observed integrated blobs, and outstanding body/
metadata differences. A matching SHA is file custody, NEVER independent QD,
source credibility, accessibility, medical safety or publication authorization.
No network, CMS or output writes. All samples and report outputs remain drafts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

PREDECESSOR = 'preparedness/tools/r305_html5_link_target_review_hold.py'
PREDECESSOR_OID = '06b00c46a704c59eb0a4f78360b3a92a43d133e9'
FROZEN = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
FROZEN_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
LEDGER = 'preparedness/audits/r306_live_lineage_35_articles_HARD_HOLD.json'
SCHEMA = 'fv-preparedness-r306-35-article-live-r200-lineage-crosswalk-v1'
SHA40 = re.compile(r'[a-f0-9]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def git_blob(b: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(b)).encode('ascii') + b'\0' + b).hexdigest()


def safe(root: Path, relative: str) -> bool:
    try:
        base = root.absolute()
        path = (base / relative).absolute()
        if not path.is_relative_to(base) or not path.is_file():
            return False
        while path != base:
            if path.is_symlink():
                return False
            path = path.parent
        return True
    except (RuntimeError, ValueError, OSError):
        return False


def audit(root: Path, ledger: dict, frozen: dict) -> dict:
    ledger = ledger if isinstance(ledger, dict) else {}
    frozen = frozen if isinstance(frozen, dict) else {}
    errors: list[str] = []
    actual = ledger.get('articles') if isinstance(ledger, dict) else None
    historic = frozen.get('articles') if isinstance(frozen, dict) else None
    if not isinstance(ledger, dict) or ledger.get('schema') != SCHEMA:
        errors.append('UNKNOWN_OR_ABSENT_SCHEMA')
    if (not isinstance(actual, list) or len(actual) != 35 or
            not isinstance(historic, list) or len(historic) != 35):
        errors.append('INCOMPLETE_35_ARTICLE_LEDGER')
        actual = actual if isinstance(actual, list) else []
        historic = historic if isinstance(historic, list) else []
    frozen_by_slug = {r.get('slug'): r for r in historic if isinstance(r, dict)}
    slugs: set[str] = set()
    routes: set[str] = set()
    verified_files = 0
    body_changes = meta_changes = both_changes = format_only = 0
    status_counts: dict[str, int] = {}
    for row in actual:
        if not isinstance(row, dict):
            errors.append('MALFORMED_LEDGER_ROW'); continue
        slug = row.get('slug')
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            errors.append('INVALID_ARTICLE_SLUG'); continue
        if slug in slugs:
            errors.append('DUPLICATE_SLUG:' + slug); continue
        slugs.add(slug)
        f = frozen_by_slug.get(slug)
        if f is None:
            errors.append('UNKNOWN_FROZEN_ARTICLE:' + slug); continue
        if row.get('n') != f.get('n') or row.get('source_cluster') != f.get('source_cluster'):
            errors.append('ARTICLE_ORDER_OR_CLUSTER_DRIFT:' + slug)
        route = row.get('route')
        if route != f.get('route') or not isinstance(route, str) or not route.startswith('/preparedness/'):
            errors.append('CANONICAL_ROUTE_DRIFT:' + slug)
        elif route in routes:
            errors.append('DUPLICATE_CANONICAL_ROUTE:' + slug)
        routes.add(route)
        bchange = row.get('frozen_body_blob') != row.get('integrated_body_blob')
        mchange = row.get('frozen_meta_blob') != row.get('integrated_meta_blob')
        if row.get('frozen_body_blob') != f.get('body_oid') or row.get('frozen_meta_blob') != f.get('meta_oid'):
            errors.append('FROZEN_SOURCE_IDENTITY_DRIFT:' + slug)
        if row.get('frozen_branch_sha') != f.get('branch_sha'):
            errors.append('FROZEN_BRANCH_DRIFT:' + slug)
        body_changes += bchange; meta_changes += mchange; both_changes += bchange and mchange
        fmt = row.get('line_endings_only_observed')
        if not isinstance(fmt, bool) or (fmt and not bchange):
            errors.append('UNSUPPORTED_FORMAT_ONLY_ATTESTATION:' + slug)
        format_only += (fmt is True)
        expected_status = ('FORMAT_ONLY_OBSERVED_QA_PENDING' if fmt else
            'CONTENT_CHANGE_UNADJUDICATED' if bchange else
            'METADATA_CHANGE_UNADJUDICATED' if mchange else
            'FROZEN_IDENTITY_ONLY_QA_PENDING')
        if row.get('review_state') != expected_status:
            errors.append('MISLEADING_REVIEW_STATUS:' + slug)
        status_counts[expected_status] = status_counts.get(expected_status, 0) + 1
        for ext, key in (('body.html', 'integrated_body_blob'), ('meta.json', 'integrated_meta_blob')):
            oid = row.get(key)
            if not isinstance(oid, str) or not SHA40.fullmatch(oid):
                errors.append('INVALID_BLOB_OID:' + slug + ':' + key); continue
            path = 'preparedness/content/articles/' + slug + '.' + ext
            if not safe(root, path):
                errors.append('UNAVAILABLE_OR_SYMLINK:' + path); continue
            try:
                if git_blob((root / path).read_bytes()) != oid:
                    errors.append('INTEGRATED_BLOB_MISMATCH:' + path)
                else:
                    verified_files += 1
            except OSError:
                errors.append('UNREADABLE_INTEGRATED_FILE:' + path)
    if set(frozen_by_slug) != slugs:
        errors.append('FROZEN_SLATE_NOT_EXHAUSTIVELY_MATCHED')
    content = root / 'preparedness/content/articles'
    if content.is_dir():
        expected = {slug + '.' + ext for slug in slugs for ext in ('body.html', 'meta.json')}
        observed = {p.name for p in content.iterdir() if p.is_file() or p.is_symlink()}
        if expected != observed:
            errors.append('MISSING_OR_UNTRACKED_ARTICLE_INPUTS')
    if ledger.get('state') != 'DRAFT_HARD_HOLD' or any(ledger.get(k) is not False for k in
        ('publication_authorized','independent_qd_pass','medical_safety_verified',
         'privacy_verified','paid_offer_approved','all_41_native_exports_verified')):
        errors.append('FALSE_RELEASE_OR_COMMERCE_APPROVAL')
    if (body_changes, meta_changes, both_changes, format_only) != (14,12,9,4):
        errors.append('LINEAGE_COUNTS_DIFFER_FROM_EVIDENCE')
    if len(actual) != 35 or verified_files != 70:
        errors.append('INCOMPLETE_AUTHENTIC_INPUT_REVIEW')
    return {
        'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
        'errors': sorted(set(errors)), 'article_records': len(actual),
        'integrated_file_blobs_verified': verified_files, 'body_changes': body_changes,
        'metadata_changes': meta_changes, 'both_changed': both_changes,
        'line_endings_only_observed': format_only, 'review_states': status_counts,
        'historical_difference_adjudicated': False, 'native_build_executed': False,
        'all_41_native_exports_verified': False, 'independent_qd_pass': False,
        'medical_safety_verified': False, 'privacy_verified': False,
        'paid_offer_approved': False, 'publication_authorized': False,
        'verified_paid_orders': None, 'net_revenue_per_1000_qualified_human_sessions': None,
    }


def run(root: Path) -> dict:
    for path, oid in ((PREDECESSOR, PREDECESSOR_OID), (FROZEN, FROZEN_OID)):
        if not safe(root, path) or git_blob((root / path).read_bytes()) != oid:
            raise ValueError('MISSING_OR_MUTATED_PINNED_PREDECESSOR:' + path)
    if not safe(root, LEDGER):
        raise ValueError('MISSING_OR_MUTATED_LEDGER')
    return audit(root, json.loads((root / LEDGER).read_text('utf-8')),
                 json.loads((root / FROZEN).read_text('utf-8')))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    opts = p.parse_args(argv)
    try:
        result = run(opts.repo_root)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, UnicodeError) as exc:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'errors': ['AUTHENTIC_BUILD_UNAVAILABLE:' + type(exc).__name__],
                  'publication_authorized': False, 'independent_qd_pass': False,
                  'medical_safety_verified': False, 'all_41_native_exports_verified': False}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2 if result['state'] == 'DRAFT_HARD_HOLD' else 1

if __name__ == '__main__':
    raise SystemExit(main())
