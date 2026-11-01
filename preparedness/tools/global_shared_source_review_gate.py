#!/usr/bin/env python3
"""R36: complete 30-group source-variant human-review CUSTODY, never approval.

Bridges R35's cited-only intake to *all* frozen duplicate-URL groups, including
uncited variants. Read-only, deterministic, original source records preserved.
The preceding source_group_review_gate independently freezes every input byte.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
import re

EXPECTED = (35, 1, 1959, 367, 43, 30)
INVENTORY = (224, 186, 30, 15)  # rows, distinct URLs, repeated URLs, repeated IDs
SOURCE_FILES = {'base': 'preparedness/sources/register.json', **{
    origin: f'preparedness/sources/fragments/{origin}.json'
    for origin in ('start', 'shelter', 'food', 'health', 'hist-food', 'hist-home', 'hist-field')}}
HOLD_FLAGS = ('may_publish', 'independent_QD_approval', 'qualified_safety_clearance',
              'human_source_reviews_completed', 'source_claim_accuracy_verified')
AUTHORITY = 'GLOBAL_SHARED_SOURCE_VARIANT_REVIEW_CUSTODY_NOT_APPROVAL'
PENDING = 'pending-human-source-and-reading-scope-review'
HEX = re.compile('[0-9a-f]{64}\\Z')

class GlobalSourceHold(ValueError):
    """Full inventory / cited-to-uncited provenance reconciliation failed."""

def require(ok, reason):
    if not ok:
        raise GlobalSourceHold(reason)

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def frozen_handoff(doc, expected):
    require(type(doc) is dict and doc.get('schema_version') == 1 and
            doc.get('issue') == 136 and doc.get('release_state') == 'HOLD' and
            doc.get('machine_authority') == 'SOURCE_AND_CLAIM_HUMAN_REVIEW_INTAKE_NOT_APPROVAL',
            'R35 intake schema/authority/release altered')
    for f in HOLD_FLAGS:
        require(doc.get(f) is False, 'R35 human/QD/medical/publish approval forged: '+f)
    fp = doc.get('fingerprint_sha256')
    require(type(fp) is str and HEX.fullmatch(fp) is not None and
            fp == sha({k:v for k,v in doc.items() if k != 'fingerprint_sha256'}),
            'R35 handoff fingerprint invalid')
    keys = ('articles', 'tools', 'citations', 'relationships',
            'base_fallback_relationships', 'shared_url_groups_unreviewed')
    require(doc.get('counts') == dict(zip(keys, expected)), 'R35 frozen census drift')
    forms = [doc.get(k) for k in ('source_scope_review_forms',
            'claim_occurrence_review_forms', 'base_fallback_review_forms',
            'shared_url_review_forms_for_used_sources_only')]
    require(all(type(f) is list for f in forms) and
            tuple(len(forms[i]) for i in range(3)) == (expected[3], expected[2], expected[4]),
            'R35 incomplete original reviewer intake')
    require(all(type(x) is dict and x.get('review_state') == 'NOT_STARTED'
                for f in forms for x in f), 'R35 review state falsely completed')
    require(doc.get('review_task_counts', {}).get('global_shared_url_groups_unreviewed') == expected[5],
            'R35 global shared source census lost')
    return fp, forms

def build_global_source_review(lib, handoff, *, expected=EXPECTED, inventory=INVENTORY,
                               source_files=SOURCE_FILES):
    """Strictly reconcile original source variants with R35 cited review intake.

    Overrides exist ONLY for isolated, deliberately reduced synthetic tests.
    Caller must already pass frozen source blob and 81-file corpus preflights.
    """
    require(type(expected) is tuple and len(expected) == 6 and
            all(type(n) is int and n >= 0 for n in expected), 'invalid corpus constants')
    require(type(inventory) is tuple and len(inventory) == 4 and
            all(type(n) is int and n >= 0 for n in inventory), 'invalid inventory constants')
    require(type(source_files) is dict and source_files and all(
            type(k) is str and type(v) is str and v for k,v in source_files.items()),
            'invalid source file allowlist')
    parent, (scopes, claims, fallbacks, cited_shared) = frozen_handoff(handoff, expected)
    variants = getattr(lib, 'source_variants', None)
    crosswalk = getattr(lib, 'crosswalk', None)
    groups_by_url = getattr(lib, 'crosswalk_groups', None)
    require(type(variants) is dict and type(crosswalk) is dict and
            type(groups_by_url) is dict and crosswalk.get('schema_version') == 1 and
            crosswalk.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
            'missing or approved source inventories')
    originals, by_url, by_id = {}, defaultdict(list), defaultdict(list)
    for sid, rows in variants.items():
        require(type(sid) is str and sid and type(rows) is list and rows,
                'invalid source identity inventory')
        for row in rows:
            require(type(row) is dict and row.get('id') == sid and
                    type(row.get('_origin')) is str and row['_origin'] in source_files and
                    type(row.get('url')) is str and row['url'].startswith('https://'),
                    'unknown origin, source ID or insecure URL')
            key = (row['_origin'], sid)
            require(key not in originals, 'ambiguous duplicate origin/source ID')
            originals[key] = row
            by_url[row['url']].append(key)
            by_id[sid].append(key)
    repeated = {url: sorted(keys) for url, keys in by_url.items() if len(keys) > 1}
    require((len(originals), len(by_url), len(repeated),
             sum(len(keys) > 1 for keys in by_id.values())) == inventory,
            'global 224-row/186-URL/30-group/15-ID source census drift')
    for key,val in zip(('raw_source_rows','unique_source_urls',
                        'duplicate_url_groups','duplicate_id_groups'), inventory):
        require(type(crosswalk.get(key)) is int and crosswalk[key] == val,
                'original crosswalk global count altered: '+key)
    groups = crosswalk.get('groups')
    require(type(groups) is list and len(groups) == expected[5] == inventory[2] and
            set(groups_by_url) == set(repeated), 'uncited shared-URL review groups missing')
    group_index = {}
    for g in groups:
        require(type(g) is dict and type(g.get('url')) is str and
                g['url'] in repeated and g['url'] not in group_index and
                g.get('canonical_url') == g['url'] and
                g.get('review_status') == PENDING and
                g.get('reviewer') is None and g.get('reviewed_on') is None,
                'global URL group absent, duplicated or falsely reviewed')
        url = g['url']
        require(canonical(groups_by_url[url]) == canonical(g),
                'source library and frozen crosswalk group disagree')
        rows, identities = g.get('variants'), g.get('identities')
        require(type(rows) is list and type(identities) is list and
                len(rows) == len(identities) == len(repeated[url]),
                'source variants or source identities dropped')
        seen_keys, seen_offsets = set(), set()
        for entry in rows:
            require(type(entry) is dict and type(entry.get('source')) is dict,
                    'invalid original crosswalk row')
            source, origin, index = entry['source'], entry.get('origin'), entry.get('row_index')
            require(type(index) is int and index >= 0 and
                    origin in source_files and entry.get('source_file') == source_files[origin],
                    'crosswalk origin, source file or row index altered')
            key = (origin, source.get('id'))
            require(key in repeated[url] and key not in seen_keys and
                    canonical(source) == canonical({k:v for k,v in originals[key].items()
                                                    if k != '_origin'}),
                    'unabridged source reading note or variant identity changed')
            require((origin,index) not in seen_offsets, 'duplicate source row index')
            seen_keys.add(key)
            seen_offsets.add((origin,index))
        want = Counter((x['origin'], x['source']['id'], x['row_index']) for x in rows)
        require(all(type(x) is dict and type(x.get('origin')) is str and
                    type(x.get('id')) is str and type(x.get('row_index')) is int
                    for x in identities) and
                Counter((x['origin'],x['id'],x['row_index']) for x in identities) == want and
                seen_keys == set(repeated[url]), 'crosswalk identity variants drift')
        group_index[url] = g
    require(set(group_index) == set(repeated), 'missing global shared-source group')
    scoped, by_relationship, used_url = {}, defaultdict(list), defaultdict(list)
    for form in scopes:
        require(type(form.get('slug')) is str and type(form.get('source_id')) is str,
                'malformed R35 source form')
        key = (form.get('source_origin'), form['source_id'])
        rid = form.get('relationship_id_sha256')
        require(key in originals and type(rid) is str and HEX.fullmatch(rid) and
                rid not in scoped and form.get('source_url') == originals[key]['url'] and
                canonical(form.get('unabridged_original_source_record')) == canonical(originals[key]) and
                form.get('source_record_sha256') == sha(originals[key]),
                'cited source lacks exact original raw row or relationship identity')
        scoped[rid] = form
        used_url[originals[key]['url']].append(rid)
    claim_ids = set()
    for item in claims:
        rid, case = item.get('relationship_id_sha256'), item.get('review_case_id_sha256')
        require(rid in scoped and type(case) is str and HEX.fullmatch(case) and
                case not in claim_ids and item.get('source_url') == scoped[rid]['source_url'],
                'claim occurrence orphaned or re-bound to a different URL')
        claim_ids.add(case)
        by_relationship[rid].append(case)
    require(len(claim_ids) == expected[2] and all(by_relationship[rid] for rid in scoped),
            'cited source omitted from individual claim review')
    fallback_relationships = [f.get('relationship_id_sha256') for f in fallbacks]
    require(len(set(fallback_relationships)) == expected[4] and
            all(rid in scoped and scoped[rid]['article_origin'] != scoped[rid]['source_origin']
                for rid in fallback_relationships), 'fallback provenance review lost')
    for rid,form in scoped.items():
        require((form['article_origin'] != form['source_origin']) ==
                (rid in fallback_relationships), 'missing fallback case on cited source')
    cited_map = {}
    for form in cited_shared:
        url, ids = form.get('source_url'), form.get('independent_relationship_ids')
        require(url in repeated and url not in cited_map and
                type(ids) is list and ids == sorted(set(ids)) and
                ids == sorted(used_url[url]) and
                form.get('human_separate_reading_scopes_reconciled') is None and
                form.get('human_discrepancy_or_exception_notes') is None,
                'R35 used shared-source grouping changed or approved')
        cited_map[url] = ids
    require(set(cited_map) == {url for url in repeated if used_url[url]},
            'uncited/cited URL groups conflated or omitted')
    cards = []
    for url in sorted(repeated):
        group = group_index[url]
        related = sorted(used_url[url])
        linked_claims = sorted(case for rid in related for case in by_relationship[rid])
        variant_cards = []
        for entry in sorted(group['variants'], key=lambda e:(e['origin'],e['row_index'])):
            original = originals[(entry['origin'], entry['source']['id'])]
            variant_cards.append({
                'origin': entry['origin'], 'source_file': entry['source_file'],
                'row_index': entry['row_index'], 'source_id': original['id'],
                'original_full_source_record': json.loads(canonical(original)),
                'source_identity_sha256': sha(original),
                'review_state': 'NOT_STARTED', 'human_source_access_date': None,
                'human_reading_scope_vs_other_variants': None,
                'human_conflict_or_provenance_notes': None})
        cards.append({
            'global_group_case_id_sha256': sha({'url': url,
                'original_crosswalk_group_sha256': sha(group)}),
            'source_url': url, 'original_crosswalk_group_sha256': sha(group),
            'unabridged_original_crosswalk_group': json.loads(canonical(group)),
            'distinct_original_variants': variant_cards,
            'used_in_any_citation': bool(related),
            'cited_relationship_ids': related,
            'cited_claim_review_case_ids': linked_claims,
            'review_state': 'NOT_STARTED',
            'human_url_and_reading_scope_reconciliation': None,
            'human_source_conflict_notes': None,
            'human_independent_safety_assessment': None})
    result = {'schema_version':1,'issue':136,'release_state':'HOLD',
              'machine_authority':AUTHORITY,
              **{k:False for k in HOLD_FLAGS},
              'parent_R35_fingerprint_sha256':parent,
              'original_global_crosswalk_sha256':sha(crosswalk),
              'original_all_source_variants_sha256':sha([originals[k] for k in sorted(originals)]),
              'counts':dict(zip(('source_rows','unique_urls','global_shared_url_groups',
                                 'repeated_source_id_groups'), inventory)),
              'global_shared_url_groups_reviewed_by_human':0,
              'shared_url_groups_with_cited_sources':sum(bool(used_url[u]) for u in repeated),
              'shared_url_groups_without_cited_sources':sum(not used_url[u] for u in repeated),
              'globally_unreviewed_shared_url_cards':cards,
              'limits':'Machine census and unabridged source-copy integrity only; no external link visit, '
                       'individual claim verification, human review, QD PASS or medical safety approval.'}
    require(len(cards) == inventory[2] and all(c['review_state'] == 'NOT_STARTED' for c in cards),
            'global source reviewer packet incomplete')
    result['fingerprint_sha256'] = sha(result)
    return result
