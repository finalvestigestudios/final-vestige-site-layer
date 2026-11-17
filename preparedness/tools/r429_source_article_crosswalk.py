#!/usr/bin/env python3
"""R429: deterministic source-ID -> article and exact-URL review escrow, Issue #136.

Never selects one of the seven Claude / two Shelter branch candidates, never
merges duplicated source IDs sharing a URL, and never certifies medical/safety,
commercial, or publishing approval. Inputs are reviewer-supplied original R397
Git-pinned docket and private R410-style 35-article citation manifest.

This is a *supplement* to R425, not a replacement for its 70 authentic paired
export/candidate/body checks. Always exit 2 (DRAFT_HARD_HOLD) even if the
source-reference graph is structurally coherent.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
_spec = spec_from_file_location('r409_source_equivalence_gate', HERE / 'r409_source_equivalence_gate.py')
if _spec is None or _spec.loader is None:
    raise RuntimeError('R409 is a required local dependency')
r409 = module_from_spec(_spec)
_spec.loader.exec_module(r409)
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def held(errors, *, crosswalk=None, groups=None, aliases=None, source_count=0,
         referenced=0, manifest_hash=None, original_hash=None, review_sha=None):
    """Keep structural checks, editorial approvals, and sales strictly separate."""
    return {
        'schema': 1, 'issue': 136, 'parent_conversion_issue': 820,
        'release_state': 'DRAFT_HARD_HOLD', 'eligible': False,
        'publication_approved': False, 'qualified_safety_approved': False,
        'paid_activation_approved': False, 'merchant_offer_verified': False,
        'verified_paid_orders': None, 'net_revenue_per_1000_qualified_humans': None,
        'source_reference_structure_ok': not bool(errors),
        'errors': sorted(set(errors)),
        'article_source_crosswalk': crosswalk or [],
        'exact_shared_url_review_groups': groups or [],
        'potential_normalized_url_aliases': aliases or [],
        'source_ids_in_original': source_count,
        'source_ids_referenced_by_articles': referenced,
        'source_ids_unreferenced_by_this_manifest': source_count - referenced if source_count >= referenced else None,
        'original_git_blob': original_hash,
        'manifest_sha256': manifest_hash,
        'review_crosswalk_sha256': review_sha,
        'reading_depth': 'NOT_TESTED_BY_R429',
        'paired_exports': 'NOT_TESTED_BY_R429',
        'qualified_claim_to_citation_truth': 'HUMAN_REVIEW_REQUIRED',
        'outstanding_original_source_disputes': 5,
        'outstanding_unselected_manuscript_forks': 9,
        'source_url_equivalence': 'NO_AUTOMATIC_MERGE',
        'conversion_evidence': 'NOT_AUTHENTICATED',
        'holds': [
            'Five source applicability disputes and nine original forks remain unselected',
            'Reading depth and original/candidate/70 export bytes require native R425 review',
            'Qualified emergency/food/child-privacy/QD approvals not granted',
            'No independently authenticated paid Preparedness SKU or settled revenue',
        ],
    }


def crosswalk_audit(original, manifest, *, raw_original=None, raw_manifest=None, test_only=False):
    """Build a closed, ordered, non-merging reviewer graph from exact source IDs."""
    errors = []
    if not isinstance(original, dict) or not isinstance(manifest, dict):
        return held(['R429_INPUTS_NOT_OBJECTS'])
    try:
        inherited = r409.audit(original, require_pin=not test_only, raw=raw_original)
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError) as exc:
        return held(['R429_INHERITED_R409_EXCEPTION_' + type(exc).__name__])
    if not inherited.get('integrity_ok'):
        errors.append('R429_ORIGINAL_R397_GRAPH_OR_GIT_PIN_FAILED')
    if raw_manifest is None or not isinstance(raw_manifest, bytes):
        errors.append('R429_MANIFEST_RAW_BYTES_MISSING')
        manifest_hash = None
    else:
        manifest_hash = hashlib.sha256(raw_manifest).hexdigest()
        try:
            reread = json.loads(raw_manifest.decode('utf-8'), object_pairs_hook=r409.unique_pairs,
                                parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            if reread != manifest:
                errors.append('R429_MANIFEST_OBJECT_NOT_MATCHING_READ_BYTES')
        except (ValueError, UnicodeError, TypeError):
            errors.append('R429_MANIFEST_JSON_READ_OR_DUPLICATE_KEY_FAILED')
    if set(manifest) != {'schema', 'release_state', 'approved', 'articles'} or \
       type(manifest.get('schema')) is not int or manifest.get('schema') != 1 or \
       manifest.get('release_state') != 'DRAFT_HARD_HOLD' or manifest.get('approved') is not False:
        errors.append('R429_MANIFEST_SCHEMA_OR_RELEASE_DRIFT')
    entries = manifest.get('articles')
    originals = original.get('original_articles')
    id_rows = original.get('all_original_source_id_crosswalk')
    declared_groups = original.get('shared_exact_url_review_groups')
    if not all(isinstance(v, list) for v in (entries, originals, id_rows, declared_groups)):
        return held(errors + ['R429_MISSING_GRAPH_ARRAYS'], manifest_hash=manifest_hash)
    if len(entries) != 35 or len(originals) != 35 or len(id_rows) != 203 or len(declared_groups) != 17:
        errors.append('R429_CANONICAL_35_203_17_COVERAGE_CHANGED')
    original_slugs = [x.get('slug') for x in originals if isinstance(x, dict)]
    manifest_slugs = [x.get('slug') for x in entries if isinstance(x, dict)]
    if (len(original_slugs) != 35 or len(manifest_slugs) != 35 or
        not all(isinstance(x, str) and SLUG.fullmatch(x) for x in original_slugs + manifest_slugs) or
        len(set(original_slugs)) != 35 or len(set(manifest_slugs)) != 35 or
        set(original_slugs) != set(manifest_slugs)):
        errors.append('R429_ARTICLE_SLUG_LOSS_COLLISION_OR_ADDITION')
    id_map = {}
    url_ids = defaultdict(set)
    normalized = defaultdict(set)
    for row in id_rows:
        if not isinstance(row, dict):
            errors.append('R429_SOURCE_ROW_NOT_OBJECT'); continue
        sid = row.get('source_id')
        if not isinstance(sid, str) or not SLUG.fullmatch(sid) or sid in id_map:
            errors.append('R429_INVALID_OR_DUPLICATED_SOURCE_ID'); continue
        variants = row.get('variants')
        if not isinstance(variants, list) or not variants:
            errors.append('R429_SOURCE_VARIANTS_MISSING_' + sid); continue
        urls = set()
        for variant in variants:
            if not isinstance(variant, dict) or not isinstance(variant.get('url'), str):
                errors.append('R429_SOURCE_URL_NOT_TEXT_' + sid); continue
            url = variant['url']
            try:
                canonical = r409.checked_url(url)
            except (ValueError, TypeError):
                errors.append('R429_INVALID_SOURCE_URL_' + sid); continue
            urls.add(url)
            normalized[canonical].add(url)
        if len(urls) != 1:
            errors.append('R429_UNADJUDICATED_SOURCE_URL_VARIANTS_' + sid)
        if urls:
            url = sorted(urls)[0]
            url_ids[url].add(sid)
            id_map[sid] = url
    by_slug = {}
    source_usage = defaultdict(list)
    for row in entries:
        if not isinstance(row, dict):
            errors.append('R429_ARTICLE_MANIFEST_ROW_NOT_OBJECT'); continue
        slug = row.get('slug')
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            errors.append('R429_ARTICLE_MANIFEST_SLUG_INVALID'); continue
        if slug in by_slug:
            errors.append('R429_ARTICLE_MANIFEST_DUPLICATE_SLUG_' + slug); continue
        if set(row) != {'slug', 'canonical_path', 'sources'}:
            errors.append('R429_EXTRA_MANIFEST_FIELDS_OR_APPROVAL_'+slug)
        route = row.get('canonical_path')
        if route != f'/preparedness/{slug}/':
            errors.append('R429_CANONICAL_ARTICLE_ROUTE_MISMATCH_'+slug)
        sids = row.get('sources')
        if not isinstance(sids, list) or not sids or not all(isinstance(s, str) and SLUG.fullmatch(s) for s in sids):
            errors.append('R429_ARTICLE_SOURCE_ID_LIST_INVALID_'+slug)
            continue
        if len(sids) != len(set(sids)):
            errors.append('R429_ARTICLE_SOURCE_ID_DUPLICATED_'+slug)
        for sid in sids:
            if sid not in id_map:
                errors.append('R429_UNKNOWN_OR_UNRESOLVED_SOURCE_ID_'+slug)
            else:
                source_usage[sid].append(slug)
        by_slug[slug] = sids
    if set(by_slug) != set(original_slugs):
        errors.append('R429_ARTICLE_SOURCE_GRAPH_INCOMPLETE')
    derived = {url: sorted(sids) for url, sids in url_ids.items() if len(sids) > 1}
    declared = {}
    for row in declared_groups:
        if not isinstance(row, dict) or not isinstance(row.get('url'), str):
            errors.append('R429_SHARED_URL_ROW_INVALID'); continue
        url = row['url']
        if url in declared or row.get('review_required') is not True or not isinstance(row.get('ids'), list):
            errors.append('R429_SHARED_URL_REVIEW_FLAG_OR_DUPLICATION'); continue
        declared[url] = row['ids']
    if declared != derived:
        errors.append('R429_EXACT_SHARED_URL_GROUP_MEMBERSHIP_DRIFT')
    articles = []
    for slug in sorted(by_slug):
        ids = by_slug[slug]
        articles.append({'slug': slug, 'canonical_path': f'/preparedness/{slug}/',
                         'source_ids_in_original_order': ids,
                         'sources_with_other_source_ids_on_exact_same_url': sorted(
                             sid for sid in ids if len(url_ids[id_map.get(sid,'')]) > 1),
                         'source_url_review_status': 'NOT_FACT_CHECKED',
                         'reading_depth_review': 'REQUIRED'})
    groups = []
    for url in sorted(derived):
        sids = derived[url]
        groups.append({'exact_url': url, 'distinct_source_ids': sids,
                       'affected_article_slugs': sorted({slug for sid in sids for slug in source_usage.get(sid, [])}),
                       'decision': 'HUMAN_REVIEW_REQUIRED', 'merged': False})
    aliases = []
    for canonical in sorted(normalized):
        originals_for_url = sorted(normalized[canonical])
        if len(originals_for_url) > 1:
            aliases.append({'normalized_review_key': canonical, 'distinct_original_urls': originals_for_url,
                            'decision': 'HUMAN_REVIEW_REQUIRED', 'merged': False})
    if errors:
        return held(errors, crosswalk=articles, groups=groups, aliases=aliases,
                    source_count=len(id_map), referenced=len(source_usage),
                    original_hash=r409.blob(raw_original) if isinstance(raw_original, bytes) else None,
                    manifest_hash=manifest_hash)
    material = {'original_git_blob': r409.blob(raw_original) if isinstance(raw_original, bytes) else None,
                'manifest_sha256': manifest_hash, 'articles': articles, 'groups': groups, 'aliases': aliases,
                'source_usage': {sid: sorted(source_usage[sid]) for sid in sorted(source_usage)}}
    digest = hashlib.sha256(b'FV-R429-SOURCE-CROSSWALK-HOLD\0' +
                            json.dumps(material, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()
    return held([], crosswalk=articles, groups=groups, aliases=aliases,
                source_count=len(id_map), referenced=len(source_usage),
                original_hash=material['original_git_blob'], manifest_hash=manifest_hash, review_sha=digest)


def main(argv=None):
    ap = argparse.ArgumentParser(description='R429 source/article crosswalk (ALWAYS DRAFT HARD HOLD)')
    ap.add_argument('original_docket', type=Path)
    ap.add_argument('private_manifest', type=Path)
    args = ap.parse_args(argv)
    try:
        original_raw = r409.read_original(args.original_docket)
        manifest_raw = r409.read_original(args.private_manifest)
        original = json.loads(original_raw.decode('utf-8'), object_pairs_hook=r409.unique_pairs,
                              parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        manifest = json.loads(manifest_raw.decode('utf-8'), object_pairs_hook=r409.unique_pairs,
                              parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        result = crosswalk_audit(original, manifest, raw_original=original_raw, raw_manifest=manifest_raw)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, OverflowError, AttributeError) as exc:
        result = held(['R429_ORIGINAL_SOURCE_OR_PRIVATE_MANIFEST_UNAVAILABLE_'+type(exc).__name__])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    sys.exit(main())
