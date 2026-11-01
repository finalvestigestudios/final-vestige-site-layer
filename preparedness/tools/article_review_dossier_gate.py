#!/usr/bin/env python3
"""R42 private article-by-article citation/source/safety handoff (Issue #136).

This read-only index preserves *every* frozen R37 worksheet row and its original
research fields, without treating any machine-verification date or old taxonomy
safety-approved-draft label as real qualified safety clearance. A caller MUST
supply a separately pinned R37 fingerprint for independent use. The repo's
mandatory build constructs that fingerprint from the upstream frozen chain.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re

R37 = Path(__file__).with_name('reviewer_csv_export_gate.py')
R38 = Path(__file__).with_name('reviewer_quarantine_gate.py')
if any(not p.is_file() or p.is_symlink() for p in (R37,R38)):
    raise ValueError('exact unsymlinked R37/R38 source gate modules required')

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise ValueError('cannot import frozen review gate '+name)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

r37 = _load(R37, 'preparedness_r42_exact_r37')
r38 = _load(R38, 'preparedness_r42_exact_r38')
EXPECTED = (35, 1, 1959, 367, 43, 30)
AUTHORITY = 'PRIVATE_PER_ARTICLE_EVIDENCE_AND_SAFETY_HANDOFF_NOT_APPROVAL'
FLAGS = ('may_publish','qualified_safety_clearance','independent_QD_approval',
         'human_source_reviews_completed','source_claim_accuracy_verified',
         'reviewer_real_identity_verified')
HEX = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

class DossierHold(ValueError):
    """Source/citation crosswalk could not be preserved without false approval."""

def need(condition, reason):
    if not condition:
        raise DossierHold(reason)

def _digest(v):
    return r37.sha(v)

def _hex(v):
    return type(v) is str and HEX.fullmatch(v) is not None and v != '0'*64

def _json_list(raw, reason):
    try:
        val=json.loads(raw)
    except (TypeError, ValueError, UnicodeError) as exc:
        raise DossierHold(reason) from exc
    need(type(val) is list and len(val) == len(set(map(repr,val))) and
         all(_hex(x) for x in val),reason)
    return val

def _taxonomy(taxonomy, expected, tool_slugs):
    need(type(taxonomy) is dict and type(taxonomy.get('slate')) is list and
         type(taxonomy.get('tools')) is list, 'full original taxonomy required')
    articles=taxonomy['slate']
    need(len(articles)==expected[0] and type(tool_slugs) is tuple and
         len(tool_slugs)==expected[1] and len(set(tool_slugs))==len(tool_slugs),
         'missing 35-piece slate or exact tool set')
    alltools={x.get('slug'):x for x in taxonomy['tools'] if type(x) is dict}
    need(len(alltools)==len(taxonomy['tools']) and all(k in alltools for k in tool_slugs),
         'tool inventory is duplicated or missing water planner')
    indexed={}
    for item in articles:
        need(type(item) is dict and item.get('n') == len(indexed)+1 and
             item.get('track') in ('modern','lost-ways') and
             type(item.get('title')) is str and bool(item['title'].strip()) and
             type(item.get('section')) is str and
             type(item.get('gate')) is bool and
             type(item.get('status')) is str, 'ordered original article taxonomy changed')
        key=item.get('slug')
        need(type(key) is str and SLUG.fullmatch(key) and key not in indexed,
             'duplicate or unsafe article slug')
        indexed[key]=dict(item)
    for key in tool_slugs:
        tool=alltools[key]
        need(type(key) is str and SLUG.fullmatch(key) and key not in indexed and
             type(tool.get('title')) is str and tool['title'].strip() and
             type(tool.get('gate')) is bool and
             type(tool.get('status')) is str,
             'water tool metadata is missing/ambiguous')
        indexed[key]=dict(tool)
    return indexed

def build_article_review_dossiers(original_r37, taxonomy, *,
                                  trusted_r37_manifest_sha256,
                                  expected=EXPECTED,
                                  tool_slugs=('water-planner',)):
    """Make private article-level review dossiers with complete source evidence.

    No human reviews are performed. This must never be used as a publication
    or clinical clearance mechanism. All case IDs are kept, never URL-merged.
    """
    need(type(expected) is tuple and len(expected)==6 and
         all(type(v) is int and v >= 0 for v in expected),
         'expected census must be an explicit bounded six-tuple')
    need(_hex(trusted_r37_manifest_sha256),
         'out-of-band original R37 manifest fingerprint required')
    try:
        manifest=r38.validated_manifest(original_r37)
    except (r38.IntakeHold,ValueError,TypeError) as exc:
        raise DossierHold('R37 source and citation evidence is not frozen') from exc
    need(manifest['fingerprint_sha256']==trusted_r37_manifest_sha256,
         'untrusted R37 original baseline substitution')
    expected_counts = dict(zip(('articles','tools','claim_reviews','source_scope_reviews',
                                'fallback_reviews','global_shared_url_reviews'),expected))
    need(manifest.get('counts')==expected_counts,
         'lost or duplicated 35+1 citation/source review census')
    lookup=_taxonomy(taxonomy,expected,tool_slugs)
    parsed={}
    for name in r37.TABLES:
        data=original_r37['csv_tables'][name]
        meta=manifest['csv_tables'][name]
        need(type(meta) is dict and set(meta)=={'rows','sha256_utf8','bytes_utf8','columns'}
             and meta['columns']==list(r37.TABLES[name])
             and type(meta['rows']) is int and meta['rows']==expected_counts[
                r38.TABLE_COUNTS[name]]
             and type(data) is str and
             hashlib.sha256(data.encode('utf-8')).hexdigest()==meta['sha256_utf8']
             and len(data.encode('utf-8'))==meta['bytes_utf8'],
             'original exported worksheet bytes/columns or counts changed: '+name)
        try:
            rows,_=r38.parse_table(data,name,limit=max(1000,len(data.encode('utf-8'))))
        except (r38.IntakeHold,UnicodeError,ValueError) as exc:
            raise DossierHold('R37 original worksheet cannot be parsed: '+name) from exc
        need(len(rows)==meta['rows'],'source/claim rows dropped: '+name)
        for row in rows.values():
            need(row['review_state']=='NOT_STARTED' and
                 all(value=='' for col,value in row.items() if col.startswith('human_')),
                 'original reviewer worksheet is not unreviewed HOLD')
        parsed[name]=rows
    scopes=parsed['source_scope_review.csv']
    claims=parsed['claim_review.csv']
    fallbacks=parsed['fallback_scope_review.csv']
    groups=parsed['global_shared_url_review.csv']
    by_article=defaultdict(lambda:{'scopes':[], 'claims':[], 'fallbacks':[], 'groups':[]})
    rid_to_scope={}
    used_by_url=defaultdict(lambda:{'relationship_ids':set(),'claim_ids':set()})
    for sid,scope in scopes.items():
        rid=scope['relationship_sha256'];slug=scope['slug'];url=scope['source_url']
        need(_hex(sid) and _hex(rid) and rid not in rid_to_scope and
             slug in lookup and url.startswith('https://') and
             type(scope['source_id']) is str and scope['source_id'] and
             scope['full_original_source_record_json'] and
             scope['full_original_article_source_use'] and
             _hex(scope['source_record_sha256']) and
             _hex(scope['source_use_sha256']) and
             scope['article_origin'] and scope['original_source_origin'],
             'orphaned, duplicate or lossy original source-reading scope')
        rid_to_scope[rid]=scope
        used_by_url[url]['relationship_ids'].add(rid)
        by_article[slug]['scopes'].append(dict(scope))
    claim_per_scope=Counter()
    for cid,claim in claims.items():
        rid=claim['relationship_sha256'];scope=rid_to_scope.get(rid)
        need(_hex(cid) and scope is not None and
             claim['slug']==scope['slug'] and
             claim['source_id']==scope['source_id'] and
             claim['source_url']==scope['source_url'] and
             claim['triage_priority_not_verdict'] in ('REVIEW_FIRST','STANDARD_REVIEW') and
             claim['exact_original_context'].count('[CITATION]')==1 and
             claim['original_codepoint_offset'].isdigit() and
             str(int(claim['original_codepoint_offset']))==claim['original_codepoint_offset'],
             'citation-to-source identity/offset/triage mismatch')
        claim_per_scope[rid]+=1
        used_by_url[claim['source_url']]['claim_ids'].add(cid)
        by_article[claim['slug']]['claims'].append(dict(claim))
    need(all(claim_per_scope[rid]==int(scope['impacted_claims']) and
             claim_per_scope[rid]>0 for rid,scope in rid_to_scope.items()),
         'citation occurrences do not match original reading scopes')
    fallback_rids=set()
    for fid,fallback in fallbacks.items():
        rid=fallback['relationship_sha256'];scope=rid_to_scope.get(rid)
        need(_hex(fid) and scope is not None and rid not in fallback_rids and
             fallback['article_origin']==scope['article_origin'] and
             fallback['original_source_origin']==scope['original_source_origin'] and
             fallback['source_url']==scope['source_url'] and
             scope['article_origin']!=scope['original_source_origin'],
             'fallback reading scope severed from original contributor')
        fallback_rids.add(rid)
        by_article[scope['slug']]['fallbacks'].append(dict(fallback))
    need(fallback_rids=={rid for rid,s in rid_to_scope.items()
                         if s['article_origin']!=s['original_source_origin']},
         'source-origin cross-cluster fallbacks were omitted')
    globally_uncited=[]
    seen_url=set()
    for gid,group in groups.items():
        url=group['source_url'];seen=used_by_url.get(url)
        related=sorted(seen['relationship_ids']) if seen else []
        claim_ids=sorted(seen['claim_ids']) if seen else []
        need(_hex(gid) and url.startswith('https://') and url not in seen_url and
             group['used_in_any_citation']==str(bool(related)).lower() and
             _json_list(group['cited_relationship_ids_json'],'bad shared URL scopes')==related and
             _json_list(group['cited_claim_case_ids_json'],'bad shared URL citations')==claim_ids and
             group['original_crosswalk_sha256'] and
             group['full_original_crosswalk_group_json'] and
             group['distinct_original_variants_json'],
             'globally shared URL variants were merged/altered/omitted')
        seen_url.add(url)
        for slug in sorted({rid_to_scope[rid]['slug'] for rid in related}):
            by_article[slug]['groups'].append(dict(group))
        if not related:
            globally_uncited.append(dict(group))
    need(len(by_article)==len(lookup) and set(by_article)==set(lookup),
         'an article or tool is missing independent claim evidence')
    dossiers=[]
    for slug in sorted(lookup):
        cases=by_article[slug];meta=lookup[slug]
        need(cases['claims'] and cases['scopes'],
             'article has zero source/claim review assignments: '+slug)
        id_keys={'claims':'claim_case_sha256', 'scopes':'source_case_sha256',
                 'fallbacks':'fallback_case_sha256','groups':'global_group_case_sha256'}
        for typ in cases:
            cases[typ].sort(key=lambda row:row[id_keys[typ]])
        dossier={'schema_version':1,'issue':136,'release_state':'HOLD',
                 'machine_authority':AUTHORITY,'slug':slug,
                 'is_tool':slug in tool_slugs,'title':meta['title'],
                 'taxonomy_safety_gate_recorded_not_approval':meta.get('gate'),
                 'taxonomy_status_recorded_not_a_human_verdict':meta.get('status'),
                 'counts':{name:len(rows) for name,rows in cases.items()},
                 'high_priority_claim_cases':sum(c['triage_priority_not_verdict']=='REVIEW_FIRST'
                                              for c in cases['claims']),
                 'original_review_records':cases,
                 'required_independent_checks':[
                     'Visit and date the exact source and independently locate every claim.',
                     'Reconcile contributor reading scope, source-origin fallbacks and all shared URLs.',
                     'Obtain qualified review for high-consequence food/water/fire/medical advice.',
                     'Complete independent rendered-browser and QD release review.'],
                 **{f:False for f in FLAGS}}
        dossier['fingerprint_sha256']=_digest(dossier)
        dossiers.append(dossier)
    result={'schema_version':1,'issue':136,'release_state':'HOLD',
            'machine_authority':AUTHORITY,'parent_R37_fingerprint_sha256':trusted_r37_manifest_sha256,
            'original_taxonomy_sha256':_digest(taxonomy),
            'counts':expected_counts,
            'all_case_rows_preserved_without_url_deduplication':True,
            'article_dossiers':dossiers,
            'uncited_shared_url_groups_unreviewed':globally_uncited,
            'all_human_reviews_completed':False,
            'qualified_hazard_safety_check_completed':False,
            'publication_authorized':False,
            **{f:False for f in FLAGS}}
    result['fingerprint_sha256']=_digest(result)
    return result
