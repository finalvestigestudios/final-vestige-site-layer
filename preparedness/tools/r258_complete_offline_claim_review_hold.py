#!/usr/bin/env python3
"""R258: source-bound, ALL-2000-citation in-memory review surface (DRAFT HARD HOLD).

Consumes R254 and R257 audited records; never approves claims, calls the network,
changes articles, renders for public WordPress or saves a file. Content is escaped.
An HTML review preview is not independent evidence review or medical certification.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import html
import json
import re

SCHEMA = 'fv-preparedness-r258-2000-claim-offline-review-v1'
HOLD = 'DRAFT_HARD_HOLD'
R254 = 'fv-preparedness-r254-readable-claim-workorders-v1'
R257 = 'fv-preparedness-r257-complete-citation-partition-v1'
SHA = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
DISPUTES = {(7, 30, 'cdc-find-clean-water'),
            (7, 48, 'cdc-find-clean-water'), (20, 55, 'start-ready-plan')}
FALSE = ('independent_claim_source_verified', 'independent_qd_pass',
         'medical_safety_verified', 'merchant_approved', 'publication_authorized')


def hold(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError('R258 DRAFT HARD HOLD: ' + reason)


def encode(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sha(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def receipt(doc: dict, schema: str) -> None:
    hold(type(doc) is dict and doc.get('schema') == schema
         and doc.get('state') == HOLD, 'wrong source schema/state')
    d = doc.get('receipt_sha256')
    hold(type(d) is str and SHA.fullmatch(d) is not None and
         d == sha(encode({k: v for k, v in doc.items() if k != 'receipt_sha256'})),
         'source receipt is invalid or altered')
    for flag in FALSE:
        hold(doc.get(flag) is False, 'source receipt unauthorized approval ' + flag)


def checked_entry(row: object, *, shared: bool) -> tuple[tuple[int, int], dict]:
    hold(type(row) is dict, 'malformed citation context')
    n, o = row.get('article_n'), row.get('citation_ordinal')
    slug, sid = row.get('article_slug'), row.get('source_id')
    hold(type(n) is int and 1 <= n <= 35 and type(o) is int and o > 0,
         'invalid original citation position')
    hold(type(slug) is str and SLUG.fullmatch(slug) is not None and
         type(sid) is str and SLUG.fullmatch(sid) is not None,
         'invalid article/source identity')
    excerpt = row.get('authored_context_excerpt')
    hold(type(excerpt) is str and 6 <= len(excerpt) <= 1000
         and row.get('context_sha256') == sha(excerpt),
         'original excerpt or hash mismatch')
    hold(type(row.get('author_source_use_note_sha256')) is str and
         SHA.fullmatch(row['author_source_use_note_sha256']) is not None,
         'missing original author-source-use witness')
    terms = row.get('review_terms') if shared else row.get('risk_terms')
    hold(type(terms) is list and terms == sorted(set(terms))
         and all(type(t) is str and 0 < len(t) <= 100 for t in terms),
         'review risk terms malformed')
    hold(row.get('source_support_verified') is False and
         row.get('safety_approved') is False,
         'citation was silently approved')
    flag = 'disputed_original_citation' if shared else 'original_dispute'
    hold(row.get(flag) is ((n, o, sid) in DISPUTES),
         'original dispute was hidden or invented')
    return (n, o), row


def prepare(workorders: dict, partition: dict) -> tuple[list[dict], dict]:
    """Bind all 2000 context rows to their original shared-source group or complement."""
    receipt(workorders, R254)
    receipt(partition, R257)
    counts = [(workorders, 'source_review_groups', 32),
              (workorders, 'shared_source_ids', 56),
              (workorders, 'human_readable_workorders', 562),
              (workorders, 'other_citation_occurrences_still_unreviewed', 1438),
              (partition, 'shared_workorders', 562),
              (partition, 'nonshared_workorders', 1438),
              (partition, 'total_unapproved_citation_occurrences', 2000)]
    for src, key, expected in counts:
        hold(type(src.get(key)) is int and src[key] == expected, 'coverage drift ' + key)
    for src in (workorders, partition):
        for key, value in [('article_count', 35), ('citation_count', 2000),
                           ('shared_disputes', 1), ('nonshared_disputes', 2)]:
            # R254 calls the last two counters shared_disputed_claims/outside_shared_disputed_claims.
            if src is workorders and key in ('shared_disputes', 'nonshared_disputes'):
                key = 'shared_disputed_claims' if key == 'shared_disputes' else 'outside_shared_disputed_claims'
            hold(type(src.get(key)) is int and src[key] == value, 'original hold/census drift ' + key)
    hold(workorders.get('disputed_original_claims') == 3, 'three original disputes missing')
    groups = workorders.get('review_queue')
    hold(type(groups) is list and len(groups) == 32, '32 source groups required')
    source_ids, seen_urls, coverage = set(), set(), {}
    for group in groups:
        hold(type(group) is dict and group.get('state') ==
             'PENDING_HUMAN_SOURCE_AND_CLAIM_REVIEW' and
             group.get('source_scope_approved') is False and
             group.get('claim_support_approved') is False,
             'shared source group unapproved state changed')
        ids = group.get('source_ids')
        url = group.get('source_url')
        hold(type(url) is str and url.startswith(('https://', 'http://'))
             and len(url) <= 2048 and url not in seen_urls,
             'missing or duplicate original source URL')
        seen_urls.add(url)
        hold(type(ids) is list and ids and len(ids) == len(set(ids))
             and all(type(s) is str and SLUG.fullmatch(s) for s in ids)
             and not source_ids.intersection(ids), 'source ID moved between groups')
        source_ids.update(ids)
        rows = group.get('workorders')
        hold(type(rows) is list and type(group.get('workorder_count')) is int
             and group['workorder_count'] == len(rows), 'group workorder missing')
        previous = (0, 0)
        for row in rows:
            key, r = checked_entry(row, shared=True)
            hold(key > previous and key not in coverage,
                 'shared workorders duplicated or reordered')
            previous = key
            hold(r['source_id'] in ids, 'shared citation mismatched source group')
            coverage[key] = ('SHARED', r, url)
    hold(len(source_ids) == 56 and len(coverage) == 562,
         'not exactly 56 shared sources / 562 occurrences')
    rows = partition.get('unreviewed_nonshared_queue')
    hold(type(rows) is list and len(rows) == 1438, '1438 other citations required')
    previous = (0, 0)
    for row in rows:
        key, r = checked_entry(row, shared=False)
        hold(key > previous and key not in coverage,
             'other citation duplicate, unsorted or overlapping shared set')
        previous = key
        hold(r['source_id'] not in source_ids,
             'shared-source ID incorrectly assigned to unmatched complement')
        coverage[key] = ('OTHER', r, None)
    hold(len(coverage) == 2000, 'incomplete citation partition')
    by_article = defaultdict(list)
    slugs = {}
    disputes = set()
    for key in sorted(coverage):
        category, r, url = coverage[key]
        n, o = key
        old = slugs.setdefault(n, r['article_slug'])
        hold(old == r['article_slug'], 'article slug mismatch across citations')
        by_article[n].append((category, r, url))
        if (n, o, r['source_id']) in DISPUTES:
            disputes.add((n, o, r['source_id']))
    hold(set(by_article) == set(range(1, 36)), 'not all 35 articles represented')
    for n, entries in by_article.items():
        hold([r['citation_ordinal'] for _, r, _ in entries] ==
             list(range(1, len(entries) + 1)),
             'missing/reordered citation position in article ' + str(n))
    hold(disputes == DISPUTES, 'one of three disputed original citations lost')
    # Bind R254 independent CDC exceptions to the exact OTHER contexts.
    ext = workorders.get('outside_shared_disputed_workorders')
    hold(type(ext) is list and len(ext) == 2, 'outside-shared CDC exceptions missing')
    for row in ext:
        key, r = checked_entry(row, shared=True)
        hold(key in coverage and coverage[key][0] == 'OTHER',
             'outside-shared disputed citation reclassified')
        original = coverage[key][1]
        for k, other in [('article_slug', 'article_slug'), ('source_id', 'source_id'),
                         ('authored_context_excerpt', 'authored_context_excerpt'),
                         ('context_sha256', 'context_sha256'),
                         ('author_source_use_note_sha256', 'author_source_use_note_sha256')]:
            hold(r[k] == original[other], 'outside-shared evidence mismatch ' + k)
    summary = {'schema': SCHEMA, 'state': HOLD, 'article_count': 35,
               'citation_occurrences': 2000, 'shared': 562, 'other': 1438,
               'source_groups': 32, 'shared_source_ids': 56,
               'held_disputes': 3, 'review_approval': False,
               **{k: False for k in FALSE}}
    return [(n, slugs[n], by_article[n]) for n in range(1, 36)], summary


def render_full_review(workorders: dict, partition: dict) -> dict:
    """In-memory HTML only; all claim excerpts are plain-text escaped and visible."""
    articles, summary = prepare(workorders, partition)
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">',
           '<title>Preparedness 2000-Citation Unapproved Review</title>',
           '<style>body{font:1rem/1.65 system-ui,sans-serif;max-width:76ch;margin:auto;padding:1rem;color:#17212c;background:#fff}article{border-top:2px solid #333;margin-top:2rem}li{padding:.6rem;border-bottom:1px solid #ccc;overflow-wrap:anywhere}li.disputed{border-left:5px solid #960000;padding-left:1rem}strong,small{display:block}p{white-space:pre-wrap}header{border:3px solid #960000;padding:1rem}code{overflow-wrap:anywhere}@media print{li{break-inside:avoid}}</style>',
           '</head><body><header><h1>UNAPPROVED — Preparedness Citation Review</h1>',
           '<p>DRAFT / HARD HOLD. Authored citation contexts are NOT independently verified, medically certified, cleared for public safety, or approved for publication. 35 articles; 2,000 original citation occurrences; 562 shared-source and 1,438 other; 3 disputed original citations. Offline editorial review only. No clickable source URLs or commercial offers.</p></header><main>']
    for n, slug, entries in articles:
        out.append('<article id="article-'+str(n)+'"><h2>Article '+str(n)+': '+html.escape(slug, quote=True)+'</h2><ol>')
        for category, r, url in entries:
            ordinal = r['citation_ordinal']
            held = (n, ordinal, r['source_id']) in DISPUTES
            out.append('<li id="cite-'+str(n)+'-'+str(ordinal)+'"'+
                       (' class="disputed"' if held else '')+'><strong>UNREVIEWED '+category+
                       ' citation '+str(ordinal)+(' — DISPUTED / HUMAN ADJUDICATION REQUIRED' if held else '')+
                       '</strong><small>Source ID: '+html.escape(r['source_id'], quote=True)+'</small>')
            if url is not None:
                out.append('<small>Shared-group source URL (not verified; unlinked): '+html.escape(url, quote=True)+'</small>')
            out.append('<p>'+html.escape(r['authored_context_excerpt'], quote=True)+'</p>')
            out.append('<small>Context SHA-256: <code>'+r['context_sha256']+'</code>; author-note SHA-256: <code>'+r['author_source_use_note_sha256']+'</code></small></li>')
        out.append('</ol></article>')
    out.append('</main><footer>DRAFT HARD HOLD — source review and independent QD pending. No approval or publication authorized.</footer></body></html>')
    page = ''.join(out)
    hold(page.count('<li id="cite-') == 2000 and page.count('<article id="article-') == 35,
         'review output omitted original citation context')
    summary['offline_review_sha256'] = sha(page)
    summary['offline_review_utf8_bytes'] = len(page.encode('utf-8'))
    summary['offline_review_html'] = page  # in-memory internal editorial artifact
    return summary
