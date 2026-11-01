#!/usr/bin/env python3
"""R34: read-only, lossless reviewer batches with source-reading custody.

Batching organizes human review; it grants NO claim, link, medical, QD or
publication approval. Repeated URLs never collapse contributor reading scopes.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
import re

EXPECTED = (35, 1, 1959, 367, 43, 30)
COUNT_KEYS = ('articles', 'tools', 'citations', 'relationships',
              'base_fallback_relationships', 'shared_url_groups_unreviewed')
HEX = re.compile(r'[0-9a-f]{64}\Z')
PENDING = 'PENDING_INDEPENDENT_CLAIM_AND_SAFETY_REVIEW'
AUTHORITY = 'LOSSLESS_HUMAN_REVIEW_BATCHES_NOT_APPROVAL'


class BatchHold(ValueError):
    """A source/claim custody or explicit HOLD requirement failed."""


def require(ok, message):
    if not ok:
        raise BatchHold(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def proof(obj, label):
    require(type(obj) is dict and type(obj.get('fingerprint_sha256')) is str
            and HEX.fullmatch(obj['fingerprint_sha256']) is not None,
            label + ': missing fingerprint')
    fp = obj['fingerprint_sha256']
    require(fp == sha({k: v for k, v in obj.items() if k != 'fingerprint_sha256'}),
            label + ': fingerprint mismatch')
    return fp


def _hold_contract(obj, authority):
    require(obj.get('schema_version') == 1 and obj.get('issue') == 136
            and obj.get('release_state') == 'HOLD'
            and obj.get('machine_authority') == authority
            and obj.get('may_publish') is False, 'unsupported release authority')
    for flag in ('independent_QD_approval', 'qualified_safety_clearance',
                 'human_source_reviews_completed', 'source_claim_accuracy_verified'):
        require(obj.get(flag) is False, 'unsupported human review claim: ' + flag)


def make_batch_index(packet, queue, *, expected=EXPECTED, batch_size=12):
    """One card per original source-use relationship, one item per citation.

    Production always uses EXPECTED. Reduced expected/batch_size are only for
    synthetic tests. Neither input is mutated; no external network or writes.
    """
    require(type(expected) is tuple and len(expected) == 6 and
            all(type(n) is int and n >= 0 for n in expected), 'invalid totals')
    require(type(batch_size) is int and 1 <= batch_size <= 50, 'unsafe batch size')
    pfp, qfp = proof(packet, 'R25'), proof(queue, 'R33')
    _hold_contract(packet, 'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY')
    _hold_contract(queue, 'LOSSLESS_REVIEW_PRIORITIZATION_NOT_SAFETY_APPROVAL')
    require(queue.get('parent_R25_fingerprint_sha256') == pfp,
            'R33 queue belongs to different original evidence')
    totals = dict(zip(COUNT_KEYS, expected))
    require(packet.get('counts') == totals and queue.get('counts') == totals,
            'frozen corpus totals drift')
    rows, tasks = packet.get('review_queue'), queue.get('review_tasks')
    require(type(rows) is list and len(rows) == expected[3] and
            type(tasks) is list and len(tasks) == expected[2],
            'lost source relationships or citation occurrences')
    by_coordinate, claim_ids = {}, set()
    for t in tasks:
        require(type(t) is dict and type(t.get('claim_ref')) is dict,
                'invalid citation task')
        ref = t['claim_ref']
        require(type(t.get('claim_ref_sha256')) is str and
                t['claim_ref_sha256'] == sha(ref), 'claim reference substitution')
        require(type(ref.get('slug')) is str and type(ref.get('source_id')) is str
                and type(ref.get('citation_codepoint_offset')) is int
                and ref['citation_codepoint_offset'] >= 0, 'invalid claim coordinate')
        key = (ref['slug'], ref['source_id'], ref['citation_codepoint_offset'])
        require(key not in by_coordinate and t['claim_ref_sha256'] not in claim_ids,
                'duplicate claim or offset')
        by_coordinate[key] = t
        claim_ids.add(t['claim_ref_sha256'])
        context = t.get('citation_context_for_human_review')
        require(type(context) is str and context.count('[CITATION]') == 1 and
                ref.get('citation_context_sha256') == hashlib.sha256(context.encode('utf-8')).hexdigest(),
                'citation context altered')
        require(t.get('review_state') == PENDING and
                t.get('priority') in ('REVIEW_FIRST', 'STANDARD_REVIEW') and
                type(t.get('triage_tags_not_safety_findings')) is list and
                all(type(tag) is str for tag in t['triage_tags_not_safety_findings']),
                'review task falsely completed or invalid priority')
    cards, seen_relationships, consumed, urls = [], set(), set(), defaultdict(list)
    fallback_count, cited_count = 0, 0
    for row in rows:
        require(type(row) is dict, 'invalid original relationship')
        slug, sid = row.get('slug'), row.get('source_id')
        require(type(slug) is str and bool(slug) and type(sid) is str and bool(sid),
                'missing contributor source relationship identity')
        relationship = (slug, sid)
        require(relationship not in seen_relationships, 'duplicated article/source relationship')
        seen_relationships.add(relationship)
        original = row.get('original_source_record_as_selected')
        require(type(original) is dict and type(original.get('supports')) is str
                and bool(original['supports'].strip()), 'missing full contributor reading depth')
        require(type(row.get('original_source_record_sha256')) is str and
                row['original_source_record_sha256'] == sha(original),
                'original contributor record no longer matches its digest')
        source_use = row.get('article_source_use_as_recorded')
        require(type(source_use) is str and bool(source_use.strip()) and
                row.get('frozen_source_use_sha256') == hashlib.sha256(source_use.encode('utf-8')).hexdigest(),
                'article-specific reading scope changed')
        body_hash = row.get('frozen_article_html_sha256')
        require(type(body_hash) is str and HEX.fullmatch(body_hash) is not None,
                'article custody missing')
        require(original.get('id') == sid and original.get('_origin') == row.get('source_origin')
                and original.get('url') == row.get('source_url') and
                row.get('article_origin') is not None, 'selected contributor/source identity drift')
        for flag in ('base_fallback_requires_human_scope_review',
                     'shared_url_group_requires_human_review'):
            require(type(row.get(flag)) is bool, 'invalid unresolved relationship review flag')
        require(row.get('human_claim_reviewed_by_this_gate') is False and
                row.get('human_link_checked_by_this_gate') is False,
                'fabricated source or link review')
        offsets, contexts = row.get('citation_token_codepoint_offsets'), row.get('all_citation_contexts_for_human_claim_review')
        require(type(offsets) is list and type(contexts) is list and
                len(offsets) == len(contexts) == row.get('citation_occurrences') and
                len(offsets) > 0 and all(type(o) is int and o >= 0 for o in offsets) and
                offsets == sorted(set(offsets)), 'source citation offsets changed')
        items = []
        for offset, context in zip(offsets, contexts):
            key = (slug, sid, offset)
            require(key in by_coordinate and key not in consumed, 'missing or reassigned citation')
            t, ref = by_coordinate[key], by_coordinate[key]['claim_ref']
            require(t.get('citation_context_for_human_review') == context and
                    t.get('source_url') == row['source_url'] and
                    t.get('source_origin') == row['source_origin'] and
                    t.get('article_origin') == row['article_origin'] and
                    ref.get('original_article_html_sha256') == body_hash and
                    ref.get('original_source_record_sha256') == row['original_source_record_sha256'] and
                    ref.get('original_source_use_sha256') == row['frozen_source_use_sha256'],
                    'R33 claim is not bound to original article/source/scope')
            consumed.add(key)
            items.append({'claim_ref': ref, 'claim_ref_sha256': t['claim_ref_sha256'],
                          'original_context': context, 'priority': t['priority'],
                          'triage_tags_not_safety_findings': t['triage_tags_not_safety_findings'],
                          'review_state': PENDING})
        fallback_count += int(row['base_fallback_requires_human_scope_review'])
        cited_count += len(items)
        card_id = sha({'slug': slug, 'source_id': sid, 'record': row['original_source_record_sha256'],
                       'source_use': row['frozen_source_use_sha256'], 'body': body_hash})
        card = {'relationship_id_sha256': card_id, 'slug': slug, 'source_id': sid,
                'article_origin': row['article_origin'], 'source_origin': row['source_origin'],
                'source_url': row['source_url'],
                'original_source_record_as_selected': original,
                'full_original_article_source_use': source_use,
                'base_fallback_requires_human_scope_review': row['base_fallback_requires_human_scope_review'],
                'shared_url_group_requires_human_review': row['shared_url_group_requires_human_review'],
                'priority': 'REVIEW_FIRST' if any(x['priority'] == 'REVIEW_FIRST' for x in items) else 'STANDARD_REVIEW',
                'citation_review_items': items, 'review_state': 'UNREVIEWED'}
        cards.append(card)
        if row['shared_url_group_requires_human_review']:
            urls[row['source_url']].append(card_id)
    require(len(consumed) == len(by_coordinate) == cited_count == expected[2] and
            len(cards) == expected[3] and fallback_count == expected[4],
            'source relationship or citation coverage loss')
    cards.sort(key=lambda c: (c['priority'] != 'REVIEW_FIRST', c['slug'], c['source_id']))
    batches = []
    for i in range(0, len(cards), batch_size):
        subset = cards[i:i+batch_size]
        ids = [c['relationship_id_sha256'] for c in subset]
        batches.append({'batch_number': len(batches) + 1, 'batch_id_sha256': sha(ids),
                        'relationship_ids': ids,
                        'citation_occurrences': sum(len(c['citation_review_items']) for c in subset),
                        'review_state': 'UNREVIEWED'})
    result = {'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
              'machine_authority': AUTHORITY, 'may_publish': False,
              'independent_QD_approval': False, 'qualified_safety_clearance': False,
              'human_source_reviews_completed': False, 'source_claim_accuracy_verified': False,
              'parent_R25_fingerprint_sha256': pfp, 'parent_R33_fingerprint_sha256': qfp,
              'counts': totals, 'batch_size': batch_size,
              'relationship_review_cards': cards, 'review_batches': batches,
              'shared_url_coordination_only': [{'url': u, 'distinct_relationship_ids': sorted(ids),
                  'review_state': 'UNREVIEWED'} for u, ids in sorted(urls.items())],
              'limitations': 'Machine grouping is not claim verification, link checking, medical safety review, or QD PASS. Shared URLs retain separate contributor reading depth and article source-use records.'}
    result['fingerprint_sha256'] = sha(result)
    return result


def main(argv=None):
    """Private read-only CLI. Never write output files, CMS or public content."""
    import argparse
    import importlib.util
    from pathlib import Path
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--format', choices=('summary', 'json', 'ndjson'), default='summary')
    args = parser.parse_args(argv)
    try:
        sibling = Path(__file__).with_name('citation_fallback_review_gate.py')
        require(sibling.is_file() and not sibling.is_symlink(), 'original review packet producer missing')
        spec = importlib.util.spec_from_file_location('preparedness_r34_source', sibling)
        require(spec is not None and spec.loader is not None, 'source producer unavailable')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        p = m.audit_checkout(args.repo_root)
        q = m.build_priority_queue(p, m.build_review_index(p))
        output = make_batch_index(p, q)
        if args.format == 'json':
            print(json.dumps(output, sort_keys=True, ensure_ascii=False))
        elif args.format == 'ndjson':
            for card in output['relationship_review_cards']:
                print(json.dumps(card, sort_keys=True, ensure_ascii=False))
        else:
            print(json.dumps({k: output[k] for k in ('schema_version', 'issue', 'release_state',
                 'machine_authority', 'may_publish', 'counts', 'batch_size',
                 'parent_R25_fingerprint_sha256', 'parent_R33_fingerprint_sha256',
                 'fingerprint_sha256', 'limitations')}, sort_keys=True, ensure_ascii=False))
        return 0
    except (BatchHold, OSError, KeyError, TypeError, ValueError) as exc:
        print('Preparedness R34 reviewer batch HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
