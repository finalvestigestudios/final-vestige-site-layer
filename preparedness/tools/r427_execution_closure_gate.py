#!/usr/bin/env python3
"""R427 review-only exact checkout + Python execution-input closure, #136.

A *structural* gate for the Preparedness source/citation safety test stack.
Does not execute tests, inspect actual pages or approve a release. It never
invokes a shell, fetches from the network, or writes to the inspected tree.
The reviewer must independently supply the PR head SHA. All CLI paths HOLD.
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

ISSUE = 136
BASE_HEAD = '25f6b3fc3d6cb6fd009437bd604519c64e1550d6'  # reviewed R426 draft
STEMS = {
    409:'source_equivalence_gate', 410:'full_slate_export_gate',
    411:'visible_evidence_gate', 412:'baseline_citation_gate',
    413:'warning_heading_escrow_gate', 414:'citation_locality_escrow_gate',
    415:'global_citation_alignment_gate', 416:'cited_claim_block_gate',
    417:'quantitative_claim_provenance_gate', 418:'uncited_claim_custody_gate',
    419:'unbound_evidence_gate', 420:'attribute_evidence_gate',
    421:'funnel_evidence_gate', 422:'social_provenance_gate',
    423:'campaign_merchant_boundary_gate', 424:'post_cohort_custody_gate',
    425:'integrated_custody_gate', 426:'exact_checkout_attestation',
    427:'execution_closure_gate',
}
# Historical tool names are not inferred from user-controlled filenames.
REQUIRED = tuple(sorted(
    [f'preparedness/tools/r{i}_{stem}.py' for i,stem in STEMS.items()] +
    [f'preparedness/tests/test_r{i}_{stem}.py' for i,stem in STEMS.items()]
))
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
LIMIT_BYTES = 2_000_000
SUSPICIOUS_SUFFIXES = ('.pyc','.pyo','.pth','.so','.pyd','.dll','.dylib')
SUSPICIOUS_NAMES = {'sitecustomize.py','usercustomize.py'}
POISON_ENV = ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT',
              'PYTHONUSERBASE','PYTHONPYCACHEPREFIX')


def git(repo,*args,binary=False):
    try:
        result=subprocess.run(['git','-C',str(repo),*args],capture_output=True,
               check=False,timeout=12,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0',
                   'GIT_CONFIG_NOSYSTEM':'1'})
    except (OSError,subprocess.TimeoutExpired) as e:
        raise ValueError('GIT_QUERY_UNAVAILABLE') from e
    if result.returncode:
        raise ValueError('GIT_QUERY_FAILED')
    return result.stdout if binary else result.stdout.strip()


def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()


def guarded_read(path,root):
    """No symlinks/hardlinks, out-of-tree reads, or best-effort partially read files."""
    path=Path(path).absolute();root=Path(root).absolute()
    if root not in path.parents:
        raise ValueError('PATH_OUTSIDE_REPO')
    cur=root
    for part in path.relative_to(root).parts:
        cur=cur/part
        mode=cur.lstat().st_mode
        if stat.S_ISLNK(mode):raise ValueError('SYMLINKED_INPUT')
    before=path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or not 0 < before.st_size<=LIMIT_BYTES:
        raise ValueError('NOT_BOUNDED_SINGLE_LINK_FILE')
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as fh:
        opened=os.fstat(fh.fileno())
        data=fh.read(LIMIT_BYTES+1)
        final=os.fstat(fh.fileno())
    marker=lambda st:(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
    if len(data)>LIMIT_BYTES or marker(before)!=marker(opened) or marker(opened)!=marker(final):
        raise ValueError('CHANGED_DURING_READ')
    return data


def closure(repo,expected_head,*,expected_base=BASE_HEAD,env=None):
    errors=[]
    def bad(code):errors.append('R427_'+code)
    root=Path(repo).absolute()
    env=dict(os.environ if env is None else env)
    if not isinstance(expected_head,str) or not HEX40.fullmatch(expected_head):bad('INVALID_EXPECTED_PR_HEAD')
    if not isinstance(expected_base,str) or not HEX40.fullmatch(expected_base):bad('INVALID_PARENT_PIN')
    for var in POISON_ENV:
        if env.get(var):bad('PYTHON_IMPORT_ENV_'+var)
    if env.get('PYTHONDONTWRITEBYTECODE')!='1':bad('BYTECODE_WRITES_NOT_DISABLED')
    if env.get('PYTHONNOUSERSITE')!='1':bad('USER_SITE_NOT_DISABLED')
    digest=None;reviewed=[]
    try:
        if root.is_symlink() or not root.is_dir() or Path(os.fsdecode(git(root,'rev-parse','--show-toplevel'))).absolute()!=root:
            bad('CHECKOUT_ROOT_DRIFT')
        head=git(root,'rev-parse','HEAD').decode('ascii')
        if head!=expected_head:bad('PR_HEAD_MISMATCH')
        if expected_base!=head:
            try:git(root,'merge-base','--is-ancestor',expected_base,head)
            except ValueError:bad('R426_BASE_NOT_ANCESTOR')
        if git(root,'rev-parse','--is-shallow-repository')==b'true':bad('SHALLOW_HISTORY')
        if git(root,'status','--porcelain','--untracked-files=all'):
            bad('UNCOMMITTED_OR_UNTRACKED_WORKTREE')
        tracked=git(root,'ls-files','-z',binary=True).split(b'\0')
        tracked={os.fsdecode(v) for v in tracked if v}
        missing=set(REQUIRED)-tracked
        if missing:bad('MISSING_REQUIRED_CHAIN_FILES')
        pyfiles=sorted(p for p in tracked if p.startswith('preparedness/') and
              (p.startswith('preparedness/tools/') or p.startswith('preparedness/tests/'))
              and p.endswith('.py'))
        if not pyfiles:bad('NO_PYTHON_REVIEW_INPUTS')
        # Ignore rules can conceal untracked bytecode or extension modules from status.
        for current,dirs,files in os.walk(root/'preparedness',followlinks=False):
            dirs[:]=[d for d in dirs if d!='.git']
            for d in dirs:
                full=Path(current)/d
                if full.is_symlink() or d=='__pycache__':bad('IMPORT_DIRECTORY_POISON')
            for filename in files:
                full=Path(current)/filename
                rel=full.relative_to(root).as_posix()
                if full.is_symlink() or filename in SUSPICIOUS_NAMES or filename.endswith(SUSPICIOUS_SUFFIXES):
                    bad('IMPORT_ARTIFACT_POISON')
                if filename.endswith('.py') and rel not in tracked:
                    bad('UNTRACKED_PYTHON_SOURCE')
        hashes=[]
        for path in pyfiles:
            try:
                raw=guarded_read(root/path,root)
                actual_blob=blob(raw)
                committed=git(root,'rev-parse','--verify',head+':'+path).decode('ascii')
                if committed!=actual_blob:bad('TREE_VERSUS_WORKTREE_BYTE_DRIFT')
                if git(root,'cat-file','-p',committed,binary=True)!=raw:bad('GIT_OBJECT_VERSUS_WORKTREE_DRIFT')
                mode=git(root,'ls-tree',head,'--',path).decode('utf-8')
                if not (mode.startswith('100644 blob ') or mode.startswith('100755 blob ')):
                    bad('UNEXPECTED_GIT_FILE_MODE')
                hashes.append((path,actual_blob,hashlib.sha256(raw).hexdigest()))
                reviewed.append(path)
            except (ValueError,OSError,UnicodeError):bad('UNREADABLE_OR_UNCOMMITTED_PYTHON_INPUT')
        if not errors:
            data=json.dumps({'issue':ISSUE,'head':head,'base':expected_base,
                    'files':hashes},separators=(',',':'),ensure_ascii=True).encode()
            digest=hashlib.sha256(b'FV-R427-REVIEW-CLOSURE-V1\0'+data).hexdigest()
    except (ValueError,OSError,UnicodeError):
        bad('CHECKOUT_OR_GIT_UNAVAILABLE')
    return {'issue':ISSUE,'release_state':'DRAFT_HARD_HOLD','eligible':False,
            'publication_approved':False,'qualified_safety_approved':False,
            'paid_activation_approved':False,'native_build_executed':False,
            'tests_executed_by_this_gate':False,'execution_input_closure_ok':not errors,
            'review_only_closure_sha256':digest,'python_files_inspected':len(reviewed),
            'required_chain_count':len(REQUIRED),'errors':sorted(set(errors)),
            'source_claim_safety_review':'HUMAN_REVIEW_REQUIRED',
            'commerce_conversion':'UNVERIFIED',
            'evidence':'GIT_BYTES_AND_IMPORT_SURFACE_ONLY_NOT_TESTS_OR_QD_PASS'}


def main(argv=None):
    parser=argparse.ArgumentParser(description='R427 read-only Python execution-closure HARD HOLD')
    parser.add_argument('repo',type=Path)
    parser.add_argument('expected_pr_head',help='40-hex GitHub PR head independently checked by reviewer')
    a=parser.parse_args(argv)
    try:r=closure(a.repo,a.expected_pr_head)
    except (ValueError,OSError,UnicodeError) as e:
        r={'release_state':'DRAFT_HARD_HOLD','eligible':False,
           'execution_input_closure_ok':False,'errors':['R427_UNHANDLED_INPUT_'+type(e).__name__]}
    print(json.dumps(r,indent=2,sort_keys=True));return 2

if __name__=='__main__':sys.exit(main())
