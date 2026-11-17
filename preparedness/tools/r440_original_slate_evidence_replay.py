#!/usr/bin/env python3
"""R440: original 35-article/9-contributor source and citation *custody*, never release approval.

Read-only replay of the R397 reviewer docket against an optional fully authenticated
checkout. Exact source identities and shared URLs are not rewritten or adjudicated.
No network, subprocess, CMS, merchant, publishing or temporary modifications.
A structural pass is not a qualified medical, food or emergency-safety review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

DRAFT = 'DRAFT_HARD_HOLD'
HEX = re.compile(r'[a-f0-9]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\}\}')
COUNTS = {'original_article_count':35, 'original_object_paths':77,
          'original_source_fragments':7, 'source_record_occurrences':280,
          'original_distinct_source_ids':203, 'base_source_records':34,
          'source_evidence_disputes':5, 'unselected_original_forks':9}
MAX_FILE = 2_000_000


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()


def bounded_read(root: Path, name: str) -> bytes:
    """Require ordinary, unique, non-linked regular files inside a frozen root."""
    if not isinstance(name,str) or not name.startswith('preparedness/') or '\\' in name:
        raise ValueError('OUTSIDE_PREPAREDNESS')
    parts = name.split('/')
    if any(x in ('','.','..') for x in parts): raise ValueError('UNSAFE_PATH')
    base = Path(root).resolve(strict=True)
    target = base.joinpath(*parts)
    if not target.resolve(strict=True).is_relative_to(base): raise ValueError('PATH_ESCAPE')
    fd = os.open(target,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or not 0<before.st_size<=MAX_FILE:
            raise ValueError('INVALID_FILE_KIND_OR_SIZE')
        data=os.read(fd,MAX_FILE+1)
        after=os.fstat(fd)
        if len(data)!=before.st_size or (before.st_ino,before.st_dev,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_dev,after.st_size,after.st_mtime_ns):
            raise ValueError('CHANGED_DURING_READ')
        return data
    finally: os.close(fd)


def unique(items):
    return len(items)==len(set(items))


def inspect_docket(docket: dict, branch_heads: dict | None = None) -> list[str]:
    e=[]
    if not isinstance(docket,dict) or docket.get('schema')!=1 or docket.get('provenance')!='ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY':
        return ['INVALID_R397_DOCKET_SCHEMA']
    if docket.get('repo')!='finalvestigestudios/final-vestige-site-layer' or docket.get('issue')!=136 or docket.get('parent_conversion_issue')!=820:
        e.append('DOCKET_OWNER_OR_ISSUE_DRIFT')
    for k,v in COUNTS.items():
        if dossier_number(docket.get('expected'),k)!=v or dossier_number(docket.get('observed'),k)!=v:
            e.append('FROZEN_COUNT_DRIFT:'+k)
    for field in ('publication_approved','qualified_safety_approved','merchant_offer_verified','automatic_variant_selection'):
        if docket.get(field) is not False:e.append('UNSAFE_RELEASE_OR_SELECTION_STATE:'+field)
    if docket.get('release_state')!=DRAFT:e.append('UNSAFE_RELEASE_STATE')
    pins=docket.get('branch_pins')
    if not isinstance(pins,list) or len(pins)!=9: return sorted(set(e+['INVALID_NINE_BRANCH_PINS']))
    bnames=[]
    for row in pins:
        if not isinstance(row,dict) or not isinstance(row.get('branch'),str) or not isinstance(row.get('sha'),str) or not HEX.fullmatch(row['sha']):
            e.append('INVALID_BRANCH_PIN');continue
        bnames.append(row['branch'])
        if not (row['branch'].startswith('claude/prep-')):e.append('UNEXPECTED_BRANCH_NAMESPACE')
        if branch_heads is not None and branch_heads.get(row['branch'])!=row['sha']:
            e.append('UNVERIFIED_OR_DRIFTED_CONTRIBUTOR_HEAD:'+row['branch'])
    if not unique(bnames) or len(bnames)!=9:e.append('DUPLICATE_BRANCH')
    if branch_heads is not None and set(branch_heads)!=set(bnames):e.append('BRANCH_HEAD_SET_MISMATCH')
    articles=docket.get('original_articles')
    if not isinstance(articles,list) or len(articles)!=35:return sorted(set(e+['INVALID_ORIGINAL_ARTICLE_LIST']))
    names=[]
    for a in articles:
        if not isinstance(a,dict) or not isinstance(a.get('slug'),str) or not SLUG.fullmatch(a['slug']):
            e.append('INVALID_ORIGINAL_ARTICLE_SLUG');continue
        names.append(a['slug'])
        shas=a.get('body_candidate_git_blobs')
        if not isinstance(shas,list) or not shas or not unique(shas) or any(not isinstance(s,str) or not HEX.fullmatch(s) for s in shas):
            e.append('INVALID_ORIGINAL_BODY_OBJECTS:'+a['slug'])
    if not unique(names):e.append('DUPLICATE_ORIGINAL_ARTICLE_SLUG')
    disputes=docket.get('source_evidence_disputes')
    if not isinstance(disputes,list) or len(disputes)!=5:e.append('FIVE_SOURCE_DISPUTES_CHANGED')
    else:
        ids=[]
        for x in disputes:
            if not isinstance(x,dict):e.append('INVALID_SOURCE_DISPUTE');continue
            ids.append(x.get('source_id'))
            if x.get('decision')!='HUMAN_REVIEW_REQUIRED' or x.get('selected_record') is not None:e.append('PREMATURE_SOURCE_ADJUDICATION')
            v=x.get('variants')
            if not isinstance(v,list) or len(v)<2:e.append('MISSING_SOURCE_VARIANTS')
            else:
                for c in v:
                    if not isinstance(c,dict) or c.get('branch') not in bnames or not isinstance(c.get('source_blob'),str) or not HEX.fullmatch(c['source_blob']) or not isinstance(c.get('url'),str) or not c.get('supports_exact') or not c.get('reading_scope_notes_exact'):
                        e.append('INCOMPLETE_SOURCE_SUPPORT_AND_READING_SCOPE')
        if not unique(ids):e.append('DUPLICATE_SOURCE_DISPUTE')
    forks=docket.get('original_fork_disputes')
    if not isinstance(forks,list) or len(forks)!=9:e.append('NINE_FORKS_CHANGED')
    else:
        paths=[]
        for f in forks:
            if not isinstance(f,dict):e.append('INVALID_FORK');continue
            path=f.get('path'); paths.append(path)
            if not isinstance(path,str) or not (path.startswith('preparedness/content/articles/') or path.startswith('preparedness/sources/fragments/')) or '..' in path:
                e.append('UNSAFE_FORK_PATH')
            if f.get('decision')!='HUMAN_REVIEW_REQUIRED' or f.get('selected_sha') is not None:e.append('PREMATURE_FORK_SELECTION')
            for v in f.get('variants',[]) if isinstance(f.get('variants'),list) else []:
                if not isinstance(v,dict) or v.get('branch') not in bnames or not isinstance(v.get('git_blob_sha'),str) or not HEX.fullmatch(v['git_blob_sha']) or type(v.get('byte_length')) is not int or v['byte_length']<=0:
                    e.append('INVALID_FORK_CANDIDATE')
            if not isinstance(f.get('variants'),list) or len(f['variants'])<2:e.append('MISSING_FORK_CANDIDATES')
        if not unique(paths):e.append('DUPLICATE_FORK_PATH')
    cross=docket.get('all_original_source_id_crosswalk')
    if not isinstance(cross,list) or len(cross)!=203:e.append('SOURCE_ID_CROSSWALK_COUNT_CHANGED')
    else:
        ids=[v.get('source_id') for v in cross if isinstance(v,dict)]
        if len(ids)!=203 or not unique(ids) or any(not isinstance(i,str) or not SLUG.fullmatch(i) for i in ids):e.append('SOURCE_ID_LOSS_OR_COLLISION')
    groups=docket.get('shared_exact_url_review_groups')
    if not isinstance(groups,list) or len(groups)!=17:e.append('SHARED_URL_GROUPS_CHANGED')
    else:
        urls=[]
        source_ids=set(x.get('source_id') for x in cross if isinstance(x,dict)) if isinstance(cross,list) else set()
        for group in groups:
            if not isinstance(group,dict):e.append('INVALID_DUPLICATE_URL_GROUP');continue
            urls.append(group.get('url'))
            ids=group.get('ids')
            if group.get('review_required') is not True or not isinstance(group.get('url'),str) or not isinstance(ids,list) or len(ids)<2 or not unique(ids) or not set(ids)<=source_ids:
                e.append('SHARED_URL_SCOPE_OR_REVIEW_LOST')
        if not unique(urls):e.append('SHARED_URL_GROUP_COLLISION')
    return sorted(set(e))


def dossier_number(d, key):
    return d.get(key) if isinstance(d,dict) and type(d.get(key)) is int else None


def inspect_checkout(docket:dict,root:Path)->dict:
    """Read original manuscripts, not synthetic exports, and retain all candidate drift."""
    errors=[]; rows=[]; meta={}; bodies={}; all_cited=[]
    for a in docket.get('original_articles',[]) if isinstance(docket.get('original_articles'),list) else []:
        if not isinstance(a,dict) or not isinstance(a.get('slug'),str) or not SLUG.fullmatch(a['slug']):continue
        slug=a['slug'];prefix=f'preparedness/content/articles/{slug}'
        try:
            body=bounded_read(root,prefix+'.body.html')
            mraw=bounded_read(root,prefix+'.meta.json')
            bsha=git_blob_sha(body)
            entry=json.loads(mraw)
            if not isinstance(entry,dict):raise ValueError('META_NOT_OBJECT')
            if entry.get('slug')!=slug:errors.append('META_SLUG_DRIFT:'+slug)
            if entry.get('status',{}).get('publish') not in ('draft',):errors.append('UNSAFE_OR_UNEXPECTED_PUBLISH_STATE:'+slug)
            if entry.get('safety_review',{}).get('state') not in ('pending','needs-review','blocked'):
                errors.append('REQUIRES_HUMAN_SAFETY_STATE_REVIEW:'+slug)
            cites=CITE.findall(body.decode('utf-8'))
            all_cited.extend(cites)
            source_use=entry.get('source_use',{})
            if not isinstance(source_use,dict):errors.append('MISSING_SOURCE_USE_MAP:'+slug);source_use={}
            for x in sorted(set(cites)-set(source_use)):errors.append('CITED_ID_LACKS_READING_SCOPE:'+slug+':'+x)
            original=set(a.get('body_candidate_git_blobs',[]))
            if bsha not in original:errors.append('BODY_NOT_IN_ORIGINAL_CANDIDATE_SET:'+slug)
            n=entry.get('n')
            if type(n) is not int:errors.append('INVALID_ARTICLE_NUMBER:'+slug)
            meta[slug]=(n,entry);bodies[slug]=body
            rows.append({'slug':slug,'n':n,'body_git_blob':bsha,'metadata_git_blob':git_blob_sha(mraw),'citations':len(cites),'source_ids':sorted(set(cites)),'unselected_candidate_count':len(original)})
        except (OSError,ValueError,KeyError,TypeError,UnicodeError,json.JSONDecodeError):
            errors.append('MISSING_OR_UNSAFE_ARTICLE_OBJECTS:'+slug)
    if len(rows)!=35:errors.append('INCOMPLETE_AUTHENTIC_ARTICLE_PAIR_SET')
    numbers=[r['n'] for r in rows]
    if sorted(numbers)!=list(range(1,36)):errors.append('ARTICLE_NUMBER_IDENTITY_DRIFT')
    slugs=set(meta)
    for slug,body in bodies.items():
        for dest in sorted(set(LINK.findall(body.decode('utf-8')))-slugs):
            errors.append('INTERNAL_ARTICLE_LINK_UNRESOLVED:'+slug+':'+dest)
    cross=docket.get('all_original_source_id_crosswalk')
    original_ids={x.get('source_id') for x in cross} if isinstance(cross,list) else set()
    for sid in sorted(set(all_cited)-original_ids):errors.append('CITATION_ID_NOT_IN_ORIGINAL_CROSSWALK:'+sid)
    return {'errors':sorted(set(errors)),'articles_read':len(rows),'citation_occurrences_in_checkout':len(all_cited),
            'distinct_ids_cited':len(set(all_cited)),'review_rows':sorted(rows,key=lambda x:x['slug'])}


def audit(docket:dict,root:Path|None=None,branch_heads:dict|None=None)->dict:
    errors=inspect_docket(docket,branch_heads)
    checks=None
    if root is None:errors.append('AUTHENTIC_CHECKOUT_NOT_PROVIDED')
    else:
        try:
            checks=inspect_checkout(docket,Path(root))
            errors.extend(checks['errors'])
        except (OSError,ValueError,TypeError,KeyError):errors.append('AUTHENTIC_CHECKOUT_UNAVAILABLE')
    if branch_heads is None:errors.append('LIVE_CONTRIBUTOR_SHAS_NOT_ATTESTED_IN_THIS_EXECUTION')
    return {'schema':1,'issues':[136,820],'release_state':DRAFT,'eligible':False,
            'originals_structurally_safe_for_release':False,'qualified_safety_approved':False,
            'publication_approved':False,'merchant_offer_verified':False,
            'automatic_fork_selection':False,'native_build_executed':False,
            'original_35_article_review':checks,
            'errors':sorted(set(errors)),
            'warning':'All branch and source variants remain preserved; no QD or checkout authority granted.'}


def main(argv=None)->int:
    p=argparse.ArgumentParser(description='R440 original source evidence replay; always hard hold')
    p.add_argument('docket',type=Path)
    p.add_argument('--repo-root',type=Path)
    p.add_argument('--branch-heads',type=Path,help='External, independently observed branch name to SHA map')
    a=p.parse_args(argv)
    try:
        data=json.loads(a.docket.read_text(encoding='utf-8'))
        heads=json.loads(a.branch_heads.read_text(encoding='utf-8')) if a.branch_heads else None
        report=audit(data,a.repo_root,heads)
    except (OSError,ValueError,TypeError,UnicodeError,json.JSONDecodeError):
        report=audit({},None,None)
    print(json.dumps(report,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':
    raise SystemExit(main())
