#!/usr/bin/env python3
"""R257: reconcile every original citation with R254's 562 shared-source workorders.

Read-only human-review evidence. No medical/source approval or WordPress writes.
This is a coverage gate, not an assertion that any cited claim is correct.
"""
from __future__ import annotations
import hashlib
import json
import re

SCHEMA = 'fv-preparedness-r257-complete-citation-partition-v1'
UPSTREAM = 'fv-preparedness-r254-readable-claim-workorders-v1'
HOLD = 'DRAFT_HARD_HOLD'
HELD = {(7, 30, 'cdc-find-clean-water'),
        (7, 48, 'cdc-find-clean-water'), (20, 55, 'start-ready-plan')}
FALSE = ('independent_claim_source_verified', 'independent_qd_pass',
         'medical_safety_verified', 'merchant_approved', 'publication_authorized')
SHA = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def require(ok, reason):
    if not ok:
        raise ValueError('R257 DRAFT HARD HOLD: ' + reason)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def valid_hash(value):
    return type(value) is str and SHA.fullmatch(value) is not None


def verify_receipt(document):
    require(type(document) is dict and valid_hash(document.get('receipt_sha256')),
            'R254 source receipt missing')
    require(document['receipt_sha256'] == digest(canonical({
        k: v for k, v in document.items() if k != 'receipt_sha256'})),
        'R254 source receipt changed')


def audit_full_partition(claims: dict, workorders: dict) -> dict:
    """Produce an independently reconcilable *unreviewed* complement of 1438 citations."""
    require(type(claims) is dict and type(workorders) is dict,
            'upstream authenticated records are required')
    verify_receipt(workorders)
    require(workorders.get('schema') == UPSTREAM and workorders.get('state') == HOLD,
            'wrong R254 upstream or cleared hold')
    expected = {'article_count': 35, 'citation_count': 2000,
                'source_review_groups': 32, 'shared_source_ids': 56,
                'human_readable_workorders': 562,
                'other_citation_occurrences_still_unreviewed': 1438,
                'disputed_original_claims': 3, 'shared_disputed_claims': 1,
                'outside_shared_disputed_claims': 2}
    for key, value in expected.items():
        require(type(workorders.get(key)) is int and workorders[key] == value,
                'R254 census drift: ' + key)
    for key in FALSE:
        require(workorders.get(key) is False, 'R254 unauthorized approval: ' + key)
    require(claims.get('state') == HOLD and claims.get('article_count') == 35
            and claims.get('citation_count') == 2000
            and claims.get('original_hold_occurrences') == 3
            and claims.get('human_review_required') is True,
            'original claim receipt census or hold drift')
    for key in ('release_authorized', 'independent_qd_pass',
                'source_review_approved', 'medical_safety_verified',
                'claim_evidence_adjudicated'):
        require(claims.get(key) is False, 'R237 unsafe approval: ' + key)

    originals, slugs = {}, set()
    articles = claims.get('articles')
    require(type(articles) is list and len(articles) == 35, '35 original articles required')
    for n, article in enumerate(articles, 1):
        require(type(article) is dict and type(article.get('n')) is int
                and article['n'] == n, 'original article order drift')
        slug = article.get('slug')
        require(type(slug) is str and SLUG.fullmatch(slug) and slug not in slugs,
                'missing/duplicate original article slug')
        slugs.add(slug)
        rows = article.get('occurrences')
        require(type(rows) is list and type(article.get('citation_count')) is int
                and len(rows) == article['citation_count'], 'article citation total drift')
        require(valid_hash(article.get('body_sha256'))
                and valid_hash(article.get('metadata_sha256')),
                'original manuscript witness missing')
        require(valid_hash(article.get('claim_context_receipt_sha256'))
                and digest(canonical(rows)) == article['claim_context_receipt_sha256'],
                'original authored contexts changed')
        for ordinal, row in enumerate(rows, 1):
            require(type(row) is dict and type(row.get('ordinal')) is int
                    and row['ordinal'] == ordinal, 'citation ordinal drift')
            sid, excerpt = row.get('source_id'), row.get('context_excerpt')
            require(type(sid) is str and SLUG.fullmatch(sid)
                    and type(excerpt) is str and 6 <= len(excerpt) <= 1000
                    and row.get('context_sha256') == digest(excerpt)
                    and valid_hash(row.get('author_note_sha256'))
                    and row.get('independent_claim_source_verified') is False,
                    'original source/author witness modified or approved')
            terms = row.get('human_risk_review_terms')
            require(type(terms) is list and all(type(t) is str and len(t) <= 100
                    for t in terms), 'original risk terms malformed')
            originals[n, ordinal] = (slug, row)
    require(len(originals) == 2000, 'original full-citation census changed')
    for n, ordinal, sid in HELD:
        require(originals[n, ordinal][1]['source_id'] == sid,
                'original disputed citation moved')

    shared = set()
    groups = workorders.get('review_queue')
    require(type(groups) is list and len(groups) == 32,
            'source-group workorders unavailable')
    for group in groups:
        require(type(group) is dict and group.get('state') ==
                'PENDING_HUMAN_SOURCE_AND_CLAIM_REVIEW'
                and group.get('source_scope_approved') is False
                and group.get('claim_support_approved') is False,
                'shared source group cleared')
        rows = group.get('workorders')
        require(type(rows) is list and group.get('workorder_count') == len(rows),
                'missing shared workorders')
        for row in rows:
            require(type(row) is dict, 'shared workorder malformed')
            key = row.get('article_n'), row.get('citation_ordinal')
            require(key in originals and key not in shared, 'unknown/duplicate shared point')
            slug, original = originals[key]
            require(row.get('article_slug') == slug
                    and row.get('source_id') == original['source_id']
                    and row.get('authored_context_excerpt') == original['context_excerpt']
                    and row.get('context_sha256') == original['context_sha256']
                    and row.get('author_source_use_note_sha256') == original['author_note_sha256']
                    and row.get('review_terms') == sorted(set(original['human_risk_review_terms']))
                    and row.get('disputed_original_citation') is
                    ((key[0], key[1], original['source_id']) in HELD)
                    and row.get('source_support_verified') is False
                    and row.get('safety_approved') is False,
                    'shared workorder differs from authored citation or cleared hold')
            shared.add(key)
    require(len(shared) == 562, 'shared coverage changed')
    complement = sorted(set(originals) - shared)
    require(len(complement) == 1438, 'nonshared coverage changed')
    external = workorders.get('outside_shared_disputed_workorders')
    require(type(external) is list and len(external) == 2,
            'outside-shared original holds missing')
    held_out = {(7, 30, 'cdc-find-clean-water'), (7, 48, 'cdc-find-clean-water')}
    require({(r.get('article_n'), r.get('citation_ordinal'), r.get('source_id'))
             for r in external if type(r) is dict} == held_out,
            'outside-shared disputed identities changed')
    for row in external:
        key = row['article_n'], row['citation_ordinal']
        require(key in complement, 'outside-shared claim unexpectedly reclassified')
        slug, original = originals[key]
        require(row.get('article_slug') == slug
                and row.get('authored_context_excerpt') == original['context_excerpt']
                and row.get('context_sha256') == original['context_sha256']
                and row.get('author_source_use_note_sha256') == original['author_note_sha256']
                and row.get('review_terms') == sorted(set(original['human_risk_review_terms']))
                and row.get('disputed_original_citation') is True
                and row.get('source_support_verified') is False
                and row.get('safety_approved') is False,
                'outside-shared original disputed witness cleared')
    require((20, 55) in shared and (7, 30) in complement and (7, 48) in complement,
            'three original citation safety holds lost')

    pending = []
    for n, ordinal in complement:
        slug, original = originals[n, ordinal]
        pending.append({'article_n': n, 'article_slug': slug,
                        'citation_ordinal': ordinal, 'source_id': original['source_id'],
                        'authored_context_excerpt': original['context_excerpt'],
                        'context_sha256': original['context_sha256'],
                        'author_source_use_note_sha256': original['author_note_sha256'],
                        'risk_terms': sorted(set(original['human_risk_review_terms'])),
                        'original_dispute': (n, ordinal, original['source_id']) in HELD,
                        'source_support_verified': False, 'safety_approved': False})
    result = {'schema': SCHEMA, 'state': HOLD,
              'article_count': 35, 'citation_count': 2000,
              'shared_workorders': 562, 'nonshared_workorders': 1438,
              'total_unapproved_citation_occurrences': 2000,
              'shared_disputes': 1, 'nonshared_disputes': 2,
              'unreviewed_nonshared_queue': pending,
              **{flag: False for flag in FALSE}}
    result['receipt_sha256'] = digest(canonical(result))
    return result
