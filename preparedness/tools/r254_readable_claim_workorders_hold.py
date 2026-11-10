#!/usr/bin/env python3
"""R254: human-readable, fail-closed workorders for unresolved shared-source citations.

Consumes independently authenticated R237/R253 receipts. Neither a citation nor
an author's source-use note proves that advice is correct. Never write to CMS.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import re

SCHEMA = 'fv-preparedness-r254-readable-claim-workorders-v1'
HOLD = 'DRAFT_HARD_HOLD'
HEX = re.compile(r'[0-9a-f]{64}\Z')
HELD = ((7, 30, 'cdc-find-clean-water'),
        (7, 48, 'cdc-find-clean-water'),
        (20, 55, 'start-ready-plan'))
FALSE_CLAIMS = ('release_authorized', 'independent_qd_pass',
                'source_review_approved', 'medical_safety_verified',
                'claim_evidence_adjudicated')
FALSE_JOIN = ('human_source_scope_approved', 'independent_claim_reviewed',
              'independent_qd_pass', 'medical_safety_verified',
              'merchant_approved', 'publication_authorized')


def fail(ok, message):
    if not ok:
        raise ValueError('R254 HARD HOLD: ' + message)


def sha(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def is_hash(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def audit_readable_workorders(joined: dict, claims: dict) -> dict:
    """Expand every shared citation to its actual authored reading context.

    Enforce the independently observed 2026-11-09 35/2000/562 census. This
    is a drift alarm, not a count of source-validated or safe claims.
    """
    fail(type(joined) is dict and type(claims) is dict, 'authenticated inputs required')
    fail(joined.get('schema') == 'fv-preparedness-r253-source-context-priority-crosswalk-v1'
         and joined.get('state') == HOLD and joined.get('article_count') == 35
         and joined.get('citation_count') == 2000 and joined.get('source_rows') == 244
         and joined.get('contributor_cluster_count') == 7,
         'R253 provenance / census changed')
    fail(claims.get('state') == HOLD and claims.get('article_count') == 35
         and claims.get('citation_count') == 2000 and claims.get('original_hold_occurrences') == 3
         and claims.get('human_review_required') is True,
         'R237 frozen receipt or human review state changed')
    for flag in FALSE_CLAIMS:
        fail(claims.get(flag) is False, 'R237 approval flag changed: ' + flag)
    for flag in FALSE_JOIN:
        fail(joined.get(flag) is False, 'R253 approval flag changed: ' + flag)
    digest = joined.get('receipt_sha256')
    fail(is_hash(digest) and digest == sha(packed({k: v for k, v in joined.items()
                                                  if k != 'receipt_sha256'})),
         'R253 receipt is not self-consistent')
    totals = joined.get('totals')
    fail(type(totals) is dict and totals.get('groups') == 32
         and totals.get('matched_occurrences') == 562
         and totals.get('unmatched_occurrences') == 1438
         and totals.get('original_disputed_occurrences') == 3,
         'independently counted 32/562/1438/three HELD census drift')
    articles, groups = claims.get('articles'), joined.get('review_queue')
    fail(type(articles) is list and len(articles) == 35
         and type(groups) is list and len(groups) == 32,
         'missing article or source review group')

    indexed = {}
    all_used = Counter()
    for n, article in enumerate(articles, 1):
        fail(type(article) is dict and type(article.get('n')) is int
             and article['n'] == n and type(article.get('slug')) is str,
             'R237 article identity/order drift')
        rows = article.get('occurrences')
        fail(type(rows) is list and type(article.get('citation_count')) is int
             and len(rows) == article['citation_count'],
             'R237 citation count drift')
        fail(is_hash(article.get('body_sha256')) and is_hash(article.get('metadata_sha256')),
             'missing manuscript source identity')
        fail(is_hash(article.get('claim_context_receipt_sha256'))
             and sha(packed(rows)) == article['claim_context_receipt_sha256'],
             'R237 individual claim custody receipt mismatch')
        for ordinal, occurrence in enumerate(rows, 1):
            fail(type(occurrence) is dict and type(occurrence.get('ordinal')) is int
                 and occurrence['ordinal'] == ordinal,
                 'missing or reordered individual citation')
            excerpt = occurrence.get('context_excerpt')
            fail(type(excerpt) is str and 6 <= len(excerpt) <= 1000
                 and occurrence.get('context_sha256') == sha(excerpt)
                 and is_hash(occurrence.get('author_note_sha256')),
                 'reader excerpt or source-use witness changed')
            sid = occurrence.get('source_id')
            fail(type(sid) is str and bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', sid))
                 and occurrence.get('independent_claim_source_verified') is False,
                 'unsafe source ID or unsupported claim approval')
            terms = occurrence.get('human_risk_review_terms')
            fail(type(terms) is list and all(type(t) is str for t in terms),
                 'citation risk terms malformed')
            indexed[n, ordinal] = (article['slug'], occurrence)
            all_used[n, sid] += 1
    fail(len(indexed) == 2000 and
         all_used[7, 'cdc-find-clean-water'] == 2 and
         all_used[20, 'start-ready-plan'] == 1,
         'three inherited original holds or total citations lost')
    for n, ordinal, sid in HELD:
        fail(indexed[n, ordinal][1]['source_id'] == sid,
             'specific disputed citation ordinal shifted')

    seen_urls, shared_ids, observed = set(), set(), set()
    readable = []
    for group in groups:
        fail(type(group) is dict and type(group.get('url')) is str
             and group['url'] not in seen_urls,
             'duplicate or missing review URL')
        seen_urls.add(group['url'])
        ids = group.get('source_ids')
        fail(type(ids) is list and bool(ids) and all(type(i) is str for i in ids)
             and not (set(ids) & shared_ids), 'shared-source ID reassignment')
        shared_ids.update(ids)
        fail(group.get('state') == 'PENDING_HUMAN_SOURCE_SCOPE_AND_CLAIM_REVIEW'
             and group.get('source_scope_approved') is False
             and group.get('claim_support_approved') is False,
             'shared group review was silently cleared')
        matches = group.get('matched_citation_evidence')
        fail(type(matches) is list and type(group.get('cited_occurrence_count')) is int
             and len(matches) == group['cited_occurrence_count'],
             'lost shared-source citation references')
        work = []
        for row in matches:
            fail(type(row) is dict and type(row.get('n')) is int
                 and type(row.get('ordinal')) is int and
                 (row['n'], row['ordinal']) in indexed,
                 'foreign source citation reference')
            key = row['n'], row['ordinal']
            fail(key not in observed, 'same citation mapped to multiple source groups')
            observed.add(key)
            slug, cite = indexed[key]
            fail(row.get('article_slug') == slug and row.get('source_id') in ids
                 and row['source_id'] == cite['source_id']
                 and row.get('context_sha256') == cite['context_sha256']
                 and row.get('author_note_sha256') == cite['author_note_sha256']
                 and row.get('review_terms') == sorted(set(cite['human_risk_review_terms'])),
                 'R253 claim does not match its R237 original source witness')
            work.append({'article_n': key[0], 'article_slug': slug,
                         'citation_ordinal': key[1], 'source_id': row['source_id'],
                         'authored_context_excerpt': cite['context_excerpt'],
                         'context_sha256': cite['context_sha256'],
                         'author_source_use_note_sha256': cite['author_note_sha256'],
                         'review_terms': row['review_terms'],
                         'disputed_original_citation': (key[0], key[1], row['source_id']) in HELD,
                         'source_support_verified': False, 'safety_approved': False})
        fail(work == sorted(work, key=lambda x: (x['article_n'], x['citation_ordinal'])),
             'nondeterministic reviewer order')
        readable.append({'source_url': group['url'], 'source_ids': list(ids),
                         'priority': group.get('priority'),
                         'source_evidence_sha256': group.get('source_evidence_sha256'),
                         'workorder_count': len(work), 'workorders': work,
                         'state': 'PENDING_HUMAN_SOURCE_AND_CLAIM_REVIEW',
                         'source_scope_approved': False, 'claim_support_approved': False})
    fail(len(shared_ids) == 56 and len(observed) == 562
         and all(indexed[n, o][1]['source_id'] in shared_ids for n, o, _ in HELD)
         and len(readable) == 32,
         'frozen 56 shared IDs / 562 claim workorders drift')
    fail(all(x['disputed_original_citation'] is True for group in readable
             for x in group['workorders'] if (x['article_n'], x['citation_ordinal'], x['source_id']) in HELD),
         'disputed citation must remain visible')
    receipt = {'schema': SCHEMA, 'state': HOLD, 'issue': 136,
               'source_review_groups': 32, 'shared_source_ids': 56,
               'article_count': 35, 'citation_count': 2000,
               'human_readable_workorders': len(observed),
               'other_citation_occurrences_still_unreviewed': 1438,
               'disputed_original_claims': len(HELD), 'review_queue': readable,
               'independent_claim_source_verified': False,
               'independent_qd_pass': False, 'medical_safety_verified': False,
               'merchant_approved': False, 'publication_authorized': False}
    receipt['receipt_sha256'] = sha(packed(receipt))
    return receipt
