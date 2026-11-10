#!/usr/bin/env python3
"""R253: join two independently pinned, draft-only source review receipts.

This is a custody/triage tool, not evidence that a source supports advice.
R235 owns raw 244-row/32-group crosswalk identity; R237 owns 35 bodies and
2,000 reader-visible cited occurrences. R253 relates them without merging
source IDs, overwriting authored prose, or granting any safety/release approval.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import re
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r253-source-context-priority-crosswalk-v1'
HOLD = 'DRAFT_HARD_HOLD'
PENDING = 'pending-human-source-and-reading-scope-review'
SEVEN = frozenset(('start', 'shelter', 'food', 'health', 'hist-field', 'hist-food', 'hist-home'))
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
# Triage terms observed in R237. Risk categorization is a reviewer queue, NOT
# an independently validated semantic hazard classification.
HIGH_CONSEQUENCE = frozenset(('water', 'boil', 'filter', 'disinfect', 'medication',
    'medical', 'oxygen', 'insulin', 'generator', 'carbon monoxide', 'refrigerat',
    'temperature', 'infant', 'canning', 'evacuat', 'smoke'))
ORIGINAL_HELD = {(7, 'cdc-find-clean-water'): 2, (20, 'start-ready-plan'): 1}
FALSE_FLAGS_R235 = ('independent_qd_pass', 'release_authorized',
                    'source_or_medical_safety_approved', 'merchant_approved')
FALSE_FLAGS_R237 = ('release_authorized', 'independent_qd_pass',
                    'source_review_approved', 'medical_safety_verified',
                    'claim_evidence_adjudicated')


def demand(condition, message):
    if not condition:
        raise ValueError('R253 HARD HOLD: ' + message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sha64(value):
    return type(value) is str and HEX64.fullmatch(value) is not None


def audit_join(sources: dict, claims: dict, roster: list) -> dict:
    """Fail-closed deterministic map: source variant -> exact cited reading context.

    Upstream receipts must already have been authenticated by the R220 pinned
    gates. Recheck safety/count semantics defensively; never claim link health.
    """
    demand(type(sources) is dict and type(claims) is dict and type(roster) is list,
           'three authenticated input structures required')
    demand(sources.get('state') == HOLD and sources.get('raw_source_rows') == 244
           and sources.get('shared_url_groups') == 32
           and sources.get('pending_human_groups') == 32,
           'R235 census, source status, or human pending groups changed')
    for key in FALSE_FLAGS_R235:
        demand(sources.get(key) is False, 'R235 independent HOLD flag ' + key)
    demand(claims.get('state') == HOLD and claims.get('article_count') == 35
           and claims.get('citation_count') == 2000
           and claims.get('original_hold_occurrences') == 3
           and claims.get('human_review_required') is True,
           'R237 claim corpus or review status changed')
    for key in FALSE_FLAGS_R237:
        demand(claims.get(key) is False, 'R237 independent HOLD flag ' + key)
    queue = sources.get('review_queue')
    articles = claims.get('articles')
    demand(type(queue) is list and len(queue) == 32, 'exactly 32 source groups required')
    demand(type(articles) is list and len(articles) == 35 and len(roster) == 35,
           'exactly 35 manuscripts required')

    source_to_group = {}
    group_by_url = {}
    for row in queue:
        demand(type(row) is dict, 'source review group must be an object')
        url = row.get('url')
        parsed = urlsplit(url) if type(url) is str else None
        demand(parsed is not None and parsed.scheme in ('https', 'http')
               and bool(parsed.hostname) and not parsed.username and not parsed.password,
               'unusable shared source review URL')
        demand(url not in group_by_url, 'repeated shared source group')
        demand(row.get('status') == PENDING and row.get('human_scope_review_required') is True,
               'shared group silently cleared')
        demand(row.get('all_human_link_checked') is False,
               'unreviewed group claims human link-check')
        demand(sha64(row.get('evidence_sha256')), 'missing group evidence identity')
        ids = row.get('source_ids')
        demand(type(ids) is list and bool(ids) and all(type(s) is str and SLUG.fullmatch(s) for s in ids)
               and len(set(ids)) == len(ids), 'invalid/duplicated group source ID')
        for sid in ids:
            demand(sid not in source_to_group, 'one source ID maps to multiple group URLs')
            source_to_group[sid] = url
        demand(type(row.get('row_count')) is int and row['row_count'] >= len(ids),
               'source variant count inconsistent')
        demand(type(row.get('scope_variants')) is int and row['scope_variants'] >= 1,
               'scope variants unavailable')
        demand(type(row.get('verification_date_variants')) is int
               and row['verification_date_variants'] >= 1, 'review date variants unavailable')
        origins = row.get('origins')
        demand(type(origins) is list and all(type(v) is str and v in SEVEN | {'base'} for v in origins),
               'invalid source origin provenance')
        group_by_url[url] = row

    seen_slugs, clusters = set(), set()
    matched_by_url = defaultdict(list)
    all_cited_ids = set()
    held_counts = Counter()
    for n, (article, original) in enumerate(zip(articles, roster), 1):
        demand(type(article) is dict and type(original) is dict and type(original.get('n')) is int
               and original['n'] == n and type(article.get('n')) is int and article['n'] == n,
               'article order / inherited contributor roster drift')
        slug = original.get('slug')
        demand(type(slug) is str and SLUG.fullmatch(slug) and article.get('slug') == slug
               and slug not in seen_slugs, 'duplicate/mismatched article or route')
        seen_slugs.add(slug)
        cluster = original.get('source_cluster')
        demand(cluster in SEVEN, 'unrecognized contributor cluster')
        clusters.add(cluster)
        demand(sha64(article.get('body_sha256')) and sha64(article.get('metadata_sha256'))
               and sha64(article.get('claim_context_receipt_sha256')),
               'missing per-manuscript claim custody')
        occurrences = article.get('occurrences')
        demand(type(occurrences) is list and type(article.get('citation_count')) is int
               and len(occurrences) == article['citation_count'],
               'missing/duplicated article citation inventory')
        for ordinal, item in enumerate(occurrences, 1):
            demand(type(item) is dict and type(item.get('ordinal')) is int
                   and item['ordinal'] == ordinal, 'missing/duplicated citation ordinal')
            sid = item.get('source_id')
            demand(type(sid) is str and SLUG.fullmatch(sid), 'unsafe/missing cited source ID')
            demand(type(item.get('offset')) is int and item['offset'] >= 0,
                   'citation location unavailable')
            demand(type(item.get('context_excerpt')) is str
                   and len(item['context_excerpt'].strip()) >= 6,
                   'reader claim context unavailable')
            demand(sha64(item.get('context_sha256')) and sha64(item.get('author_note_sha256')),
                   'claim/source-use evidence identity missing')
            demand(sha256(item['context_excerpt'].encode()).hexdigest() == item['context_sha256'],
                   'reader claim context checksum mismatch')
            demand(item.get('independent_claim_source_verified') is False,
                   'unsupported independent claim-source approval')
            risks = item.get('human_risk_review_terms')
            demand(type(risks) is list and all(type(t) is str for t in risks),
                   'invalid qualitative review terms')
            all_cited_ids.add(sid)
            if (n, sid) in ORIGINAL_HELD:
                held_counts[(n, sid)] += 1
            url = source_to_group.get(sid)
            if url is not None:
                matched_by_url[url].append({'n': n, 'article_slug': slug,
                    'contributor_cluster': cluster, 'ordinal': ordinal,
                    'source_id': sid, 'context_sha256': item['context_sha256'],
                    'author_note_sha256': item['author_note_sha256'],
                    'review_terms': sorted(set(risks))})
    demand(clusters == SEVEN, 'one or more contributor clusters not represented')
    demand(sum(a['citation_count'] for a in articles) == 2000,
           'cross-article citation inventory not 2,000')
    demand(dict(held_counts) == ORIGINAL_HELD,
           'historically unreviewed three citation occurrences not preserved')

    grouped = []
    for url in sorted(group_by_url):
        source = group_by_url[url]
        matches = sorted(matched_by_url[url], key=lambda m: (m['n'], m['ordinal']))
        hits = sorted({term for m in matches for term in m['review_terms'] if term in HIGH_CONSEQUENCE})
        priority = ('HIGH_CONSEQUENCE_REVIEW' if hits else
                    'UNMAPPED_VARIANT_REVIEW' if not matches else 'ROUTINE_SCOPE_REVIEW')
        grouped.append({'url': url, 'priority': priority,
                        'source_ids': sorted(source['source_ids']),
                        'origins': sorted(set(source['origins'])),
                        'source_scope_variants': source['scope_variants'],
                        'source_date_variants': source['verification_date_variants'],
                        'source_evidence_sha256': source['evidence_sha256'],
                        'cited_occurrence_count': len(matches),
                        'cited_article_numbers': sorted({m['n'] for m in matches}),
                        'matched_citation_evidence': matches,
                        'high_consequence_review_terms': hits,
                        'state': 'PENDING_HUMAN_SOURCE_SCOPE_AND_CLAIM_REVIEW',
                        'source_scope_approved': False, 'claim_support_approved': False})
    totals = {'groups': len(grouped),
              'high_consequence_groups': sum(r['priority'] == 'HIGH_CONSEQUENCE_REVIEW' for r in grouped),
              'unmapped_groups': sum(r['priority'] == 'UNMAPPED_VARIANT_REVIEW' for r in grouped),
              'groups_with_cited_occurrences': sum(r['cited_occurrence_count'] > 0 for r in grouped),
              'matched_occurrences': sum(r['cited_occurrence_count'] for r in grouped),
              'unmatched_occurrences': 2000 - sum(r['cited_occurrence_count'] for r in grouped),
              'distinct_cited_source_ids': len(all_cited_ids),
              'original_disputed_occurrences': 3}
    demand(totals['matched_occurrences'] <= 2000, 'citation double-counted across shared groups')
    receipt = {'schema': SCHEMA, 'state': HOLD, 'issue': 136, 'conversion_issue': 820,
               'article_count': 35, 'citation_count': 2000, 'source_rows': 244,
               'contributor_cluster_count': 7, 'totals': totals, 'review_queue': grouped,
               'human_source_scope_approved': False, 'independent_claim_reviewed': False,
               'independent_qd_pass': False, 'medical_safety_verified': False,
               'merchant_approved': False, 'publication_authorized': False}
    receipt['receipt_sha256'] = sha256(canonical(receipt).encode('utf-8')).hexdigest()
    return receipt
