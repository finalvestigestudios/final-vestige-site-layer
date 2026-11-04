#!/usr/bin/env python3
"""R115 original 35-author body/scoped citation custody (read only, always HOLD).

The ledger records Git blobs from a specific review, not factual or safety proof.
A mismatch cannot be automatically substituted with a newer contributor revision.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

SCHEMA='fv-preparedness-r115-35-article-frozen-read-census-NOT-SAFETY-v1'
CITE=re.compile(rb'\{\{cite:([a-z0-9-]+)\}\}')
SLUG=re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

class EvidenceHold(ValueError):pass

def demand(ok,message):
    if not ok:raise EvidenceHold(message)

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()

def verify(taxonomy,ledger,articles):
    """articles maps each slug to (raw body bytes, metadata dict). No mutations."""
    demand(isinstance(taxonomy,dict) and taxonomy.get('base_path')=='/preparedness/',
           'TAXONOMY_BASE_DRIFT')
    slate=taxonomy.get('slate')
    demand(isinstance(slate,list) and len(slate)==35 and
           all(isinstance(x,dict) for x in slate),'35_SLATE_REQUIRED')
    demand({x.get('n') for x in slate}==set(range(1,36)),'DUPLICATE_OR_MISSING_ARTICLE_NUMBER')
    demand(type(ledger) is dict and ledger.get('schema')==SCHEMA and
           ledger.get('reference_commit') and ledger.get('release_state')=='HOLD' and
           ledger.get('may_publish') is False and
           ledger.get('source_claim_truth_verified') is False and
           ledger.get('qualified_safety_review_verified') is False and
           ledger.get('independent_QD_PASS') is False,
           'FROZEN_LEDGER_OR_APPROVAL_STATE_MISSING')
    rows=ledger.get('rows_NOT_APPROVED')
    demand(type(rows) is list and len(rows)==35 and ledger.get('article_count')==35,
           'FROZEN_ROSTER_MISSING')
    tax={x['n']:x for x in slate}
    demand({x.get('n') for x in rows}==set(range(1,36)) and
           len({x.get('slug') for x in rows})==35,'FROZEN_ROSTER_DUPLICATE')
    demand(set(articles)=={x['slug'] for x in rows},'ARTICLE_FILES_ROSTER_CHANGED')
    paths=set();citations=0;scopes=0;states={'pending':0,'approved':0,'not-required':0}
    for row in sorted(rows,key=lambda r:r['n']):
        n=row['n']; s=row['slug']; t=tax[n]
        demand(all(isinstance(x,str) and SLUG.fullmatch(x) for x in
                   (s,row.get('section'),t.get('section'),t.get('slug'))),
               'UNSAFE_CANONICAL_COMPONENT')
        demand(s==t['slug'] and row['section']==t['section'] and
               row.get('track')==t.get('track'), 'FROZEN_TAXONOMY_DRIFT')
        path='/preparedness/'+t['section']+'/'+s+'/'
        demand(path not in paths,'DUPLICATE_CANONICAL_URL')
        paths.add(path)
        raw,meta=articles[s]
        demand(type(raw) is bytes and type(meta) is dict,'INVALID_BODY_OR_META')
        demand(git_blob(raw)==row.get('body_git_blob_oid'),'ORIGINAL_BODY_CHANGED_'+s)
        demand(meta.get('slug')==s and meta.get('section')==t['section'] and
               meta.get('track')==t.get('track'),'AUTHOR_IDENTITY_DRIFT_'+s)
        status=meta.get('status')
        demand(type(status) is dict and status.get('publish')=='draft',
               'AUTHOR_PUBLICATION_STATE_DRIFT_'+s)
        scope=meta.get('source_use')
        demand(type(scope) is dict and all(type(k) is str and type(v) is str and v.strip()
               for k,v in scope.items()),'AUTHOR_READING_SCOPE_MISSING_'+s)
        mentions=[x.decode() for x in CITE.findall(raw)]
        demand(len(mentions)==row.get('raw_citation_occurrences'),
               'ORIGINAL_CITATION_OCCURRENCES_DRIFT_'+s)
        demand(set(mentions)==set(scope) and len(scope)==row.get('distinct_author_scoped_source_ids'),
               'AUTHOR_CITATION_SCOPE_DRIFT_'+s)
        safety=meta.get('safety_review')
        demand(type(safety) is dict and safety.get('state') in states,
               'SAFETY_REVIEW_METADATA_DRIFT_'+s)
        states[safety['state']]+=1
        citations+=len(mentions);scopes+=len(scope)
    demand(citations==ledger.get('raw_citation_occurrences_total') and
           scopes==ledger.get('article_scoped_source_id_total_NOT_GLOBAL_UNIQUE'),
           'AUTHOR_CITATION_TOTALS_DRIFT')
    demand(states==ledger.get('self_reported_safety_metadata_counts'),
           'HISTORICAL_SAFETY_STATES_CHANGED_NEEDS_HUMAN_ADJUDICATION')
    return {'schema':'fv-preparedness-r115-corpus-object-check-HOLD-v1','issue':136,
            'frozen_article_count':35,'unique_urls':len(paths),
            'original_raw_citation_occurrences':citations,
            'original_author_scoped_source_ids_NOT_GLOBAL_UNIQUE':scopes,
            'author_scope_mismatches':0,'unaltered_body_git_objects':35,
            'source_claim_truth_verified':False,'qualified_medical_safety_verified':False,
            'independent_QD_PASS':False,'release_state':'HOLD',
            'may_publish':False,'may_merge':False,'cms_writes':False}

def check_checkout(root):
    root=Path(root)/'preparedness'
    tax=json.loads((root/'taxonomy.json').read_text('utf-8'))
    ledger=json.loads((root/'docs/R115_FROZEN_ALL_35_AUTHOR_BODY_CENSUS.json').read_text('utf-8'))
    articles={}
    for row in ledger['rows_NOT_APPROVED']:
        s=row['slug']
        if not isinstance(s,str) or not SLUG.fullmatch(s):
            raise EvidenceHold('UNSAFE_LEDGER_FILE_PATH')
        folder=root/'content/articles'
        articles[s]=((folder/(s+'.body.html')).read_bytes(),
                     json.loads((folder/(s+'.meta.json')).read_text('utf-8')))
    return verify(tax,ledger,articles)

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--repo-root',default='.')
    args=p.parse_args()
    try:
        print(json.dumps(check_checkout(args.repo_root),sort_keys=True,indent=2));return 0
    except (EvidenceHold,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'release_state':'HOLD','integrity':'FAILED_CLOSED',
                          'may_publish':False,'reason':str(exc)},sort_keys=True));return 2
if __name__=='__main__':raise SystemExit(main())
