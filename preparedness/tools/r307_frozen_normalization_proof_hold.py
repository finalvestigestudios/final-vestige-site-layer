#!/usr/bin/env python3
"""R307: read-only, byte-bound verification of R306's four CRLF-only claims.

Independent frozen/integrated GitHub blobs were compared on 2026-11-12.
These byte proofs do not review safety, historical accuracy, merchant claims
or the 41 actual WordPress draft exports. No CMS, network or file writes.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PREDECESSOR = 'preparedness/tools/r306_live_lineage_review_hold.py'
PREDECESSOR_OID = '5a81011b664183fecb5c5fd950776255a0ba17fd'
LEDGER = 'preparedness/audits/r306_live_lineage_35_articles_HARD_HOLD.json'
LEDGER_OID = 'c7ab84eeacbd43f17bb3cab72a888430cb102f25'
SCHEMA = 'fv-preparedness-r307-frozen-normalization-proof-v1'
# These SHA256 values are of the LF-normalized original FROZEN blob bytes.
# Exact original and integrated GitHub blob objects were independently read.
PROOFS = {
 'root-cellars-cool-storage': (
   '7f375c32d74f2828b4912f5692abc44483e4629a',
   '2ff8d029769aa9a97de6b1e388d937899f3af38c',
   '0f2d1992fc9915218fb64d14479fdc178cd18f47001dc5cad497e18dfaf3a45f',21281,102),
 'navigation-before-gps': (
   '49beb68339a6b85b07d686c0cfb9fe1d88b8de4f',
   '3c02e58c30d1d608224944142f31fbead44a1252',
   '1bb5f1b6213cc21d267731ac21a3a025e9bd0dde42c650d917b415606ddad2f4',21752,100),
 'sanitation-before-germ-theory': (
   '02090fc1b773fd79f08a7ba754b6125844c37eab',
   'd56df76647d2598f35cfd4609f91649cef063f12',
   '404e6fa663e0848fa78b059afeea6c8110d898a8f6aec32528d20458deb11d05',21947,102),
 'pioneer-supply-chains-failed': (
   '3643c50b43ca7ba6c1d9bc439e7c78730503b80f',
   'ad158ee898f76d05bcb65c845b1e4a0e8103c660',
   'd2131798ade5ae3250fe0e74fdf3d5af95368a3266f1315a927b8ee85a71b529',24803,113),
}

def git_blob(b: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(b)).encode('ascii') + b'\0' + b).hexdigest()

def safe(root: Path, rel: str) -> bool:
    try:
        base=root.absolute()
        target=(base/rel).absolute()
        if not target.is_relative_to(base) or not target.is_file(): return False
        while target != base:
            if target.is_symlink(): return False
            target=target.parent
        return True
    except (OSError, ValueError, RuntimeError): return False

def audit(root: Path, ledger: dict, prior: dict, proofs: dict | None = None) -> dict:
    errors=[];verified=0
    proofs=PROOFS if proofs is None else proofs
    if not isinstance(prior,dict) or prior.get('state')!='DRAFT_HARD_HOLD' or prior.get('errors') != []:
        errors.append('R306_PREDECESSOR_UNVERIFIED')
    else:
        for key,value in (('integrated_file_blobs_verified',70),('body_changes',14),
                          ('metadata_changes',12),('both_changed',9),('line_endings_only_observed',4)):
            if type(prior.get(key)) is not int or prior[key] != value:
                errors.append('R306_COUNT_UNVERIFIED:'+key)
        for key in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                    'privacy_verified','paid_offer_approved','all_41_native_exports_verified'):
            if prior.get(key) is not False:errors.append('R306_FALSE_RELEASE:'+key)
    rows=ledger.get('articles') if isinstance(ledger,dict) else None
    if not isinstance(rows,list) or len(rows)!=35 or any(not isinstance(r,dict) for r in rows):
        errors.append('BAD_35_ARTICLE_LEDGER')
        rows=[r for r in rows if isinstance(r,dict)] if isinstance(rows,list) else []
    if len(set(r.get('slug') for r in rows if isinstance(r.get('slug'),str)))!=35:
        errors.append('SLUG_INVENTORY_DRIFT')
    flagged={r.get('slug') for r in rows if r.get('line_endings_only_observed') is True}
    if flagged!=set(proofs):errors.append('FORMAT_ONLY_ATTESTATIONS_MOVED')
    for slug,(frozen,integrated,normalized_sha256,nbytes,old_crlf) in proofs.items():
        found=[r for r in rows if r.get('slug')==slug]
        if len(found)!=1:
            errors.append('PROOF_ROW_NOT_UNIQUE:'+slug);continue
        row=found[0]
        if row.get('line_endings_only_observed') is not True or row.get('review_state')!='FORMAT_ONLY_OBSERVED_QA_PENDING':
            errors.append('UNAPPROVED_FORMAT_STATUS:'+slug)
        if row.get('frozen_body_blob')!=frozen:errors.append('FROZEN_BLOB_REASSIGNED:'+slug)
        if row.get('integrated_body_blob')!=integrated:errors.append('INTEGRATED_BLOB_REASSIGNED:'+slug)
        path='preparedness/content/articles/'+slug+'.body.html'
        if not safe(root,path):
            errors.append('MISSING_OR_SYMLINK_BODY:'+slug);continue
        try:body=(root/path).read_bytes()
        except OSError:
            errors.append('UNREADABLE_BODY:'+slug);continue
        if git_blob(body)!=integrated:errors.append('SOURCE_GIT_BLOB_CHANGED:'+slug)
        if b'\r' in body:errors.append('INTEGRATED_NOT_PURE_LF:'+slug)
        if len(body)!=nbytes:errors.append('NORMALIZED_LENGTH_CHANGED:'+slug)
        if hashlib.sha256(body.replace(b'\r\n',b'\n')).hexdigest()!=normalized_sha256:
            errors.append('FROZEN_NORMALIZED_PROOF_MISMATCH:'+slug)
        if old_crlf<1:errors.append('MISSING_FROZEN_LINE_ENDING_PROOF:'+slug)
        if not any(e.endswith(':'+slug) for e in errors):verified+=1
    if not isinstance(ledger,dict) or ledger.get('state')!='DRAFT_HARD_HOLD':
        errors.append('LEDGER_STATE_NOT_HARD_HOLD')
    if not isinstance(ledger,dict) or any(ledger.get(k) is not False for k in
        ('publication_authorized','independent_qd_pass','medical_safety_verified',
         'privacy_verified','paid_offer_approved','all_41_native_exports_verified')):
        errors.append('LEDGER_FALSE_APPROVAL')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'bound_format_proofs':verified,
            'proofs_expected':len(proofs),'articles_expected':35,
            'wordpress_draft_outputs_expected':41,
            'substantive_body_differences_unadjudicated':10,
            'metadata_differences_unadjudicated':12,
            'native_build_executed':False,'all_41_drafts_verified':False,
            'publication_authorized':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'privacy_verified':False,
            'paid_offer_approved':False,'confirmed_paid_orders':None,
            'net_revenue_per_1000_qualified_human_sessions':None}

def run(root: Path) -> dict:
    for path,oid in ((PREDECESSOR,PREDECESSOR_OID),(LEDGER,LEDGER_OID)):
        if not safe(root,path) or git_blob((root/path).read_bytes())!=oid:
            raise ValueError('PINNED_UPSTREAM_MISSING_OR_CHANGED:'+path)
    spec=importlib.util.spec_from_file_location('fv_r307_pinned_r306',root/PREDECESSOR)
    if spec is None or spec.loader is None:raise RuntimeError('PREDECESSOR_IMPORT_FAILED')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return audit(root,json.loads((root/LEDGER).read_text('utf-8')),mod.run(root))

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    args=p.parse_args(argv)
    try:result=run(args.repo_root)
    except (OSError,ValueError,TypeError,RuntimeError,KeyError,UnicodeError) as e:
        result={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'errors':['AUTHENTIC_SOURCE_UNAVAILABLE:'+type(e).__name__],
                'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'all_41_drafts_verified':False}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
