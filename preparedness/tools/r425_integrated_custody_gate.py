#!/usr/bin/env python3
"""R425: atomic 35-article source/export/commerce custody preflight.

READ-ONLY, private, reviewer-supplied evidence. Composes R409–R420
source/citation/prose/attribute checks and R421–R424 offer/attribution checks.
Every original fork and both HTML channels are locked to supplied byte hashes.
No publisher authentication, safety adjudication, purchase proof or release PASS.
Every CLI execution exits 2 (HARD HOLD), including structurally valid evidence.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import stat
import sys

HERE = Path(__file__).resolve().parent

def predecessor(name):
    spec = spec_from_file_location(name, HERE / (name + '.py'))
    if spec is None or spec.loader is None:
        raise RuntimeError('required predecessor missing: ' + name)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

r420 = predecessor('r420_attribute_evidence_gate')
r424 = predecessor('r424_post_cohort_custody_gate')
r409 = r420._r409
r412 = r420._r412
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
MAX_FILE = 1_000_000

def held(errors, *, source=None, campaign=None, digest=None, details=None):
    """Never authorize any release or infer human safety, paid sales or revenue."""
    return {'release_state':'DRAFT_HARD_HOLD', 'eligible':False,
        'publication_approved':False, 'qualified_safety_approved':False,
        'paid_activation_approved':False, 'verified_paid_orders':None,
        'net_revenue_per_1000_qualified_humans':None,
        'structural_integrity_ok': not errors and bool(source and source.get('integrity_ok'))
            and bool(campaign and campaign.get('structural_integrity_ok')),
        'errors':sorted(set(errors)), 'source_gate':{
            'integrity_ok':bool(source and source.get('integrity_ok')),
            'errors':list(source.get('errors',[]))[:30] if isinstance(source,dict) else ['NOT_RUN']},
        'campaign_gate':{
            'structural_integrity_ok':bool(campaign and campaign.get('structural_integrity_ok')),
            'errors':list(campaign.get('errors',[]))[:30] if isinstance(campaign,dict) else ['NOT_RUN']},
        'review_only_crosswalk_sha256':digest,
        'article_custody':details or [],
        'holds':['35 ORIGINAL ARTICLES AND UNSELECTED FORKS REQUIRE QD/SOURCE REVIEW',
                 'SITE/WORDPRESS BUILD, EXTERNAL SOURCE LINKS AND DELIVERY NOT AUTHENTICATED',
                 'SOCIAL RIGHTS, PAID SKU, MERCHANT SETTLEMENT AND NET REVENUE UNVERIFIED'],
        'evidence':'STRUCTURAL_REVIEW_ONLY_NOT_A_RELEASE_OR_SAFETY_DECISION'}

def lock_audit(original, manifest, exports, candidates, lock, *, source_pin=r409.PIN):
    """Never select a manuscript; independently account for every original fork.

    Hashes bind exact bytes in this review execution. They are NOT safety proof.
    """
    errors, details = [], []
    if not isinstance(original,dict) or not isinstance(manifest,dict) or not isinstance(lock,dict):
        return ['R425_EVIDENCE_OBJECT_MISSING'],[],None
    if set(lock) != {'schema','issue','release_state','approved','original_docket_git_blob',
                     'articles'} or type(lock.get('schema')) is not int or lock['schema']!=1 or \
       lock.get('issue')!=136 or lock.get('release_state')!='DRAFT_HARD_HOLD' or lock.get('approved') is not False or lock.get('original_docket_git_blob')!=source_pin:
        errors.append('R425_LOCK_IDENTITY_OR_APPROVAL_DRIFT')
    rows=lock.get('articles')
    original_rows=original.get('original_articles')
    manifest_rows=manifest.get('articles')
    if not all(isinstance(x,list) for x in (rows,original_rows,manifest_rows)):
        return errors+['R425_SLATE_OR_ARTICLE_ROWS_MISSING'],[],None
    if len(rows)!=35 or len(original_rows)!=35 or len(manifest_rows)!=35:
        errors.append('R425_REQUIRED_35_ARTICLE_COVERAGE')
    def indexed(seq, name):
        ans={}
        for row in seq:
            if not isinstance(row,dict) or not isinstance(row.get('slug'),str) or not SLUG.fullmatch(row['slug']) or row['slug'] in ans:
                errors.append('R425_'+name+'_DUPLICATE_OR_INVALID_SLUG')
                continue
            ans[row['slug']]=row
        return ans
    o=indexed(original_rows,'ORIGINAL')
    m=indexed(manifest_rows,'MANIFEST')
    l=indexed(rows,'LOCK')
    if set(o)!=set(m) or set(o)!=set(l) or not isinstance(exports,dict) or set(exports)!=set(o):
        errors.append('R425_ORIGINAL_MANIFEST_LOCK_EXPORT_IDENTITY_DRIFT')
    routes=set()
    for slug in sorted(set(o)|set(m)|set(l)):
        a,b,c=o.get(slug),m.get(slug),l.get(slug)
        if not all(isinstance(x,dict) for x in (a,b,c)):
            continue
        if set(c)!={'slug','canonical_path','source_ids','original_git_blobs','wordpress_sha256','preview_sha256'}:
            errors.append('R425_LOCK_ROW_SHAPE_'+slug)
        route=b.get('canonical_path')
        if not isinstance(route,str) or route!=f'/preparedness/{slug}/' or c.get('canonical_path')!=route or route in routes:
            errors.append('R425_DUPLICATE_OR_DRIFTED_ROUTE_'+slug)
        if isinstance(route,str): routes.add(route)
        ids=b.get('sources')
        if not isinstance(ids,list) or not ids or len(ids)!=len(set(x for x in ids if isinstance(x,str))) or \
           not all(isinstance(x,str) and SLUG.fullmatch(x) for x in ids) or c.get('source_ids')!=ids:
            errors.append('R425_SOURCE_ID_ORDER_OR_SET_DRIFT_'+slug)
        pins=a.get('body_candidate_git_blobs')
        if not isinstance(pins,list) or not pins or len(pins)!=len(set(x for x in pins if isinstance(x,str))) or \
           not all(isinstance(x,str) and HEX40.fullmatch(x) for x in pins) or c.get('original_git_blobs')!=sorted(pins):
            errors.append('R425_UNSELECTED_ORIGINAL_FORKS_LOST_'+slug)
        pair=exports.get(slug) if isinstance(exports,dict) else None
        if not isinstance(pair,(tuple,list)) or len(pair)!=2:
            errors.append('R425_MISSING_PAIRED_EXPORT_'+slug)
            continue
        for channel,body,expected in zip(('wordpress','preview'),pair,
                                          (c.get('wordpress_sha256'),c.get('preview_sha256'))):
            if not isinstance(body,bytes) or not 10<=len(body)<=MAX_FILE or not isinstance(expected,str) or not HEX64.fullmatch(expected):
                errors.append('R425_MISSING_OR_INVALID_EXPORT_LOCK_'+slug+'_'+channel)
            elif hashlib.sha256(body).hexdigest()!=expected:
                errors.append('R425_EXPORT_CONTENT_SHA256_DRIFT_'+slug+'_'+channel)
        if isinstance(pins,list):
            for pin in pins:
                if not isinstance(pin,str) or not HEX40.fullmatch(pin):continue
                item=candidates.get((slug,pin)) if isinstance(candidates,dict) else None
                if not isinstance(item,bytes) or not item or len(item)>MAX_FILE or r409.blob(item)!=pin:
                    errors.append('R425_MISSING_OR_CHANGED_ORIGINAL_CANDIDATE_'+slug)
        details.append({'slug':slug, 'original_candidate_count':len(pins) if isinstance(pins,list) else 0,
                        'source_id_count':len(ids) if isinstance(ids,list) else 0,
                        'paired_channels':2, 'source_and_safety_review':'HARD_HOLD'})
    if not isinstance(candidates,dict) or set(candidates)!={(slug,pin) for slug,row in o.items()
                                    for pin in row.get('body_candidate_git_blobs',[]) if isinstance(pin,str)}:
        errors.append('R425_CANDIDATE_COMPLETENESS_OR_EXTRA_OBJECT')
    if len(details)!=35:
        errors.append('R425_INCOMPLETE_ARTICLE_CUSTODY')
    if errors:return sorted(set(errors)),details,None
    canonical_manifest={**manifest, 'articles': [m[s] for s in sorted(m)]}
    material=[source_pin,hashlib.sha256(json.dumps(canonical_manifest,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()]
    for slug in sorted(l):
        row=l[slug]
        material.append([slug,row['canonical_path'],row['source_ids'],row['original_git_blobs'],
                         row['wordpress_sha256'],row['preview_sha256']])
    raw=json.dumps(material,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
    digest=hashlib.sha256(b'FV-R425-REVIEW-ONLY-EVIDENCE-LOCK\0'+raw).hexdigest()
    return [],details,digest

def validate(original,manifest,exports,candidates,lock,receipt,*,raw_original=None):
    errors, details, digest=lock_audit(original,manifest,exports,candidates,lock)
    source=None
    if raw_original is None or r409.blob(raw_original)!=r409.PIN:
        errors.append('R425_AUTHENTIC_ORIGINAL_DOCKET_GIT_BLOB_MISSING')
    if not errors:
        try:
            source=r420.check(original,manifest,exports,candidates,raw_original=raw_original)
            if not source.get('integrity_ok'):
                errors.append('R425_INHERITED_R409_TO_R420_SOURCE_CUSTODY_FAILED')
        except (ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError,AttributeError,RecursionError) as e:
            errors.append('R425_INHERITED_SOURCE_GATE_EXCEPTION_'+type(e).__name__)
    try:
        campaign=r424.validate(receipt)
        if not campaign.get('structural_integrity_ok'):
            errors.append('R425_CAMPAIGN_OR_OFFER_EVIDENCE_SHAPE_FAILED')
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError,AttributeError,RecursionError) as e:
        errors.append('R425_CAMPAIGN_GATE_EXCEPTION_'+type(e).__name__)
        campaign=None
    return held(errors,source=source,campaign=campaign,digest=digest,details=details)

def safe_path(path,root):
    """Reject symlinks anywhere below reviewer-selected root, not just leaf."""
    root=Path(root).absolute()
    path=Path(path).absolute()
    if path!=root and root not in path.parents:raise ValueError('path outside private review root')
    rel=path.relative_to(root)
    cursor=root
    if stat.S_ISLNK(cursor.lstat().st_mode):raise ValueError('symlinked review root')
    for part in rel.parts:
        if part in ('','.', '..'):raise ValueError('unsafe path')
        cursor=cursor/part
        if stat.S_ISLNK(cursor.lstat().st_mode):raise ValueError('symlinked evidence path')
    return path

def read_json(path,root):
    safe_path(path,root)
    raw=r409.read_original(path)
    return json.loads(raw.decode('utf-8'),object_pairs_hook=r409.unique_pairs,parse_constant=lambda c: (_ for _ in ()).throw(ValueError('nonstandard JSON constant'))),raw

def load_bundle(original_path,manifest_path,export_root,candidate_root,lock_path,receipt_path):
    """Read all authentic original/export/lock bytes before any integrated check."""
    roots=[p.parent for p in (original_path,manifest_path,lock_path,receipt_path)]
    original,raw=read_json(original_path,roots[0])
    manifest,_=read_json(manifest_path,roots[1])
    lock,_=read_json(lock_path,roots[2])
    receipt=r424.bounded_receipt(safe_path(receipt_path,roots[3]))
    exports,candidates={},{}
    entries=original.get('original_articles',[]) if isinstance(original,dict) else []
    if len(entries)!=35:raise ValueError('not 35 original article identities')
    slugs=[]
    for article in entries:
        slug=article.get('slug') if isinstance(article,dict) else None
        if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in slugs:
            raise ValueError('invalid or duplicate article path')
        slugs.append(slug)
        pair=[]
        for channel in ('wordpress','preview'):
            p=safe_path(export_root/channel/(slug+'.html'),export_root)
            b=r409.read_original(p,MAX_FILE)
            pair.append(b)
        exports[slug]=tuple(pair)
        pins=article.get('body_candidate_git_blobs')
        if not isinstance(pins,list) or not pins:raise ValueError('missing original forks')
        for pin in pins:
            if not isinstance(pin,str) or not HEX40.fullmatch(pin):raise ValueError('invalid original Git pin')
            p=safe_path(candidate_root/slug/(pin+'.txt'),candidate_root)
            candidates[slug,pin]=r412.checked_candidate_read(p,root=candidate_root)
    for channel in ('wordpress','preview'):
        directory=safe_path(export_root/channel,export_root)
        if {p.name for p in directory.iterdir()}!={slug+'.html' for slug in slugs}:
            raise ValueError('missing/extra HTML export file in '+channel)
    if {p.name for p in Path(candidate_root).iterdir()}!=set(slugs):
        raise ValueError('missing/extra private candidate article directory')
    for a in entries:
        directory=safe_path(candidate_root/a['slug'],candidate_root)
        if {p.name for p in directory.iterdir()}!={p+'.txt' for p in a['body_candidate_git_blobs']}:
            raise ValueError('missing/extra original candidate in '+a['slug'])
    return original,manifest,exports,candidates,lock,receipt,raw

def main(argv=None):
    ap=argparse.ArgumentParser(description='R425 read-only integrated original-source/paired-export/offer HOLD gate')
    for name in ('original','manifest','export_root','private_candidate_root','evidence_lock','campaign_receipt'):
        ap.add_argument(name,type=Path)
    args=ap.parse_args(argv)
    try:
        original,manifest,exports,candidates,lock,receipt,raw=load_bundle(
            args.original,args.manifest,args.export_root,args.private_candidate_root,
            args.evidence_lock,args.campaign_receipt)
        result=validate(original,manifest,exports,candidates,lock,receipt,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError,AttributeError,RecursionError) as e:
        result=held(['R425_AUTHENTIC_COMPLETE_EVIDENCE_UNAVAILABLE_'+type(e).__name__])
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':
    sys.exit(main())
