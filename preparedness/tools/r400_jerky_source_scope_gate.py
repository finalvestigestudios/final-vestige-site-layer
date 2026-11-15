#!/usr/bin/env python3
"""Read-only post-freeze Article #11 source-scope review gate (Issue #136).

Structural PASS never means qualified food-safety approval or permission to publish.
Source URLs and scope identifiers are deliberately pinned; a reviewer must amend
and re-review code and tests to change them. Original docket remains immutable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ORIGINAL_DOCKET_BLOB = '86d22a1d504c93db7689b914e2202a7845b648e2'
ORIGINAL_SOURCE_BLOBS = frozenset({
    'a1f73c8170932d6b3192e9cd506686d516d23d30',
    'c1856c998c6c728f0de72221e5654a238df994a9',
})
STATE = 'DRAFT_HARD_HOLD'
SOURCE_POLICY = {
    'umn_drying': (
        'https://extension.umn.edu/food/preparing/cooking-at-home/food-preservation/drying',
        'DIRECT_HTML', 'MEAT_JERKY_REFRIGERATION_EXCEPTION', '2026-11-15',
    ),
    'umn_cooking_without_kitchen': (
        'https://extension.umn.edu/natural-resources/weather-and-climate/prepare-for-risks/cooking-without-a-kitchen',
        'DIRECT_HTML', 'JERKY_LISTED_AMONG_ROOM_TEMPERATURE_FOODS', '2026-11-15',
    ),
    'nchfp_home_jerky': (
        'https://nchfp.uga.edu/how/dry/recipes/jerky/',
        'DIRECT_HTML', 'CONDITIONAL_HOME_JERKY_STORAGE', '2026-11-15',
    ),
    'gpo_fsis_2011_catalog': (
        'https://www.govinfo.gov/app/details/GOVPUB-A110-PURL-gpo38739',
        'OFFICIAL_BIBLIOGRAPHY', 'ARCHIVED_2011_NOT_CURRENT_POLICY', '2026-11-15',
    ),
    'fsis_ask_jerky': (
        'https://ask.fsis.usda.gov/article/How-do-I-dry-jerky',
        'INDEX_ONLY_NOT_DIRECTLY_CHECKED', 'NEWER_FAQ_FULL_TEXT_NOT_AUTHENTICATED', '2026-11-15',
    ),
}
CONFLICT_POLICY = {
    'umn_cross_page_storage_scope': ('umn_drying', 'umn_cooking_without_kitchen'),
    'home_processing_storage_scope': ('umn_drying', 'nchfp_home_jerky'),
    'commercial_versus_home_scope': ('gpo_fsis_2011_catalog', 'nchfp_home_jerky'),
    'pre_post_drying_sequence_not_adjudicated': ('fsis_ask_jerky', 'nchfp_home_jerky'),
}
RELEASE_FALSE = (
    'publication_approved', 'qualified_safety_approved',
    'merchant_offer_verified', 'paid_cta_approved',
    'automatic_source_selection', 'human_link_check_complete',
)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def inspect(docket_raw: bytes, registry_raw: bytes, *, docket_pin: str = ORIGINAL_DOCKET_BLOB) -> dict:
    """Validate source/custody *structure*, not advice; fail closed on any mutation."""
    failures: list[str] = []
    def need(ok: bool, tag: str) -> None:
        if not ok:
            failures.append(tag)
    need(git_blob(docket_raw) == docket_pin, 'original_docket_blob')
    try:
        docket, register = json.loads(docket_raw), json.loads(registry_raw)
        need(isinstance(docket, dict) and isinstance(register, dict), 'json_root')
        if not isinstance(docket, dict) or not isinstance(register, dict):
            raise ValueError('non-object root')
    except (TypeError, ValueError, UnicodeError):
        return {'integrity': 'FAIL', 'release': STATE, 'failures': ['invalid_json'], 'eligible': False}
    need(register.get('schema') == 'r400.source-scope-review.v1', 'schema')
    need(register.get('source_docket_git_blob') == docket_pin, 'source_pin')
    need(register.get('article_slug') == 'safe-jerky-dehydration', 'article_slug')
    need(register.get('source_id') == 'nchfp-jerky', 'source_id')
    need(register.get('editorial_issue') == 136, 'editorial_issue')
    need(register.get('conversion_issue') == 820, 'conversion_issue')
    need(register.get('business_charter_issue') == 818, 'business_charter')
    need(register.get('review_comment_ids') == [6901118072, 6901975450], 'editorial_comment_custody')
    need(register.get('state') == STATE and register.get('decision') == 'HUMAN_ADJUDICATION_REQUIRED', 'hold_state')
    for flag in RELEASE_FALSE:
        need(register.get(flag) is False, 'release_flag:' + flag)
    need(register.get('selected_source_id') is None, 'source_autoselected')
    need(register.get('selected_manuscript_blob') is None, 'manuscript_autoselected')
    need(register.get('current_household_instructions') is None, 'unsafe_instructions')
    need(register.get('actual_paid_preparedness_sku') is None, 'speculative_sku')
    need(docket.get('release_state') == STATE and docket.get('publication_approved') is False
         and docket.get('qualified_safety_approved') is False
         and docket.get('automatic_variant_selection') is False, 'original_hold_modified')
    expected = docket.get('expected', {})
    need(all(expected.get(k) == n for k, n in {
        'original_article_count': 35, 'original_distinct_source_ids': 203,
        'source_record_occurrences': 280, 'source_evidence_disputes': 5,
        'unselected_original_forks': 9,
    }.items()), 'original_inventory_changed')
    need(len(docket.get('original_articles', [])) == 35, 'missing_original_articles')
    need('safe-jerky-dehydration' in {a.get('slug') for a in docket.get('original_articles', []) if isinstance(a, dict)}, 'original_article_identity')
    disputes = [s for s in docket.get('source_evidence_disputes', []) if isinstance(s, dict) and s.get('source_id') == 'nchfp-jerky']
    need(len(disputes) == 1, 'original_source_dispute')
    if len(disputes) == 1:
        src = disputes[0]
        need(src.get('decision') == 'HUMAN_REVIEW_REQUIRED' and src.get('selected_record') is None, 'original_dispute_selected')
        variants = src.get('variants', [])
        need(len(variants) == 2 and {v.get('source_blob') for v in variants if isinstance(v, dict)} == ORIGINAL_SOURCE_BLOBS, 'original_candidate_blobs')
        need(all(v.get('human_link_check') is False for v in variants if isinstance(v, dict)), 'original_human_link_status')
    sources = register.get('sources')
    need(isinstance(sources, list) and len(sources) == len(SOURCE_POLICY), 'source_count')
    ids: set[str] = set()
    if isinstance(sources, list):
        for item in sources:
            if not isinstance(item, dict):
                failures.append('invalid_source_entry')
                continue
            sid = item.get('id', '')
            need(isinstance(sid, str) and sid not in ids, 'duplicate_source')
            if isinstance(sid, str): ids.add(sid)
            expected_src = SOURCE_POLICY.get(sid)
            need(expected_src is not None, 'unexpected_source:' + str(sid))
            if expected_src:
                for key, target in zip(('url', 'evidence_level', 'scope', 'observed_on'), expected_src):
                    need(item.get(key) == target, f'source_field:{sid}:{key}')
            need(item.get('human_reviewer_checked') is False, 'false_human_review:' + str(sid))
            need(item.get('usable_as_current_home_method') is False, 'unsafe_source_promotion:' + str(sid))
            need(item.get('selected_for_article') is False, 'unapproved_source_selection:' + str(sid))
    need(ids == set(SOURCE_POLICY), 'source_id_set')
    conflicts = register.get('conflicts')
    need(isinstance(conflicts, list) and len(conflicts) == len(CONFLICT_POLICY), 'conflict_count')
    cids: set[str] = set()
    if isinstance(conflicts, list):
        for item in conflicts:
            if not isinstance(item, dict):
                failures.append('invalid_conflict_entry')
                continue
            cid = item.get('id', '')
            need(isinstance(cid, str) and cid not in cids, 'duplicate_conflict')
            if isinstance(cid, str): cids.add(cid)
            need(item.get('source_ids') == list(CONFLICT_POLICY.get(cid, ())), 'conflict_sources:' + str(cid))
            need(item.get('decision') == 'UNRESOLVED_HUMAN_REVIEW' and item.get('approved_public_guidance') is False, 'conflict_premature_approval:' + str(cid))
    need(cids == set(CONFLICT_POLICY), 'conflict_id_set')
    if isinstance(register.get('review_requirements'), list):
        required = {'product_and_processing_scope', 'source_date_and_currency', 'storage_conditions',
                    'processing_sequence', 'species_specific_risks', 'independent_qualified_signoff'}
        need(set(register['review_requirements']) == required, 'review_requirement_coverage')
    else:
        need(False, 'review_requirement_coverage')
    return {'integrity': 'FAIL' if failures else 'PASS', 'release': STATE,
            'eligible': False, 'source_count': len(SOURCE_POLICY),
            'conflict_count': len(CONFLICT_POLICY), 'failures': sorted(set(failures))}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-docket', required=True, type=Path)
    parser.add_argument('--scope-registry', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = inspect(args.original_docket.read_bytes(), args.scope_registry.read_bytes())
    except (OSError, ValueError) as exc:
        result = {'integrity': 'FAIL', 'release': STATE,
                  'eligible': False, 'failures': ['missing_or_invalid_input:' + type(exc).__name__]}
    print(json.dumps(result, sort_keys=True))
    return 2  # Required review remains a hard hold even when integrity is PASS.


if __name__ == '__main__':
    raise SystemExit(main())
