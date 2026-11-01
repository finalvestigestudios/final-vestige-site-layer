#!/usr/bin/env python3
"""R35: deterministic, evidence-bound human-review *intake*, never approval.

This read-only private handoff converts the signed R34 reading packet into 1:1
source-scope, claim-occurrence and base-fallback tasks. It does NOT contact
external sources, accept reviewed responses, grant QD/medical approval, or
publish/modify WordPress content. The underlying original reading-depth and
article-specific source-use evidence must be retained without URL collapsing.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

EXPECTED = (35, 1, 1959, 367, 43, 30)
COUNT_KEYS = ('articles', 'tools', 'citations', 'relationships',
              'base_fallback_relationships', 'shared_url_groups_unreviewed')
HEX = re.compile(r'[0-9a-f]{64}\Z')
AUTHORITY = 'SOURCE_AND_CLAIM_HUMAN_REVIEW_INTAKE_NOT_APPROVAL'
PENDING = 'PENDING_INDEPENDENT_CLAIM_AND_SAFETY_REVIEW'
HOLD_FLAGS = ('may_publish', 'independent_QD_approval', 'qualified_safety_clearance',
              'human_source_reviews_completed', 'source_claim_accuracy_verified')


class HandoffHold(ValueError):
    """A non-approving review-intake provenance/census invariant failed."""


def need(condition, message):
    if not condition:
        raise HandoffHold(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def text_digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def is_digest(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def validate_hold(doc, authority):
    need(type(doc) is dict and doc.get('schema_version') == 1 and doc.get('issue') == 136
         and doc.get('release_state') == 'HOLD'
         and doc.get('machine_authority') == authority,
         'wrong review document schema/authority/release')
    for flag in HOLD_FLAGS:
        need(doc.get(flag) is False, 'human, safety, QD or publishing flag cannot pass: '+flag)
    fp = doc.get('fingerprint_sha256')
    need(is_digest(fp) and fp == digest({k:v for k,v in doc.items()
                                         if k != 'fingerprint_sha256'}),
         'changed or missing review document fingerprint')
    return fp


def make_handoff(reading_batches, *, expected=EXPECTED):
    """Reconcile complete R34 evidence into independent, blank reviewer tasks.

    Expected counts are frozen in production and overrideable solely by synthetic
    fixtures. Inputs are never mutated. No real-world source can pass review by
    satisfying this deterministic integrity gate.
    """
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(x) is int and x >= 0 for x in expected), 'invalid frozen totals')
    rfp = validate_hold(reading_batches, 'LOSSLESS_HUMAN_REVIEW_BATCHES_NOT_APPROVAL')
    need(reading_batches.get('counts') == dict(zip(COUNT_KEYS, expected)),
         'R34 corpus counts drift')
    need(all(is_digest(reading_batches.get(k)) for k in
             ('parent_R25_fingerprint_sha256', 'parent_R33_fingerprint_sha256')),
         'missing original evidence parents')
    size = reading_batches.get('batch_size')
    need(type(size) is int and 1 <= size <= 50, 'invalid reviewer batching policy')
    cards, batches, shared = (reading_batches.get(k) for k in
                              ('relationship_review_cards', 'review_batches',
                               'shared_url_coordination_only'))
    need(type(cards) is list and len(cards) == expected[3] and
         type(batches) is list and type(shared) is list,
         'relationship, batch or shared URL evidence missing')
    source_forms, claim_forms, fallback_forms = [], [], []
    relationship_ids, claim_ids, relationship_pairs = set(), set(), set()
    shared_expected = defaultdict(list)
    priority_counts = Counter()
    for card in cards:
        need(type(card) is dict and card.get('review_state') == 'UNREVIEWED',
             'source relationship has unapproved or malformed review state')
        cid = card.get('relationship_id_sha256')
        slug, sid = card.get('slug'), card.get('source_id')
        origin, source_origin = card.get('article_origin'), card.get('source_origin')
        record = card.get('original_source_record_as_selected')
        source_use = card.get('full_original_article_source_use')
        url = card.get('source_url')
        need(is_digest(cid) and cid not in relationship_ids and
             type(slug) is str and bool(slug) and type(sid) is str and bool(sid) and
             (slug, sid) not in relationship_pairs,
             'duplicate, missing or invalid source relationship identity')
        need(type(origin) is str and bool(origin) and type(source_origin) is str
             and bool(source_origin), 'missing original contributor origins')
        need(type(record) is dict and record.get('id') == sid and
             record.get('_origin') == source_origin and record.get('url') == url
             and type(url) is str and url.startswith('https://') and
             type(record.get('supports')) is str and bool(record['supports'].strip()) and
             type(source_use) is str and bool(source_use.strip()),
             'full original source record, URL or reading scope missing')
        need(type(card.get('base_fallback_requires_human_scope_review')) is bool and
             type(card.get('shared_url_group_requires_human_review')) is bool,
             'original unresolved source-review flags missing')
        need(card['base_fallback_requires_human_scope_review'] == (origin != source_origin),
             'base/contributor source fallback identity drift')
        citations = card.get('citation_review_items')
        need(type(citations) is list and len(citations) > 0,
             'empty or absent claim-occurrence evidence for source relationship')
        record_hash = digest(record)
        use_hash = text_digest(source_use)
        body_hashes = set()
        offsets = set()
        card_priority = 'STANDARD_REVIEW'
        for entry in citations:
            need(type(entry) is dict and entry.get('review_state') == PENDING,
                 'citation task cannot be marked reviewed')
            ref = entry.get('claim_ref')
            need(type(ref) is dict and entry.get('claim_ref_sha256') == digest(ref),
                 'citation occurrence not bound to original ref')
            rfp_claim = entry['claim_ref_sha256']
            need(is_digest(rfp_claim) and rfp_claim not in claim_ids,
                 'duplicate or invalid citation identity')
            offset = ref.get('citation_codepoint_offset')
            need(type(offset) is int and offset >= 0 and offset not in offsets,
                 'invalid or duplicated source-specific citation position')
            need(ref.get('slug') == slug and ref.get('source_id') == sid and
                 ref.get('original_source_record_sha256') == record_hash and
                 ref.get('original_source_use_sha256') == use_hash and
                 is_digest(ref.get('original_article_html_sha256')),
                 'citation detached from full original contributor source/reading')
            context = entry.get('original_context')
            need(type(context) is str and context.count('[CITATION]') == 1 and
                 ref.get('citation_context_sha256') == text_digest(context),
                 'missing or changed exact original claim context')
            tags, priority = entry.get('triage_tags_not_safety_findings'), entry.get('priority')
            need(type(tags) is list and all(type(t) is str and bool(t) for t in tags) and
                 priority in ('REVIEW_FIRST', 'STANDARD_REVIEW'),
                 'automated triage is not a clinical or editorial verdict')
            offsets.add(offset)
            body_hashes.add(ref['original_article_html_sha256'])
            claim_ids.add(rfp_claim)
            priority_counts[priority] += 1
            if priority == 'REVIEW_FIRST':
                card_priority = 'REVIEW_FIRST'
            claim_forms.append({
                'review_case_id_sha256': digest({'relationship_id_sha256': cid,
                                                 'claim_ref_sha256': rfp_claim}),
                'relationship_id_sha256': cid,
                'claim_ref_sha256': rfp_claim,
                'slug': slug, 'source_id': sid,
                'original_codepoint_offset': offset,
                'exact_original_context': context,
                'source_url': url,
                'triage_priority_not_verdict': priority,
                'triage_tags_not_safety_findings': list(tags),
                'review_state': 'NOT_STARTED',
                'human_source_access_date': None,
                'human_exact_page_or_section_locator': None,
                'human_claim_to_source_support_assessment': None,
                'human_risk_or_scope_notes': None,
                'independent_qualified_safety_review': None})
        need(len(body_hashes) == 1 and card.get('priority') == card_priority,
             'mismatched article body custody or review priority')
        expected_id = digest({'slug': slug, 'source_id': sid, 'record': record_hash,
                              'source_use': use_hash, 'body': next(iter(body_hashes))})
        need(cid == expected_id, 'source relationship ID inconsistent with frozen evidence')
        relationship_ids.add(cid)
        relationship_pairs.add((slug, sid))
        source_forms.append({
            'source_case_id_sha256': digest({'relationship_id_sha256': cid,
                                             'review_type': 'ORIGINAL_SOURCE_READING_SCOPE'}),
            'relationship_id_sha256': cid,
            'slug': slug, 'source_id': sid,
            'article_origin': origin, 'source_origin': source_origin,
            'source_url': url,
            'unabridged_original_source_record': json.loads(canonical(record)),
            'unabridged_article_specific_source_use': source_use,
            'source_record_sha256': record_hash,
            'source_use_sha256': use_hash,
            'source_impact_claim_occurrences': len(citations),
            'review_state': 'NOT_STARTED',
            'human_link_access_date': None,
            'human_source_reading_scope_assessment': None,
            'human_publisher_authority_assessment': None,
            'human_discrepancy_or_correction_notes': None})
        if card['base_fallback_requires_human_scope_review']:
            fallback_forms.append({
                'fallback_case_id_sha256': digest({'relationship_id_sha256': cid,
                    'review_type': 'ORIGINAL_CROSS_CLUSTER_FALLBACK_SCOPE'}),
                'relationship_id_sha256': cid,
                'article_origin': origin,
                'original_source_origin': source_origin,
                'source_url': url,
                'review_state': 'NOT_STARTED',
                'human_original_reading_scope_matches_article_use': None,
                'human_provenance_exception_notes': None})
        if card['shared_url_group_requires_human_review']:
            shared_expected[url].append(cid)
    need(len(source_forms) == expected[3] and len(claim_forms) == expected[2] and
         len(fallback_forms) == expected[4],
         'dropped or invented claim/source/fallback review tasks')
    # Verify R34 really partitions every relationship into its original batches.
    observed = []
    for number, batch in enumerate(batches, start=1):
        need(type(batch) is dict and batch.get('batch_number') == number and
             batch.get('review_state') == 'UNREVIEWED',
             'changed reviewer batch state or sequence')
        ids = batch.get('relationship_ids')
        expected_ids = [c['relationship_id_sha256'] for c in cards[(number-1)*size:number*size]]
        need(type(ids) is list and ids == expected_ids and
             batch.get('batch_id_sha256') == digest(ids) and
             batch.get('citation_occurrences') == sum(len(c['citation_review_items'])
                                                      for c in cards[(number-1)*size:number*size]),
             'changed reviewer batch grouping, digest or citation total')
        observed.extend(ids)
    need(len(batches) == (len(cards) + size - 1)//size and
         len(observed) == len(relationship_ids) and set(observed) == relationship_ids,
         'missing, duplicated or orphaned review batch relationship')
    observed_shared = {}
    for track in shared:
        need(type(track) is dict and track.get('review_state') == 'UNREVIEWED',
             'shared URL not independently unresolved')
        url, ids = track.get('url'), track.get('distinct_relationship_ids')
        need(type(url) is str and type(ids) is list and url not in observed_shared and
             all(is_digest(s) for s in ids) and ids == sorted(set(ids)),
             'duplicate/invalid global shared URL coordination track')
        observed_shared[url] = ids
    need(observed_shared == {url: sorted(ids) for url,ids in shared_expected.items()},
         'shared URL human-review coordination silently lost/merged')
    # Source and URL review grouping is intentionally NOT equivalence of reading scopes.
    source_forms.sort(key=lambda x:x['relationship_id_sha256'])
    claim_forms.sort(key=lambda x:(x['relationship_id_sha256'],x['original_codepoint_offset']))
    fallback_forms.sort(key=lambda x:x['relationship_id_sha256'])
    shared_forms = [{'source_url': url, 'independent_relationship_ids': list(ids),
                     'review_state': 'NOT_STARTED',
                     'human_separate_reading_scopes_reconciled': None,
                     'human_discrepancy_or_exception_notes': None}
                    for url,ids in sorted(observed_shared.items())]
    result = {
        'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
        'machine_authority': AUTHORITY,
        **{flag: False for flag in HOLD_FLAGS},
        'parent_R34_fingerprint_sha256': rfp,
        'parent_R25_fingerprint_sha256': reading_batches['parent_R25_fingerprint_sha256'],
        'parent_R33_fingerprint_sha256': reading_batches['parent_R33_fingerprint_sha256'],
        'counts': dict(zip(COUNT_KEYS, expected)),
        'review_task_counts': {
            'source_scope_items_unreviewed': len(source_forms),
            'claim_occurrences_unreviewed': len(claim_forms),
            'fallback_scope_items_unreviewed': len(fallback_forms),
            'global_shared_url_groups_unreviewed': expected[5],
            'shared_url_tracks_in_used_source_relationships_unreviewed': len(shared_forms),
            'review_first_claims_unreviewed': priority_counts['REVIEW_FIRST'],
            'standard_claims_unreviewed': priority_counts['STANDARD_REVIEW']},
        'source_scope_review_forms': source_forms,
        'claim_occurrence_review_forms': claim_forms,
        'base_fallback_review_forms': fallback_forms,
        'shared_url_review_forms_for_used_sources_only': shared_forms,
        'global_uncited_shared_url_groups':
            'Not reconstructable from R34 cited-only work cards. The frozen '
            '30-group global source inventory remains independently unreviewed.',
        'limits': 'Machine verifies task custody only. Blank forms are NOT human reviews; '
                  'no source was visited, no claim accuracy or medical safety was '
                  'assessed, and no QD or publishing approval is granted.'}
    result['fingerprint_sha256'] = digest(result)
    return result


def main(argv=None):
    """Private stdout-only dry-run. Never creates review files or CMS objects."""
    import argparse
    import importlib.util
    import sys
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--format', choices=('summary','json','ndjson'), default='summary')
    a = p.parse_args(argv)
    try:
        other = Path(__file__).with_name('citation_fallback_review_gate.py')
        need(other.is_file() and not other.is_symlink(), 'original evidence source missing')
        spec = importlib.util.spec_from_file_location('preparedness_r35_source', other)
        need(spec is not None and spec.loader is not None, 'original evidence source cannot load')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Stage-13 audit already invokes R34; run once and export a fresh R34 handoff.
        r25 = module.audit_checkout(a.repo_root)
        r31 = module.build_review_index(r25)
        r33 = module.build_priority_queue(r25, r31)
        r34 = module.build_source_reading_batches(r25, r33)
        handoff = make_handoff(r34)
        if a.format == 'json':
            print(json.dumps(handoff, ensure_ascii=False, sort_keys=True))
        elif a.format == 'ndjson':
            for key in ('source_scope_review_forms', 'claim_occurrence_review_forms',
                        'base_fallback_review_forms',
                        'shared_url_review_forms_for_used_sources_only'):
                for form in handoff[key]:
                    print(json.dumps({'form_type': key, 'form': form},
                                     ensure_ascii=False, sort_keys=True))
        else:
            print(json.dumps({key: handoff[key] for key in
                             ('schema_version','issue','release_state','machine_authority',
                              'may_publish','counts','review_task_counts',
                              'parent_R34_fingerprint_sha256',
                              'fingerprint_sha256','limits')},
                             ensure_ascii=False, sort_keys=True))
        return 0
    except (HandoffHold, OSError, ValueError, TypeError, KeyError) as exc:
        print('Preparedness R35 human review intake HOLD: '+str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
