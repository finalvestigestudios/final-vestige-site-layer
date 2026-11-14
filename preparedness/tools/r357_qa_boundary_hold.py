#!/usr/bin/env python3
"""R357 read-only cross-PR Preparedness QA custody. Never approves release."""
from __future__ import annotations
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 'fv-preparedness-r357-qa-boundary-v1'
HOLD = dict(may_merge=False, may_publish=False, qualified_qd_pass=False,
            safety_review_complete=False, verified_paid_orders=False,
            native_export_verified=False, may_activate_paid_cta=False)
SPECS = {
    157: dict(base='10f58fed1ba808056813064ca5f9680589db8da1',
              head='7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
              paths=('preparedness/content/articles/household-emergency-plan.body.html',
                     'preparedness/content/articles/three-day-kit.body.html',
                     'preparedness/sources/fragments/start.json',
                     'preparedness/taxonomy.json',
                     'preparedness/tests/test_preparedness.py')),
    169: dict(base='4b009361277ea1d4617b368f5d45104c7318b284',
              head='e9cd7766dac59d47ab467d8945269b9146c2aef5',
              paths=('preparedness/tests/test_preparedness.py',)),
    2205: dict(base='e9cd7766dac59d47ab467d8945269b9146c2aef5',
               head='bbcf1859768624c611df4abadc564c18247cf32a',
               paths=('preparedness/tests/test_preparedness.py',
                      'preparedness/audits/r318_source_fixture_qa_remediation_HARD_HOLD.md')),
}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SRC = re.compile(r'\{\{inline-js:([^}]+)\}\}')
HREF = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.I)
HEADING = re.compile(r'<h[1-6]\b[^>]*\bid=["\']([^"\']+)["\']', re.I)
WORD = re.compile(r"[\w'-]+", re.UNICODE)

class Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[]
        self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.skip: self.skip-=1
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)

def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def word_count(body):
    p=Visible(); p.feed(body); p.close()
    return len(WORD.findall(' '.join(p.parts)))

def compare_article(path, old, new):
    issues=[]
    if len(new.strip()) == 0: issues.append('EMPTY_ARTICLE:'+path)
    a,b=word_count(old),word_count(new)
    if a < 30 or b < max(30,int(a*.92)): issues.append('READING_DEPTH_LOSS:'+path)
    if Counter(CITE.findall(old))-Counter(CITE.findall(new)):
        issues.append('CITATION_OCCURRENCE_LOST:'+path)
    if HEADING.findall(old)!=HEADING.findall(new): issues.append('HEADING_ANCHOR_DRIFT:'+path)
    if Counter(HREF.findall(old))!=Counter(HREF.findall(new)):
        issues.append('LINK_DESTINATION_CHANGE:'+path)
    if Counter(SRC.findall(old))!=Counter(SRC.findall(new)):
        issues.append('SCRIPT_DEPENDENCY_CHANGE:'+path)
    return issues, dict(path=path, before_sha256=digest(old),after_sha256=digest(new),
                        original_words=a,reviewed_words=b,original_citations=len(CITE.findall(old)),
                        reviewed_citations=len(CITE.findall(new)),release_review_required=True)

def source_rows(s):
    data=json.loads(s)
    rows=data.get('sources') if isinstance(data,dict) else None
    if not isinstance(rows,list) or not all(isinstance(x,dict) and isinstance(x.get('id'),str) for x in rows):
        raise ValueError('INVALID_SOURCE_FRAGMENT')
    by_id={x['id']:x for x in rows}
    if len(by_id)!=len(rows): raise ValueError('DUPLICATE_SOURCE_IDS')
    return by_id

def compare_sources(old,new):
    a,b=source_rows(old),source_rows(new)
    issues=[]
    if set(a)!=set(b):issues.append('SOURCE_IDENTITY_ADDED_OR_DROPPED')
    protected=('url','title','publisher','verified_on','human_link_check','supports','published','updated','reviewed')
    for key in sorted(set(a)&set(b)):
        if any(a[key].get(k)!=b[key].get(k) for k in protected):issues.append('SOURCE_EVIDENCE_MUTATED:'+key)
        if a[key].get('kind')!=b[key].get('kind'):
            issues.append('SOURCE_CLASSIFICATION_REQUIRES_HUMAN_REVIEW:'+key)
    return issues,dict(source_count_before=len(a),source_count_after=len(b),
                       source_hash_before=digest(old),source_hash_after=digest(new))

def compare_taxonomy(old,new):
    a,b=json.loads(old),json.loads(new)
    if not isinstance(a,dict) or not isinstance(b,dict):raise ValueError('INVALID_TAXONOMY')
    return (['TAXONOMY_SEMANTICS_CHANGED'] if a!=b else []),dict(taxonomy_semantics_equal=a==b,
                original_sha256=digest(old),reviewed_sha256=digest(new))

def review_snapshot(number, before, after, declared_paths=None, base=None, head=None):
    """In-memory reviewer: synthetic tests can inspect rules but never clear a release."""
    spec=SPECS.get(number)
    if spec is None or not isinstance(before,dict) or not isinstance(after,dict):
        return dict(schema=SCHEMA,status='INVALID_HARD_HOLD',errors=['INVALID_INPUT'], **HOLD)
    paths=set(declared_paths if declared_paths is not None else (set(before)|set(after)))
    errors=[]; docket=[]
    if paths!=set(spec['paths']):errors.append('QA_CHANGE_SCOPE_DRIFT')
    if base is not None and base!=spec['base']:errors.append('QA_BASE_SHA_DRIFT')
    if head is not None and head!=spec['head']:errors.append('QA_HEAD_SHA_DRIFT')
    if set(before)!=paths or set(after)!=paths:errors.append('INCOMPLETE_QA_SNAPSHOT')
    for path in sorted(paths):
        if not path.startswith('preparedness/') or '..' in Path(path).parts:
            errors.append('UNSAFE_FILE_PATH');continue
        a,b=before.get(path),after.get(path)
        if not isinstance(a,str) or not isinstance(b,str):errors.append('MISSING_QA_FILE:'+path);continue
        if a==b:errors.append('DECLARED_PATH_NOT_CHANGED:'+path)
        if path.endswith('.body.html'):
            found,detail=compare_article(path,a,b); errors.extend(found);docket.append(detail)
        elif path.endswith('/start.json'):
            try:found,detail=compare_sources(a,b);errors.extend(found);docket.append(detail)
            except (ValueError,TypeError,json.JSONDecodeError):errors.append('SOURCE_REGISTER_UNPARSABLE')
        elif path.endswith('/taxonomy.json'):
            try:found,detail=compare_taxonomy(a,b);errors.extend(found);docket.append(detail)
            except (ValueError,TypeError,json.JSONDecodeError):errors.append('TAXONOMY_UNPARSABLE')
        elif path.endswith('.py'):
            if number in (169,2205) and not all(x in b for x in ('TemporaryDirectory','copytree')):
                errors.append('SYNTHETIC_FIXTURE_ISOLATION_NOT_EVIDENCED')
            docket.append(dict(path=path,before_sha256=digest(a),after_sha256=digest(b),
                               executable_test_review_required=True))
        elif path.endswith('.md'):
            docket.append(dict(path=path,before_sha256=digest(a),after_sha256=digest(b)))
        else:errors.append('UNHANDLED_QA_PATH:'+path)
    return dict(schema=SCHEMA,status='INVALID_HARD_HOLD' if errors else 'QA_REVIEW_REQUIRED_HARD_HOLD',
                qa_number=number,expected_base=spec['base'],expected_head=spec['head'],
                errors=sorted(set(errors)),docket=docket,**HOLD)

def git(repo,*args):
    r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,check=False,timeout=20)
    if r.returncode:raise ValueError('GIT_OBJECT_UNAVAILABLE')
    if len(r.stdout)>4_000_000:raise ValueError('GIT_OBJECT_TOO_LARGE')
    return r.stdout.decode('utf-8','strict')

def native_review(repo,number):
    """Only reads pinned local git objects, no checkout/write, no network, no approval."""
    try:
        root=Path(repo).resolve(strict=True)
        if not (root/'.git').exists():raise ValueError('GIT_CHECKOUT_REQUIRED')
        spec=SPECS[number]
        if Path(git(root,'rev-parse','--show-toplevel').strip()).resolve()!=root:
            raise ValueError('GIT_ROOT_MISMATCH')
        for sha in (spec['base'],spec['head']):
            if git(root,'cat-file','-t',sha).strip()!='commit':raise ValueError('PIN_NOT_A_COMMIT')
        paths=git(root,'diff','--name-only',spec['base'],spec['head'],'--','preparedness/').splitlines()
        before={};after={}
        for path in paths:
            if path not in spec['paths']:continue
            before[path]=git(root,'show',spec['base']+':'+path)
            after[path]=git(root,'show',spec['head']+':'+path)
        return review_snapshot(number,before,after,paths,spec['base'],spec['head'])
    except (OSError,ValueError,TypeError,KeyError,UnicodeError,subprocess.TimeoutExpired) as exc:
        return dict(schema=SCHEMA,status='INVALID_HARD_HOLD',qa_number=number,
                    errors=['NATIVE_CUSTODY_UNAVAILABLE:'+type(exc).__name__],**HOLD)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--qa',type=int,choices=sorted(SPECS),default=157)
    args=p.parse_args()
    print(json.dumps(native_review(args.repo_root,args.qa),sort_keys=True,indent=2))
    sys.exit(2)  # permanent release hold, even when a synthetic review reports no errors
