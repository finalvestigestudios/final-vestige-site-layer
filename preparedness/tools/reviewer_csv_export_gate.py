#!/usr/bin/env python3
"""R37: private, deterministic, spreadsheet-safe HUMAN REVIEW export custody.

Transforms the *unreviewed* R35/R36 source/citation packets into usable CSV
review work queues. Raw originals remain in the upstream fingerprint-bound JSON;
CSV is an escaped presentation, not a change to the historical source record.
Never reads networks, accepts human approvals, writes CMS data, or publishes.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
import re

EXPECTED = (35, 1, 1959, 367, 43, 30)
HOLD_FLAGS = ('may_publish', 'independent_QD_approval', 'qualified_safety_clearance',
              'human_source_reviews_completed', 'source_claim_accuracy_verified')
HEX = re.compile(r'[a-f0-9]{64}\Z')
AUTHORITY = 'PRIVATE_CSV_HUMAN_REVIEW_WORKSHEETS_NOT_APPROVAL'
# Spreadsheet programs often interpret a leading =,+,-,@ as a formula, even
# if the source string originated in a quotation. Escape before CSV quoting.
_FORMULA = re.compile(r'^[\s\ufeff\u200b]*[=+\-@]', re.UNICODE)

class ExportHold(ValueError):
    """Missing, altered, approved or ambiguous human-review evidence."""

def need(ok, message):
    if not ok:
        raise ExportHold(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def _hex(v):
    return type(v) is str and HEX.fullmatch(v) is not None

def _frozen(doc, authority):
    need(type(doc) is dict and doc.get('schema_version') == 1 and
         doc.get('issue') == 136 and doc.get('release_state') == 'HOLD' and
         doc.get('machine_authority') == authority, 'review packet is not frozen HOLD')
    for f in HOLD_FLAGS:
        need(doc.get(f) is False, 'review packet contains forged approval: '+f)
    fp = doc.get('fingerprint_sha256')
    need(_hex(fp) and sha({k:v for k,v in doc.items() if k != 'fingerprint_sha256'}) == fp,
         'review packet fingerprint mismatch')
    return fp

def _safe_cell(v):
    """Lossless, reversible CSV cell presentation; neutralize spreadsheet formulas.

    Newline/tab and backslash escapes prevent multi-line formula smuggling while
    preserving original text in the upstream source packet. None stays blank.
    Unescape after import only by a program treating cells as *data*, never eval.
    """
    if v is None:
        return ''
    if type(v) is bool:
        v = 'true' if v else 'false'
    elif type(v) in (dict, list, tuple):
        v = canonical(v).decode('utf-8')
    elif type(v) is not str:
        v = str(v)
    v = v.replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')
    if _FORMULA.match(v):
        v = "'" + v
    return v

def _render(header, rows):
    need(type(header) is tuple and header and len(set(header)) == len(header),
         'ambiguous CSV columns')
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, dialect='excel', lineterminator='\r\n')
    writer.writerow(header)
    for row in rows:
        need(type(row) is dict and set(row) == set(header),
             'CSV export row has missing or unaccounted evidence fields')
        writer.writerow([_safe_cell(row[key]) for key in header])
    content = stream.getvalue()
    # Round-trip CSV parse, cardinality and shape. No external I/O.
    parsed = list(csv.reader(io.StringIO(content, newline='')))
    need(parsed[0] == list(header) and len(parsed) == len(rows) + 1 and
         all(len(r) == len(header) for r in parsed), 'CSV round-trip lost review data')
    return content

CLAIM = ('claim_case_sha256', 'relationship_sha256', 'slug', 'source_id',
         'source_url', 'original_codepoint_offset', 'triage_priority_not_verdict',
         'triage_tags_not_safety_findings', 'exact_original_context',
         'review_state', 'human_source_access_date', 'human_exact_page_locator',
         'human_claim_support_assessment', 'human_scope_risk_notes',
         'human_qualified_safety_check')
SCOPE = ('source_case_sha256', 'relationship_sha256', 'slug', 'source_id',
         'article_origin', 'original_source_origin', 'source_url',
         'full_original_source_record_json', 'full_original_article_source_use',
         'source_record_sha256', 'source_use_sha256', 'impacted_claims',
         'review_state', 'human_access_date', 'human_reading_scope_check',
         'human_publisher_authority_check', 'human_discrepancy_notes')
FALLBACK = ('fallback_case_sha256', 'relationship_sha256', 'article_origin',
            'original_source_origin', 'source_url', 'review_state',
            'human_reading_scope_match', 'human_provenance_exception_notes')
GROUP = ('global_group_case_sha256', 'source_url', 'original_crosswalk_sha256',
         'full_original_crosswalk_group_json', 'distinct_original_variants_json',
         'used_in_any_citation', 'cited_relationship_ids_json', 'cited_claim_case_ids_json',
         'review_state', 'human_url_and_scope_reconciliation', 'human_source_conflict_notes',
         'human_independent_safety_assessment')

TABLES = {'claim_review.csv': CLAIM, 'source_scope_review.csv': SCOPE,
          'fallback_scope_review.csv': FALLBACK, 'global_shared_url_review.csv': GROUP}

def build_review_csv_export(handoff, global_review, reading_batches, *, expected=EXPECTED):
    """Produce content-addressed CSV worklists with strict cross-packet custody.

    Machine success means only that the original evidence has reached the
    private reviewer *desk*, not that any of it is true or medically safe.
    """
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(x) is int and x >= 0 for x in expected), 'invalid expected census')
    hf = _frozen(handoff, 'SOURCE_AND_CLAIM_HUMAN_REVIEW_INTAKE_NOT_APPROVAL')
    gf = _frozen(global_review, 'GLOBAL_SHARED_SOURCE_VARIANT_REVIEW_CUSTODY_NOT_APPROVAL')
    rf = _frozen(reading_batches, 'LOSSLESS_HUMAN_REVIEW_BATCHES_NOT_APPROVAL')
    need(handoff.get('parent_R34_fingerprint_sha256') == rf,
         'handoff does not descend from the exact original R34 reading evidence')
    cards = reading_batches.get('relationship_review_cards')
    need(type(cards) is list and len(cards) == expected[3],
         'missing original source-reading review cards')
    original_index = {}
    original_claims = {}
    for card in cards:
        need(type(card) is dict and card.get('review_state') == 'UNREVIEWED',
             'original review card falsely approved')
        rid = card.get('relationship_id_sha256')
        need(_hex(rid) and rid not in original_index,
             'duplicate original source-reading relationship')
        original_index[rid] = card
        original_cites = card.get('citation_review_items')
        need(type(original_cites) is list and original_cites,
             'original source card has no claim citations')
        for item in original_cites:
            need(type(item) is dict and item.get('review_state') ==
                 'PENDING_INDEPENDENT_CLAIM_AND_SAFETY_REVIEW',
                 'original claim not pending independent review')
            claim_ref_sha = item.get('claim_ref_sha256')
            cid = sha({'relationship_id_sha256':rid,'claim_ref_sha256':claim_ref_sha})
            need(_hex(claim_ref_sha) and cid not in original_claims and
                 item.get('claim_ref_sha256') == sha(item.get('claim_ref')) and
                 type(item.get('original_context')) is str and
                 item['claim_ref'].get('citation_context_sha256') ==
                    hashlib.sha256(item['original_context'].encode('utf-8')).hexdigest(),
                 'original claim citation context or original fingerprint altered')
            original_claims[cid] = (rid, item)

    need(global_review.get('parent_R35_fingerprint_sha256') == hf,
         'global-source packet does not descend from exact cited-source handoff')
    hcounts = handoff.get('counts')
    need(type(hcounts) is dict and [hcounts.get(k) for k in
         ('articles','tools','citations','relationships','base_fallback_relationships',
          'shared_url_groups_unreviewed')] == list(expected),
         'original article, claim, source or shared URL census drift')
    gcounts = global_review.get('counts')
    need(type(gcounts) is dict and gcounts.get('global_shared_url_groups') == expected[5],
         'global source inventory census drift')
    if expected == EXPECTED:
        need(tuple(gcounts.get(k) for k in
                   ('source_rows','unique_urls','global_shared_url_groups',
                    'repeated_source_id_groups')) == (224, 186, 30, 15),
             'original full source inventory was not preserved')
    need(global_review.get('global_shared_url_groups_reviewed_by_human') == 0,
         'unverified shared URLs marked human reviewed')
    scopes = handoff.get('source_scope_review_forms')
    claims = handoff.get('claim_occurrence_review_forms')
    fallbacks = handoff.get('base_fallback_review_forms')
    groups = global_review.get('globally_unreviewed_shared_url_cards')
    need(all(type(x) is list for x in (scopes,claims,fallbacks,groups)) and
         (len(scopes),len(claims),len(fallbacks),len(groups)) ==
         (expected[3],expected[2],expected[4],expected[5]),
         'missing, extra or incomplete reviewer worksheets')
    source_index, url_index = {}, defaultdict(list)
    source_rows = []
    for s in scopes:
        need(type(s) is dict and s.get('review_state') == 'NOT_STARTED',
             'source scope falsely reviewed')
        rid = s.get('relationship_id_sha256')
        record = s.get('unabridged_original_source_record')
        use = s.get('unabridged_article_specific_source_use')
        need(_hex(rid) and rid not in source_index and type(record) is dict and
             type(use) is str and bool(use.strip()) and
             s.get('source_record_sha256') == sha(record) and
             s.get('source_use_sha256') == hashlib.sha256(use.encode('utf-8')).hexdigest() and
             record.get('id') == s.get('source_id') and
             record.get('url') == s.get('source_url') and
             record.get('_origin') == s.get('source_origin') and
             type(s.get('source_url')) is str and s['source_url'].startswith('https://'),
             'source record, scope, origin or digest lost')
        need(_hex(s.get('source_case_id_sha256')) and
             s['source_case_id_sha256'] == sha({'relationship_id_sha256':rid,
                                  'review_type':'ORIGINAL_SOURCE_READING_SCOPE'}),
             'source review task identity changed')
        for key in ('human_link_access_date','human_source_reading_scope_assessment',
                    'human_publisher_authority_assessment','human_discrepancy_or_correction_notes'):
            need(s.get(key) is None, 'source review field already populated: '+key)
        original = original_index.get(rid)
        need(original is not None and original.get('slug') == s.get('slug') and
             original.get('source_id') == s.get('source_id') and
             original.get('article_origin') == s.get('article_origin') and
             original.get('source_origin') == s.get('source_origin') and
             original.get('source_url') == s.get('source_url') and
             canonical(original.get('original_source_record_as_selected')) == canonical(record) and
             original.get('full_original_article_source_use') == use,
             'source reading evidence differs from original R34 card')
        source_index[rid] = s
        url_index[s['source_url']].append(rid)
        source_rows.append(dict(zip(SCOPE, (
            s['source_case_id_sha256'],rid,s['slug'],s['source_id'],
            s['article_origin'],s['source_origin'],s['source_url'],record,use,
            s['source_record_sha256'],s['source_use_sha256'],
            s['source_impact_claim_occurrences'],'NOT_STARTED',None,None,None,None))))
    claim_index = {}
    claim_rows = []
    claim_counts = Counter()
    for c in claims:
        need(type(c) is dict and c.get('review_state') == 'NOT_STARTED',
             'claim falsely marked reviewed')
        rid, cid = c.get('relationship_id_sha256'), c.get('review_case_id_sha256')
        source = source_index.get(rid)
        need(source is not None and _hex(cid) and cid not in claim_index and
             cid == sha({'relationship_id_sha256': rid,
                         'claim_ref_sha256': c.get('claim_ref_sha256')}) and
             c.get('slug') == source['slug'] and c.get('source_id') == source['source_id'] and
             c.get('source_url') == source['source_url'] and
             type(c.get('exact_original_context')) is str and
             c['exact_original_context'].count('[CITATION]') == 1 and
             type(c.get('original_codepoint_offset')) is int and
             c['original_codepoint_offset'] >= 0 and
             c.get('triage_priority_not_verdict') in ('REVIEW_FIRST','STANDARD_REVIEW') and
             type(c.get('triage_tags_not_safety_findings')) is list,
             'claim context, identity, source or priority lost')
        original_claim = original_claims.get(cid)
        need(original_claim is not None and original_claim[0] == rid and
             original_claim[1]['claim_ref_sha256'] == c.get('claim_ref_sha256') and
             original_claim[1]['original_context'] == c.get('exact_original_context') and
             original_claim[1]['claim_ref']['citation_codepoint_offset'] ==
                 c.get('original_codepoint_offset') and
             original_claim[1]['priority'] == c.get('triage_priority_not_verdict') and
             original_claim[1]['triage_tags_not_safety_findings'] ==
                 c.get('triage_tags_not_safety_findings'),
             'individual reviewer claim differs from original R34 citation reading')
        for key in ('human_source_access_date','human_exact_page_or_section_locator',
                    'human_claim_to_source_support_assessment','human_risk_or_scope_notes',
                    'independent_qualified_safety_review'):
            need(c.get(key) is None, 'claim reviewer result forged: '+key)
        claim_counts[rid] += 1
        claim_index[cid] = c
        claim_rows.append(dict(zip(CLAIM, (
            cid,rid,c['slug'],c['source_id'],c['source_url'],
            c['original_codepoint_offset'],c['triage_priority_not_verdict'],
            c['triage_tags_not_safety_findings'],c['exact_original_context'],
            'NOT_STARTED',None,None,None,None,None))))
    need(set(original_index) == set(source_index) and
         set(original_claims) == set(claim_index),
         'original R34 source/citation evidence omitted from CSV tasks')
    need(all(claim_counts[rid] == s['source_impact_claim_occurrences']
             for rid,s in source_index.items()),
         'source-to-claim count or reviewer scope drift')
    fallback_rows = []
    fallback_ids = set()
    for f in fallbacks:
        need(type(f) is dict and f.get('review_state') == 'NOT_STARTED',
             'fallback source falsely marked reviewed')
        rid = f.get('relationship_id_sha256')
        s = source_index.get(rid)
        need(s is not None and rid not in fallback_ids and
             s['article_origin'] != s['source_origin'] and
             f.get('article_origin') == s['article_origin'] and
             f.get('original_source_origin') == s['source_origin'] and
             f.get('source_url') == s['source_url'] and
             f.get('fallback_case_id_sha256') == sha({'relationship_id_sha256':rid,
                'review_type':'ORIGINAL_CROSS_CLUSTER_FALLBACK_SCOPE'}),
             'fallback provenance detached from original source scope')
        need(f.get('human_original_reading_scope_matches_article_use') is None and
             f.get('human_provenance_exception_notes') is None,
             'fallback reviewer fields already populated')
        fallback_ids.add(rid)
        fallback_rows.append(dict(zip(FALLBACK, (
            f['fallback_case_id_sha256'],rid,f['article_origin'],
            f['original_source_origin'],f['source_url'],'NOT_STARTED',None,None))))
    need({rid for rid,s in source_index.items() if s['article_origin'] != s['source_origin']} == fallback_ids,
         'missing fallback scope review assignment')
    group_rows = []
    seen_urls, seen_group_ids = set(), set()
    for g in groups:
        need(type(g) is dict and g.get('review_state') == 'NOT_STARTED',
             'global shared URL falsely reconciled')
        url, gid = g.get('source_url'),g.get('global_group_case_id_sha256')
        original = g.get('unabridged_original_crosswalk_group')
        variants = g.get('distinct_original_variants')
        need(type(url) is str and url.startswith('https://') and url not in seen_urls and
             _hex(gid) and gid not in seen_group_ids and type(original) is dict and
             type(variants) is list and len(variants) >= 2 and
             g.get('original_crosswalk_group_sha256') == sha(original) and
             gid == sha({'url':url,'original_crosswalk_group_sha256':sha(original)}) and
             original.get('url') == url,
             'crosswalk group ID, URL or unabridged original evidence changed')
        original_variants = original.get('variants')
        need(type(original_variants) is list and len(original_variants) == len(variants) and
             original.get('canonical_url') == url and
             original.get('review_status') == 'pending-human-source-and-reading-scope-review' and
             original.get('reviewer') is None and original.get('reviewed_on') is None,
             'original crosswalk reading variants missing or previously approved')
        original_keys = {(x['origin'], x['row_index'], canonical(x['source']))
                         for x in original_variants if type(x) is dict and
                         type(x.get('source')) is dict and type(x.get('origin')) is str and
                         type(x.get('row_index')) is int}
        variant_keys = {(v['origin'], v['row_index'], canonical({k:value for k,value in
                            v['original_full_source_record'].items() if k != '_origin'}))
                        for v in variants if type(v) is dict and
                        type(v.get('original_full_source_record')) is dict and
                        type(v.get('origin')) is str and type(v.get('row_index')) is int}
        need(len(original_keys) == len(variants) and original_keys == variant_keys,
             'original source-row locations or reading-depth variants changed')
        for v in variants:
            need(type(v) is dict and v.get('review_state') == 'NOT_STARTED' and
                 type(v.get('original_full_source_record')) is dict and
                 v.get('source_identity_sha256') == sha(v['original_full_source_record']) and
                 v['original_full_source_record'].get('url') == url and
                 v.get('human_source_access_date') is None and
                 v.get('human_reading_scope_vs_other_variants') is None and
                 v.get('human_conflict_or_provenance_notes') is None,
                 'global source variant is missing evidence or falsely reviewed')
        related = g.get('cited_relationship_ids')
        related_claims = g.get('cited_claim_review_case_ids')
        need(type(related) is list and type(related_claims) is list and
             related == sorted(set(url_index[url])) and
             related_claims == sorted(cid for cid,c in claim_index.items()
                                      if c['source_url'] == url) and
             g.get('used_in_any_citation') is bool(related),
             'global URL group citation lineage lost, duplicated or invented')
        for key in ('human_url_and_reading_scope_reconciliation','human_source_conflict_notes',
                    'human_independent_safety_assessment'):
            need(g.get(key) is None, 'global URL reviewer result forged: '+key)
        seen_urls.add(url)
        seen_group_ids.add(gid)
        group_rows.append(dict(zip(GROUP, (
            gid,url,g['original_crosswalk_group_sha256'],original,variants,
            bool(related),related,related_claims,'NOT_STARTED',None,None,None))))
    need(len(seen_urls) == expected[5], 'global duplicate URL rows dropped')
    rows = {'claim_review.csv': sorted(claim_rows,key=lambda x:x['claim_case_sha256']),
            'source_scope_review.csv': sorted(source_rows,key=lambda x:x['source_case_sha256']),
            'fallback_scope_review.csv': sorted(fallback_rows,key=lambda x:x['fallback_case_sha256']),
            'global_shared_url_review.csv': sorted(group_rows,key=lambda x:x['source_url'])}
    csvs = {name:_render(header,rows[name]) for name,header in TABLES.items()}
    manifest = {'schema_version':1,'issue':136,'release_state':'HOLD',
                'machine_authority':AUTHORITY,
                **{f:False for f in HOLD_FLAGS},
                'parent_R35_fingerprint_sha256':hf,
                'parent_R36_fingerprint_sha256':gf,
                'parent_R34_original_reading_sha256':rf,
                'counts':dict(zip(('articles','tools','claim_reviews','source_scope_reviews',
                                   'fallback_reviews','global_shared_url_reviews'), expected)),
                'csv_tables':{name:{'rows':len(rows[name]),
                                    'sha256_utf8':hashlib.sha256(csvs[name].encode('utf-8')).hexdigest(),
                                    'bytes_utf8':len(csvs[name].encode('utf-8')),
                                    'columns':list(header)}
                              for name,header in TABLES.items()},
                'limits':'CSV reviewer worksheets are NOT an approval record. Full original research and '
                         'reading depth remain upstream, fingerprint-bound. No external source visited; '
                         'all human review blank; no medical safety or QD signoff.'}
    manifest['fingerprint_sha256'] = sha(manifest)
    return {'manifest':manifest,'csv_tables':csvs}
