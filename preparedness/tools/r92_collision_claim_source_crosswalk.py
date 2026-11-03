#!/usr/bin/env python3
"""R92 PRIVATE HOLD: literal shared-URL source/citation custody and reviewer workorders.

An identical URL is NOT an identical reading, assertion, human link check,
independent editorial approval, medical safety verdict, or permission to publish.
Purely local, deterministic, read-only. No URLs are fetched or rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re

SCHEMA = 'r92-literal-url-source-citation-scope-private-hold-v1'
PARENT_SCHEMA = 'r91-historical-citation-claim-boundary-private-hold-v1'
REVIEW = 'NOT_REVIEWED'
HOLD = 'HOLD'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
EXPECTED = {'documents': 41, 'article': 35, 'tool': 6,
            'citation_occurrences': 2173, 'source_variant_edges': 2359,
            'complete_DOM_blocks': 4070, 'distinct_source_variants': 242,
            'unpaired_historical_reviews_preserved': 11,
            'raw_source_rows': 224, 'unique_source_urls': 186,
            'shared_url_groups': 30}


class Gate(ValueError):
    """Evidence, literal source identity or publication HOLD was altered."""


def need(condition, message):
    if not condition:
        raise Gate(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def parent_module():
    path = Path(__file__).with_name('r91_historical_citation_claim_boundary.py')
    need(path.is_file() and not path.is_symlink(), 'R91 parent missing')
    spec = importlib.util.spec_from_file_location('r92_r91_parent', path)
    need(spec is not None and spec.loader is not None, 'R91 parent loader missing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def protect_csv(value):
    text = str(value)
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else text


def source_row(source):
    need(type(source) is dict and type(source.get('_origin')) is str
         and source['_origin'], 'missing literal contributor identity')
    origin = source['_origin']
    raw = {k:v for k,v in source.items() if k != '_origin'}
    need(all(type(raw.get(k)) is str and raw[k] for k in ('id','url','title')),
         'missing literal source id/url/title')
    need(raw['url'].startswith('https://'), 'non-HTTPS literal research URL')
    return {'origin': origin, 'source': raw}


def check_parent(parent):
    need(type(parent) is dict and parent.get('schema') == PARENT_SCHEMA
         and parent.get('issue') == 136 and parent.get('release_state') == HOLD
         and parent.get('may_publish') is False
         and parent.get('medical_safety_approved') is False,
         'R91 ancestor release/safety state changed')
    for key in ('human_source_approvals','human_claim_approvals',
                'qualified_safety_approvals','independent_QD_approvals'):
        need(type(parent.get(key)) is int and parent[key] == 0,
             'R91 ancestor falsely approved: '+key)
    need(parent.get('sha256_seal') == digest(
         {k:v for k,v in parent.items() if k != 'sha256_seal'}),
         'R91 ancestor evidence digest invalid')
    need(type(parent.get('complete_R90_original_evidence_UNABRIDGED_NOT_APPROVED')) is dict
         and type(parent.get('all_literal_citation_claim_boundary_review_rows_NOT_APPROVED')) is list
         and type(parent.get('counts')) is dict,
         'R91 full original evidence unavailable')


def index(lib, parent, *, expected=None, allow_historical_body_drift=False):
    """Recompute collision-to-article literal links, preserving full sealed R91.

    The library may be the original read-only build.Library or a synthetic
    in-memory fixture. Nothing is modified. Caller supplies optional census.
    """
    check_parent(parent)
    need(type(lib.crosswalk) is dict and type(lib.crosswalk.get('groups')) is list
         and type(lib.source_variants) is dict and type(lib.articles) is dict,
         'original crosswalk/library missing')
    groups = lib.crosswalk['groups']
    need(len(groups) == len(lib.crosswalk_groups), 'duplicate crosswalk URLs')
    source_urls = defaultdict(list)
    for sid, variants in sorted(lib.source_variants.items()):
        need(type(sid) is str and type(variants) is list and variants,
             'invalid original source variants')
        for variant in variants:
            need(variant.get('id') == sid, 'source ID/variant index mismatch')
            snapshot = source_row(variant)
            source_urls[snapshot['source']['url']].append(snapshot)
    collision = {u:v for u,v in source_urls.items() if len(v)>1}
    need(set(collision) == set(lib.crosswalk_groups),
         'crosswalk omits or invents a literal shared URL')
    need(lib.crosswalk.get('raw_source_rows') == sum(map(len,source_urls.values()))
         and lib.crosswalk.get('unique_source_urls') == len(source_urls)
         and lib.crosswalk.get('duplicate_url_groups') == len(collision),
         'original raw/unique/collision census changed')

    original_rows = parent['all_literal_citation_claim_boundary_review_rows_NOT_APPROVED']
    original = {}
    for row in original_rows:
        key = (row['kind'], row['slug'], row['citation_ordinal'])
        need(key not in original, 'duplicate R91 original citation')
        need(row.get('may_publish') is False and
             all(row.get(k)==REVIEW for k in ('human_source_review',
                 'human_claim_support','qualified_safety_review','independent_QD_review')),
             'R91 literal citation human review changed')
        original[key] = row['literal_source_ID']
    need(parent['counts'].get('citation_occurrences') == len(original),
         'R91 citation census mismatch')

    cite_rows, actual, document_routes, mismatch_rows = [], {}, set(), []
    doc_counts = Counter()
    for slug, meta in sorted(lib.articles.items()):
        need(type(slug) is str and type(meta) is dict and
             type(meta.get('_body')) is str, 'missing original article body')
        kind = 'tool' if meta.get('kind') == 'tool' else 'article'
        doc_counts[kind] += 1
        need(meta.get('status',{}).get('publish') == 'draft',
             'unreviewed article/tool publication state changed')
        route = lib.url_path(slug)
        need(type(route) is str and route.startswith('/preparedness/')
             and route not in document_routes and route.endswith('/'),
             'duplicate or non-private Preparedness route')
        document_routes.add(route)
        for ordinal, match in enumerate(CITE.finditer(meta['_body']),1):
            sid = match.group(1)
            key = (kind,slug,ordinal)
            need(key not in actual, 'duplicate original citation location')
            actual[key]=sid
            if original.get(key) != sid:
                mismatch_rows.append({
                    'kind':kind,'slug':slug,'citation_ordinal':ordinal,
                    'current_literal_body_source_ID_NOT_EQUIVALENT':sid,
                    'sealed_R91_source_ID_OR_NONE':original.get(key),
                    'lexical_drift_cue_NOT_ERROR_VERDICT':
                        'BODY_CITATION_DIFFERS_FROM_FROZEN_R91_CONTEXT',
                    'human_claim_support':REVIEW,'qualified_safety_review':REVIEW,
                    'may_publish':False,
                })
                need(allow_historical_body_drift,
                     'citation ID/ordinal differs from sealed R91: '+
                     repr((key,sid,original.get(key))))
            source = lib.source_for(meta,sid)
            snapshot = source_row(source)
            url = snapshot['source']['url']
            # An article is bound to its own contributor or explicit base,
            # not an arbitrary third-party source record at the same URL.
            own = lib.article_origins.get(slug,'base')
            need(snapshot['origin'] in (own,'base'),
                 'citation borrowed unrelated contributor research scope')
            need(snapshot in source_urls[url], 'citation source reading not in originals')
            if url in collision:
                cite_rows.append({
                    'kind':kind,'slug':slug,'route_PRIVATE_NOT_FOR_IMPORT':route,
                    'citation_ordinal':ordinal,'literal_source_ID':sid,
                    'literal_url_UNMODIFIED':url,
                    'source_variant_SHA256':digest(snapshot),
                    'R91_prior_literal_source_ID_NOT_EQUIVALENT':original.get(key),
                    'source_match_to_R91_claim_NOT_PROVEN':original.get(key)==sid,
                    'source_origin':snapshot['origin'],
                    'article_author_origin':own,
                    'human_source_review':REVIEW,'human_link_check':REVIEW,
                    'qualified_safety_review':REVIEW,'may_publish':False,
                })
    for key in sorted(set(original)-set(actual)):
        mismatch_rows.append({
            'kind':key[0],'slug':key[1],'citation_ordinal':key[2],
            'current_literal_body_source_ID_NOT_EQUIVALENT':None,
            'sealed_R91_source_ID_OR_NONE':original[key],
            'lexical_drift_cue_NOT_ERROR_VERDICT':
                'FROZEN_R91_CITATION_NOT_IN_CURRENT_RAW_BODY',
            'human_claim_support':REVIEW,'qualified_safety_review':REVIEW,
            'may_publish':False,
        })
    need(allow_historical_body_drift or actual==original,
         'original citation lost, inserted or replaced')
    # The frozen full-slate reviewer evidence covers 41 planned documents,
    # but the *current* WordPress draft generator contains 35 articles and
    # only one implemented tool. The remaining five tools are NOT draft files.
    # Never counterfeit a WordPress-ready page to satisfy the historical count.
    planned_tools = {x['slug']:x for x in getattr(lib,'taxonomy',{}).get('tools',[])}
    current_tools = {slug for slug,meta in lib.articles.items()
                     if meta.get('kind')=='tool'}
    missing_tool_plans = sorted(set(planned_tools) - current_tools)
    if expected is not None:
        need(doc_counts['article']==35 and doc_counts['tool']==1
             and len(planned_tools)==6 and len(missing_tool_plans)==5
             and all(planned_tools[x].get('status')=='not-started'
                     for x in missing_tool_plans),
             'actual 35 article + one implemented tool census changed')
        need(parent['counts'].get('documents')==41 and
             parent['counts'].get('article')==35 and
             parent['counts'].get('tool')==6,
             'frozen 41-document reviewer census changed')
    else:
        need(doc_counts['article']==parent['counts'].get('article') and
             doc_counts['tool']==parent['counts'].get('tool') and
             sum(doc_counts.values())==parent['counts'].get('documents'),
             'synthetic document/tool identities changed')

    by_url = defaultdict(list)
    for row in cite_rows:
        by_url[row['literal_url_UNMODIFIED']].append(row)
    dossiers=[]
    for url in sorted(collision):
        item = lib.crosswalk_groups[url]
        need(type(item) is dict and item.get('url') == url,
             'literal crosswalk URL key disagrees')
        need(item.get('review_status') == 'pending-human-source-and-reading-scope-review',
             'shared source scope marked resolved without independent human baseline')
        actual_variants = sorted(collision[url],key=digest)
        declared = item.get('variants')
        need(type(declared) is list and sorted(declared,key=digest)==actual_variants,
             'source variant provenance, reading depth or metadata altered')
        need(len({(r['origin'],r['source']['id']) for r in actual_variants})
             ==len(actual_variants), 'duplicate contributor/source record')
        literal_ids=sorted({r['source']['id'] for r in actual_variants})
        readings=sorted({r['source'].get('supports') or '' for r in actual_variants})
        for v in actual_variants:
            need(v['source'].get('human_link_check') is not True,
                 'source now has new human-check evidence: rebaseline required')
        citations=sorted(by_url[url],key=lambda x:(x['kind'],x['slug'],x['citation_ordinal']))
        dossiers.append({
            'literal_url_UNMODIFIED':url,
            'all_distinct_original_source_readings_UNABRIDGED_NOT_APPROVED':actual_variants,
            'distinct_source_record_SHA256':[digest(v) for v in actual_variants],
            'distinct_literal_source_IDs':literal_ids,
            'reading_scope_variants_count':len(readings),
            'source_ID_count':len(literal_ids),
            'review_risk_cues_NOT_VERDICTS': sorted(
                (['DIFFERENT_LITERAL_SOURCE_IDS_SHARE_URL'] if len(literal_ids)>1 else [])+
                (['READING_SCOPE_STATEMENTS_DIFFER'] if len(readings)>1 else [])+
                (['REPEATED_ORIGIN_SPECIFIC_SOURCE_ID'] if len(literal_ids)<len(actual_variants) else [])+
                (['CITED_IN_RELEASE_CANDIDATE'] if citations else ['NO_RC_CITATION_FOUND'])),
            'all_literal_release_candidate_citation_links_NOT_APPROVED':citations,
            'human_url_review':REVIEW,'human_reading_scope_review':REVIEW,
            'qualified_safety_review':REVIEW,'independent_QD_review':REVIEW,
            'may_publish':False,
        })
    report = {
        'schema':SCHEMA,'issue':136,'release_state':HOLD,
        'may_publish':False,'medical_safety_approved':False,
        'human_source_approvals':0,'human_claim_approvals':0,
        'qualified_safety_approvals':0,'independent_QD_approvals':0,
        'complete_R91_original_evidence_UNABRIDGED_NOT_APPROVED':parent,
        'all_literal_shared_URL_review_dossiers_NOT_APPROVED':dossiers,
        'all_R91_vs_current_raw_body_citation_drift_workorders_NOT_APPROVED':mismatch_rows,
        'planned_tool_slots_NOT_CURRENT_WORDPRESS_DRAFTS':missing_tool_plans,
        'counts':{
            **{k:parent['counts'][k] for k in (
              'documents','article','tool','citation_occurrences',
              'source_variant_edges','complete_DOM_blocks',
              'distinct_source_variants','unpaired_historical_reviews_preserved')},
            'raw_source_rows':sum(map(len,source_urls.values())),
            'unique_source_urls':len(source_urls),
            'shared_url_groups':len(dossiers),
            'current_wordpress_draft_article_files':doc_counts['article'],
            'current_wordpress_draft_tool_files':doc_counts['tool'],
            'current_wordpress_draft_document_files':sum(doc_counts.values()),
            'planned_tools_without_wordpress_draft_files':len(missing_tool_plans),
            'current_raw_body_citation_occurrences':len(actual),
            'historical_raw_body_citation_alignment_review_cues':len(mismatch_rows),
            'shared_url_citation_occurrences':len(cite_rows),
            'shared_urls_with_rc_citations':sum(bool(d[
              'all_literal_release_candidate_citation_links_NOT_APPROVED']) for d in dossiers),
            'separate_source_id_shared_url_groups':sum(d['source_ID_count']>1 for d in dossiers),
        },
    }
    report['sha256_seal']=digest(report)
    if expected is not None:
        need(all(report['counts'].get(k)==v for k,v in expected.items()),
             'strict complete-slate and URL census changed')
    return report


def verify(report, lib, parent, *, expected=None, allow_historical_body_drift=False):
    need(type(report) is dict and report.get('schema')==SCHEMA
         and report.get('issue')==136 and report.get('release_state')==HOLD
         and report.get('may_publish') is False
         and report.get('medical_safety_approved') is False,
         'R92 false release or qualified-safety status')
    need(all(type(report.get(k)) is int and report[k]==0 for k in (
         'human_source_approvals','human_claim_approvals',
         'qualified_safety_approvals','independent_QD_approvals')),
         'R92 false source/claim/qualified safety/QD approval')
    need(report.get('sha256_seal')==digest(
         {k:v for k,v in report.items() if k!='sha256_seal'}),
         'R92 evidence digest mismatch')
    need(report==index(lib,parent,expected=expected,
         allow_historical_body_drift=allow_historical_body_drift),
         'R92 literal URL, citation or source evidence changed')


def live():
    r91=parent_module()
    parent, ancestor=r91.live()
    r91.verify(parent,ancestor,expected=r91.EXPECTED)
    # Same trusted read-only Library used by native validator/build.
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    import build
    lib=build.Library()
    report=index(lib,parent,expected=EXPECTED,allow_historical_body_drift=True)
    verify(report,lib,parent,expected=EXPECTED,allow_historical_body_drift=True)
    return report,lib,parent


def private_csv(report,lib,parent,*,expected=None,allow_historical_body_drift=False):
    verify(report,lib,parent,expected=expected,
           allow_historical_body_drift=allow_historical_body_drift)
    stream=io.StringIO(newline='')
    writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(('literal_url_UNMODIFIED','original_source_records',
        'distinct_source_IDs','RC_citation_occurrences',
        'review_risk_cues_NOT_SAFETY_FINDINGS','human_source_review',
        'qualified_safety_review','may_publish'))
    for item in report['all_literal_shared_URL_review_dossiers_NOT_APPROVED']:
        writer.writerow([protect_csv(item['literal_url_UNMODIFIED']),
            len(item['all_distinct_original_source_readings_UNABRIDGED_NOT_APPROVED']),
            item['source_ID_count'],
            len(item['all_literal_release_candidate_citation_links_NOT_APPROVED']),
            protect_csv(';'.join(item['review_risk_cues_NOT_VERDICTS'])),
            REVIEW,REVIEW,'FALSE'])
    return stream.getvalue()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-csv-stdout',action='store_true')
    args=parser.parse_args(argv)
    report,lib,parent=live()
    if args.private_csv_stdout:
        print(private_csv(report,lib,parent,expected=EXPECTED,
                  allow_historical_body_drift=True),end='')
    else:
        print(json.dumps({'schema':SCHEMA,'release_state':HOLD,
             'may_publish':False,'counts':report['counts'],
             'sha256_seal':report['sha256_seal']},sort_keys=True))


if __name__=='__main__':
    main()
