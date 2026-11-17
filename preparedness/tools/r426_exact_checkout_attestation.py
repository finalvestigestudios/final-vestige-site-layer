#!/usr/bin/env python3
"""R426 read-only Git checkout and test-byte attestation (Issue #136).

Requires the original R397 Git-pinned docket; protects against reporting tests
run on local copies as tests of a different published PR commit. No network,
no git checkout, no writes to the inspected repository, no release approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

PIN = '86d22a1d504c93db7689b914e2202a7845b648e2'
R425_HEAD = '268102f54c35e37570707b2e0ca93428181a2a5e'
FILES = ('preparedness/tools/r425_integrated_custody_gate.py',
         'preparedness/tests/test_r425_integrated_custody_gate.py')
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
MAX_INPUT = 2_000_000


def gitblob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def git(repo, *args, binary=False):
    try:
        p = subprocess.run(['git','-C',str(repo),*args],capture_output=True,
                           check=False,timeout=8,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
    except (OSError,subprocess.TimeoutExpired) as e:
        raise ValueError('GIT_EXEC_UNAVAILABLE') from e
    if p.returncode: raise ValueError('GIT_QUERY_FAILED')
    return p.stdout if binary else p.stdout.rstrip(b'\n')


def regular_read(path, limit=MAX_INPUT):
    path=Path(path)
    try:
        before=path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or not 0 < before.st_size<=limit:
            raise ValueError('NOT_SINGLE_LINK_REGULAR_FILE')
        fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
        with os.fdopen(fd,'rb') as fh:
            after=os.fstat(fh.fileno())
            raw=fh.read(limit+1)
            end=os.fstat(fh.fileno())
        mark=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
        if not stat.S_ISREG(after.st_mode) or after.st_nlink!=1 or len(raw)>limit or mark(before)!=mark(after) or mark(after)!=mark(end):
            raise ValueError('SOURCE_CHANGED_DURING_READ')
        return raw
    except OSError as e:
        raise ValueError('SOURCE_NOT_READABLE') from e


def unique_pairs(items):
    d={}
    for k,v in items:
        if k in d:raise ValueError('DUPLICATE_JSON_KEY')
        d[k]=v
    return d


def json_file(path):
    return json.loads(regular_read(path).decode('utf-8'),object_pairs_hook=unique_pairs,
                      parse_constant=lambda _:(_ for _ in ()).throw(ValueError('INVALID_JSON_CONSTANT')))


def check(repo, docket_raw, receipt, *, expected_pin=PIN, expected_head=R425_HEAD):
    errors=[]
    def bad(code):errors.append('R426_'+code)
    try:
        docket=json.loads(docket_raw.decode('utf-8'),object_pairs_hook=unique_pairs)
    except (ValueError,UnicodeError,TypeError,AttributeError):
        docket={};bad('INVALID_DOCKET')
    if gitblob(docket_raw)!=expected_pin:bad('DOCKET_GIT_BLOB_MISMATCH')
    if not isinstance(docket,dict) or docket.get('schema')!=1 or docket.get('issue')!=136 or docket.get('release_state')!='DRAFT_HARD_HOLD' or docket.get('publication_approved') is not False or docket.get('qualified_safety_approved') is not False:
        bad('DOCKET_IDENTITY_OR_APPROVAL_DRIFT')
    pins=docket.get('branch_pins',[]) if isinstance(docket,dict) else []
    articles=docket.get('original_articles',[]) if isinstance(docket,dict) else []
    if not isinstance(pins,list) or len(pins)!=9 or not all(isinstance(x,dict) and isinstance(x.get('branch'),str) and isinstance(x.get('sha'),str) and HEX40.fullmatch(x['sha']) for x in pins) or len({x.get('branch') for x in pins if isinstance(x,dict)})!=9:bad('NINE_BRANCH_PINS_REQUIRED')
    if not isinstance(articles,list) or len(articles)!=35:bad('THIRTY_FIVE_ARTICLES_REQUIRED')
    if not isinstance(receipt,dict) or set(receipt)!={'schema','issue','release_state','approved','head_sha','files'} or type(receipt.get('schema')) is not int or receipt['schema']!=1 or receipt.get('issue')!=136 or receipt.get('release_state')!='DRAFT_HARD_HOLD' or receipt.get('approved') is not False or receipt.get('head_sha')!=expected_head:
        bad('RECEIPT_IDENTITY_OR_HEAD_MISMATCH')
    rows=receipt.get('files') if isinstance(receipt,dict) else None
    if not isinstance(rows,list) or len(rows)!=len(FILES) or set(x.get('path') for x in rows if isinstance(x,dict))!=set(FILES):bad('REQUIRED_CODE_AND_TEST_PATHS')
    root=Path(repo).absolute()
    try:
        if root.is_symlink() or Path(os.fsdecode(git(root,'rev-parse','--show-toplevel'))).absolute()!=root:
            bad('NOT_EXACT_WORKTREE_ROOT')
        head=git(root,'rev-parse','HEAD').decode('ascii')
        if head!=expected_head:bad('CHECKOUT_HEAD_NOT_PR_HEAD')
        if git(root,'status','--porcelain','--untracked-files=no'):bad('DIRTY_TRACKED_WORKTREE')
        if git(root,'rev-parse','--is-shallow-repository')==b'true':bad('SHALLOW_BRANCH_PROVENANCE')
        for p in pins if isinstance(pins,list) else []:
            if not isinstance(p,dict) or not isinstance(p.get('branch'),str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{1,120}',p['branch']) or '..' in p['branch'] or not HEX40.fullmatch(str(p.get('sha',''))):continue
            try:
                commit=git(root,'rev-parse','--verify','refs/heads/'+p['branch']).decode('ascii')
                if commit!=p['sha']:bad('BRANCH_SHA_MISMATCH_'+p['branch'])
                if git(root,'cat-file','-t',commit)!=b'commit':bad('BRANCH_NOT_COMMIT_'+p['branch'])
            except ValueError:bad('BRANCH_UNAVAILABLE_'+p['branch'])
        if isinstance(rows,list):
            for item in rows:
                if not isinstance(item,dict) or set(item)!={'path','git_blob','tested_sha256'} or item.get('path') not in FILES:
                    bad('FILE_ROW_INVALID');continue
                path=item['path']
                if not HEX40.fullmatch(str(item.get('git_blob',''))) or not HEX64.fullmatch(str(item.get('tested_sha256',''))):bad('INVALID_FILE_HASHES');continue
                try:
                    raw=regular_read(root/path)
                    tree_id=git(root,'rev-parse','--verify',expected_head+':'+path).decode('ascii')
                    if tree_id!=item['git_blob'] or gitblob(raw)!=tree_id:bad('CHECKOUT_VERSUS_TREE_BLOB_DRIFT_'+path)
                    if hashlib.sha256(raw).hexdigest()!=item['tested_sha256']:bad('EXECUTED_BYTES_NOT_COMMITTED_'+path)
                    if git(root,'cat-file','-p',tree_id,binary=True)!=raw:bad('GIT_OBJECT_CONTENT_DRIFT_'+path)
                except ValueError:bad('FILE_UNAVAILABLE_'+path)
    except (ValueError,UnicodeError):bad('GIT_WORKTREE_UNAVAILABLE')
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,'qualified_safety_approved':False,
            'publication_approved':False,'paid_activation_approved':False,
            'exact_code_and_test_checkout_attested':not errors,
            'errors':sorted(set(errors)),'base_pr_head':expected_head,
            'original_docket_git_blob':expected_pin,'original_slate_count':35,
            'review_only':True,'tests_executed_by_this_gate':False,
            'evidence':'EXACT_GIT_BYTE_IDENTITY_ONLY_NOT_NATIVE_BUILD_OR_QD_REVIEW'}


def main(argv=None):
    ap=argparse.ArgumentParser(description='R426 private exact checkout/branch/code+test attestation; always HARD HOLD')
    ap.add_argument('repo',type=Path);ap.add_argument('original_docket',type=Path);ap.add_argument('receipt',type=Path)
    a=ap.parse_args(argv)
    try:
        result=check(a.repo,regular_read(a.original_docket),json_file(a.receipt))
    except (ValueError,OSError,TypeError,UnicodeError) as e:
        result={'release_state':'DRAFT_HARD_HOLD','eligible':False,'exact_code_and_test_checkout_attested':False,
                'errors':['R426_EVIDENCE_UNAVAILABLE_'+type(e).__name__],'tests_executed_by_this_gate':False}
    print(json.dumps(result,indent=2,sort_keys=True));return 2

if __name__=='__main__':sys.exit(main())
