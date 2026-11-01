#!/usr/bin/env python3
"""R33: lossless citation-occurrence triage for human Preparedness review.

This is a deterministic, read-only work *order*. Keyword matches never establish
factual accuracy, human link verification, clinical safety or publication approval.
Each citation remains a separate claim-review task, even across repeated URLs.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import re

COUNTS = ('articles', 'tools', 'citations', 'relationships',
          'base_fallback_relationships', 'shared_url_groups_unreviewed')
EXPECTED = (35, 1, 1959, 367, 43, 30)
HEX = re.compile(r'[0-9a-f]{64}\Z')
# Deliberately broad, recall-oriented *triage* terms: false positives remain
# human-review tasks; the absence of a term never means a claim is safe.
TOPICS = {
    'water-and-chemicals': (r'\b(?:boil|boiling|bleach|chlorin\w*|disinfect\w*|'
                            r'filter\w*|purif\w*|contamin\w*|chemical\w*|'
                            r'water\s+advis\w*|cistern|drinking\s+water)\b'),
    'food-and-preservation': (r'\b(?:canner|canning|botulis\w*|jerky|dehydrat\w*|'
                              r'ferment\w*|refrigerat\w*|freez\w*|'
                              r'food\s+safety|meat|brin\w*|curing|pickle\w*)\b'),
    'fire-and-combustion': (r'\b(?:generator|carbon\s+monoxide|charcoal|grill|'
                            r'propane|fire\s+escape|smoke\s+alarm|'
                            r'fuel|evacuat\w*|ventilat\w*|flame|combust\w*)\b'),
    'medical-and-dependencies': (r'\b(?:medicat\w*|prescri\w*|pharmacist|'
                                 r'insulin|oxygen|dialys\w*|medical\s+device|'
                                 r'injur\w*|first\s+aid|poison\w*|wound|'
                                 r'epipen|defibrillat\w*|temperature-sensitive)\b'),
    'children-and-access': (r'\b(?:infant\w*|babies|baby|formula|'
                            r'pregnan\w*|disabilit\w*|wheelchair|'
                            r'caregiver|mobility\s+device|older\s+adult\w*)\b'),
}
PATTERNS = {name: re.compile(expr, re.I) for name, expr in TOPICS.items()}


class PriorityHold(ValueError):
    """The unapproved review work order cannot be proven complete."""


def demand(condition, message):
    if not condition:
        raise PriorityHold(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _valid_fingerprint(obj):
    demand(type(obj) is dict and type(obj.get('fingerprint_sha256')) is str
           and HEX.fullmatch(obj['fingerprint_sha256']) is not None,
           'missing evidence fingerprint')
    supplied = obj['fingerprint_sha256']
    demand(digest({k: v for k, v in obj.items() if k != 'fingerprint_sha256'}) == supplied,
           'evidence fingerprint mismatch')
    return supplied


def build_priority_queue(packet, index, *, expected=EXPECTED):
    """Return a fingerprinted 1:1 occurrence queue; never modify inputs.

    Call only after R25's source identity and R31's human-review index gate.
    Both parent fingerprints are rechecked here. Tests can provide a reduced
    synthetic corpus through `expected`; production uses frozen EXPECTED.
    """
    demand(type(expected) is tuple and len(expected) == 6
           and all(type(n) is int and n >= 0 for n in expected),
           'invalid frozen corpus counts')
    parent_sha, index_sha = _valid_fingerprint(packet), _valid_fingerprint(index)
    demand(packet.get('issue') == index.get('issue') == 136 and
           packet.get('schema_version') == index.get('schema_version') == 1 and
           packet.get('release_state') == index.get('release_state') == 'HOLD' and
           packet.get('may_publish') is False and index.get('may_publish') is False and
           packet.get('machine_authority') == 'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY' and
           index.get('machine_authority') == 'DETERMINISTIC_HUMAN_REVIEW_WORK_INDEX_ONLY',
           'review packet claims unsupported authority')
    for key in ('independent_QD_approval', 'qualified_safety_clearance',
                'human_source_reviews_completed', 'source_claim_accuracy_verified'):
        demand(packet.get(key) is False and index.get(key) is False,
               'fabricated human or emergency safety approval')
    demand(index.get('parent_R25_fingerprint_sha256') == parent_sha,
           'R31 review index belongs to a different claim packet')
    expected_map = dict(zip(COUNTS, expected))
    demand(packet.get('counts') == index.get('counts') == expected_map,
           'review totals differ from frozen corpus')
    rows = packet.get('review_queue')
    cards = index.get('article_review_cards')
    demand(type(rows) is list and len(rows) == expected[3] and
           type(cards) is list and len(cards) == expected[0] + expected[1],
           'article/source relationship or article card loss')
    card_map = {}
    for card in cards:
        demand(type(card) is dict and type(card.get('slug')) is str and
               card.get('review_state') == 'UNREVIEWED' and
               card['slug'] not in card_map,
               'duplicate article or fabricated completion in R31 card')
        card_map[card['slug']] = card
    tasks, seen = [], set()
    related, fallbacks = Counter(), 0
    for row in rows:
        demand(type(row) is dict, 'invalid source/claim relationship')
        slug, source_id = row.get('slug'), row.get('source_id')
        demand(type(slug) is str and slug in card_map and
               type(source_id) is str and bool(source_id),
               'unknown article or source identity')
        card = card_map[slug]
        demand(card.get('article_html_sha256') == row.get('frozen_article_html_sha256') and
               card.get('contributor_origin') == row.get('article_origin'),
               'original article custody differs from review card')
        for key in ('frozen_article_html_sha256', 'frozen_source_use_sha256',
                    'original_source_record_sha256'):
            demand(type(row.get(key)) is str and HEX.fullmatch(row[key]) is not None,
                   'missing original source/body identity: ' + key)
        offsets = row.get('citation_token_codepoint_offsets')
        contexts = row.get('all_citation_contexts_for_human_claim_review')
        n = row.get('citation_occurrences')
        demand(type(n) is int and n > 0 and type(offsets) is list and
               type(contexts) is list and len(offsets) == len(contexts) == n and
               offsets == sorted(set(offsets)),
               'claim offsets/contexts are incomplete')
        demand(type(row.get('base_fallback_requires_human_scope_review')) is bool and
               type(row.get('shared_url_group_requires_human_review')) is bool and
               row.get('human_claim_reviewed_by_this_gate') is False and
               row.get('human_link_checked_by_this_gate') is False,
               'invalid unresolved source flags')
        related[slug] += 1
        fallbacks += int(row['base_fallback_requires_human_scope_review'])
        for offset, context in zip(offsets, contexts):
            demand(type(offset) is int and offset >= 0 and
                   type(context) is str and context.count('[CITATION]') == 1,
                   'invalid citation context or position')
            key = (slug, offset)
            demand(key not in seen, 'citation offset assigned twice')
            seen.add(key)
            topics = sorted(name for name, pattern in PATTERNS.items()
                            if pattern.search(context))
            if row['base_fallback_requires_human_scope_review']:
                topics.append('cross-cluster-source-fallback')
            if row['shared_url_group_requires_human_review']:
                topics.append('shared-url-different-reading-scopes')
            topics.sort()
            # Review-first is a workflow *priority*, never a safety finding.
            priority = 'REVIEW_FIRST' if topics else 'STANDARD_REVIEW'
            ref = {
                'slug': slug,
                'source_id': source_id,
                'citation_codepoint_offset': offset,
                'original_article_html_sha256': row['frozen_article_html_sha256'],
                'original_source_record_sha256': row['original_source_record_sha256'],
                'original_source_use_sha256': row['frozen_source_use_sha256'],
                'citation_context_sha256': hashlib.sha256(context.encode('utf-8')).hexdigest(),
            }
            tasks.append({
                'claim_ref': ref,
                'claim_ref_sha256': digest(ref),
                'citation_context_for_human_review': context,
                'source_url': row.get('source_url'),
                'source_origin': row.get('source_origin'),
                'article_origin': row.get('article_origin'),
                'priority': priority,
                'triage_tags_not_safety_findings': topics,
                'review_state': 'PENDING_INDEPENDENT_CLAIM_AND_SAFETY_REVIEW',
            })
    demand(len(tasks) == expected[2] and len(seen) == expected[2] and
           len(related) == expected[0] + expected[1] and
           sum(related.values()) == expected[3] and fallbacks == expected[4],
           'citation or fallback coverage drift')
    for slug, card in card_map.items():
        demand(related[slug] == card.get('relationships') and
               sum(t['claim_ref']['slug'] == slug for t in tasks) == card.get('citations'),
               'article-level source/citation parity drift')
    tasks.sort(key=lambda t: (0 if t['priority'] == 'REVIEW_FIRST' else 1,
                              t['claim_ref']['slug'],
                              t['claim_ref']['citation_codepoint_offset'],
                              t['claim_ref']['source_id']))
    totals = Counter(t['priority'] for t in tasks)
    result = {
        'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
        'may_publish': False, 'independent_QD_approval': False,
        'qualified_safety_clearance': False, 'source_claim_accuracy_verified': False,
        'human_source_reviews_completed': False,
        'machine_authority': 'LOSSLESS_REVIEW_PRIORITIZATION_NOT_SAFETY_APPROVAL',
        'parent_R25_fingerprint_sha256': parent_sha,
        'parent_R31_fingerprint_sha256': index_sha,
        'counts': expected_map,
        'priority_counts': dict(sorted(totals.items())),
        'review_tasks': tasks,
        'limitations': 'Every occurrence requires a human claim-to-source check. Keywords identify review priority, not safety, factual accuracy, link accessibility or source scope. Historical descriptions require separate present-day safety evaluation.'
    }
    result['fingerprint_sha256'] = digest(result)
    return result
