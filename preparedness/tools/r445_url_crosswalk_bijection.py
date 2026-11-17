#!/usr/bin/env python3
"""R445: read-only exact URL/source crosswalk custody. Never QD/publish/commerce."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

R397_BLOB = '86d22a1d504c93db7689b914e2202a7845b648e2'
DRAFT = 'DRAFT_HARD_HOLD'
HEX40 = re.compile(r'[0-9a-f]{40}\Z')

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def safe_url(url: object) -> bool:
    if not isinstance(url,str) or len(url)>2048 or any(ord(c)<33 or ord(c)==127 for c in url):
        return False
    try:
        p=urlsplit(url)
        return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password and p.port in (None,443) and '\\' not in url and not any(c in url for c in ('\u202e','\u202d','\u2066','\u2067','\u2068','\u2069'))
    except ValueError:
        return False

def check_graph(d: object) -> dict:
    errors=[]
    if not isinstance(d,dict):d={};errors.append('DOCKET_NOT_OBJECT')
    pins=d.get('branch_pins');pins=pins if isinstance(pins,list) else []
    branches={p.get('branch') for p in pins if isinstance(p,dict) and isinstance(p.get('branch'),str)}
    if len(pins)!=9 or len(branches)!=9:errors.append('NINE_CONTRIBUTORS_NOT_PRESERVED')
    rows=d.get('all_original_source_id_crosswalk');rows=rows if isinstance(rows,list) else []
    seen=set();urls=defaultdict(set);variants={};count=0
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or not isinstance(row.get('source_id'),str):
            errors.append('INVALID_SOURCE_ROW:'+str(i));continue
        sid=row['source_id']
        if sid in seen:errors.append('DUPLICATE_SOURCE_ID:'+sid)
        seen.add(sid)
        vals=row.get('variants')
        if not isinstance(vals,list) or not vals:errors.append('SOURCE_VARIANTS_MISSING:'+sid);continue
        branches_for_id=set();triples=set()
        for j,v in enumerate(vals):
            count+=1
            if not isinstance(v,dict):errors.append('INVALID_VARIANT:'+sid+':'+str(j));continue
            branch,blob,url=v.get('branch'),v.get('source_blob'),v.get('url')
            if not isinstance(branch,str):branch=None
            if not isinstance(blob,str):blob=None
            if not isinstance(url,str):url=None
            if branch not in branches:errors.append('UNKNOWN_VARIANT_BRANCH:'+sid+':'+str(j))
            if branch in branches_for_id:errors.append('REPEATED_ID_BRANCH:'+sid+':'+str(j))
            branches_for_id.add(branch)
            if not isinstance(blob,str) or not HEX40.fullmatch(blob):errors.append('INVALID_SOURCE_BLOB:'+sid+':'+str(j))
            if not safe_url(url):errors.append('INVALID_SOURCE_URL:'+sid+':'+str(j))
            else:urls[url].add(sid)
            triples.add((branch,blob,url))
        variants[sid]=triples
    if len(rows)!=203 or len(seen)!=203:errors.append('SOURCE_ID_COUNT_DRIFT')
    if count!=280:errors.append('SOURCE_OCCURRENCE_COUNT_DRIFT')
    if len(urls)!=181:errors.append('EXACT_URL_COUNT_DRIFT')
    actual={u:ids for u,ids in urls.items() if len(ids)>1}
    groups=d.get('shared_exact_url_review_groups');groups=groups if isinstance(groups,list) else []
    listed={}
    for i,g in enumerate(groups):
        if not isinstance(g,dict) or not isinstance(g.get('url'),str) or not isinstance(g.get('ids'),list):
            errors.append('INVALID_URL_REVIEW_GROUP:'+str(i));continue
        u=g['url'];ids=g['ids']
        if u in listed:errors.append('DUPLICATE_REVIEW_GROUP_URL:'+u)
        if len(ids)!=len(set(map(str,ids))):errors.append('DUPLICATE_GROUP_ID:'+u)
        if any(not isinstance(x,str) for x in ids):errors.append('NONSTRING_GROUP_SOURCE_ID:'+u)
        if g.get('review_required') is not True:errors.append('SHARED_URL_REVIEW_REMOVED:'+u)
        listed[u]=set(map(str,ids))
    if len(groups)!=17 or len(actual)!=17:errors.append('SHARED_URL_COUNT_DRIFT')
    for url in sorted(set(listed)|set(actual)):
        if listed.get(url)!=actual.get(url):errors.append('EXACT_URL_BIJECTION_DRIFT:'+url)
    disputes=d.get('source_evidence_disputes');disputes=disputes if isinstance(disputes,list) else []
    disputed_ids=set()
    for i,q in enumerate(disputes):
        if not isinstance(q,dict):errors.append('INVALID_DISPUTE:'+str(i));continue
        sid=q.get('source_id')
        if not isinstance(sid,str):errors.append('INVALID_DISPUTED_ID:'+str(i));sid=str(sid)
        if sid in disputed_ids:errors.append('DUPLICATE_DISPUTED_ID:'+str(sid))
        disputed_ids.add(sid)
        if q.get('decision')!='HUMAN_REVIEW_REQUIRED' or q.get('selected_record') is not None:
            errors.append('PREMATURE_SOURCE_SELECTION:'+str(sid))
        vals=q.get('variants')
        if not isinstance(vals,list) or len(vals)<2:errors.append('DISPUTE_VARIANTS_LOST:'+str(sid));continue
        for j,v in enumerate(vals):
            if not isinstance(v,dict):errors.append('INVALID_DISPUTED_VARIANT:'+str(sid));continue
            parts=tuple(x if isinstance(x,str) else None for x in (v.get('branch'),v.get('source_blob'),v.get('url')))
            if parts not in variants.get(sid,set()):
                errors.append('DISPUTE_CROSSWALK_VARIANT_MISMATCH:'+str(sid)+':'+str(j))
            if not isinstance(v.get('supports_exact'),str) or not v['supports_exact'].strip() or not isinstance(v.get('reading_scope_notes_exact'),str) or not v['reading_scope_notes_exact'].strip():
                errors.append('DISPUTE_SCOPE_LOST:'+str(sid)+':'+str(j))
    if len(disputes)!=5:errors.append('FIVE_DISPUTES_CHANGED')
    forks=d.get('original_fork_disputes');forks=forks if isinstance(forks,list) else []
    for i,f in enumerate(forks):
        if not isinstance(f,dict):errors.append('INVALID_FORK:'+str(i));continue
        if f.get('decision')!='HUMAN_REVIEW_REQUIRED' or f.get('selected_sha') is not None:
            errors.append('PREMATURE_FORK_SELECTION:'+str(i))
        if f.get('requires_reading_depth_review') is not True or f.get('requires_source_citation_review') is not True:
            errors.append('FORK_REVIEW_DEPTH_LOST:'+str(i))
        v=f.get('variants')
        if not isinstance(v,list) or len(v)<2:errors.append('FORK_VARIANTS_LOST:'+str(i))
    if len(forks)!=9:errors.append('NINE_FORKS_CHANGED')
    return {'errors':sorted(set(errors)),'articles':len(d.get('original_articles',[])) if isinstance(d.get('original_articles'),list) else 0,
            'source_ids':len(seen),'occurrences':count,'exact_urls':len(urls),'review_groups':len(actual),
            'disputes':len(disputes),'forks':len(forks),'release_state':DRAFT,'qd_pass':False,
            'publishable':False,'paid_offer_verified':False}

def audit(d: object, raw: bytes|None=None, observed_heads: dict|None=None) -> dict:
    r=check_graph(d)
    if not isinstance(d,dict):d={}
    if d.get('repo')!='finalvestigestudios/final-vestige-site-layer' or d.get('issue')!=136 or d.get('parent_conversion_issue')!=820 or d.get('schema')!=1:
        r['errors'].append('DOCKET_OWNER_DRIFT')
    if d.get('release_state')!=DRAFT or any(d.get(k) is not False for k in ('publication_approved','qualified_safety_approved','automatic_variant_selection','merchant_offer_verified')):
        r['errors'].append('FALSE_RELEASE_OR_COMMERCE_APPROVAL')
    if raw is None or git_blob(raw)!=R397_BLOB:r['errors'].append('AUTHENTIC_R397_BYTES_MISSING')
    pins=d.get('branch_pins');pins=pins if isinstance(pins,list) else []
    names={v.get('branch'):v.get('sha') for v in pins if isinstance(v,dict) and isinstance(v.get('branch'),str) and isinstance(v.get('sha'),str)}
    if observed_heads is None or observed_heads!=names:r['errors'].append('CURRENT_BRANCH_SHA_EVIDENCE_MISSING_OR_DRIFTED')
    r['errors']=sorted(set(r['errors']))
    r['graph_structural_pass']=not r['errors']
    r['release_state']=DRAFT
    return r

def main(argv=None):
    p=argparse.ArgumentParser(description='R445 source/URL custody; always hard hold')
    p.add_argument('docket',type=Path)
    p.add_argument('--observed-heads',type=Path)
    a=p.parse_args(argv)
    try:
        raw=a.docket.read_bytes();d=json.loads(raw)
        heads=json.loads(a.observed_heads.read_text()) if a.observed_heads else None
        report=audit(d,raw,heads)
    except (OSError,ValueError,UnicodeError,TypeError,json.JSONDecodeError):report=audit({})
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2

if __name__=='__main__':raise SystemExit(main())
