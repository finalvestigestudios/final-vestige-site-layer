#!/usr/bin/env python3
"""R350: read-only nine-branch, 41-document Preparedness custody/reconciliation docket.

Never merges, checks out, edits source, validates medical advice, or approves publishing.
A conflict-free Git ledger is not editorial or qualified safety clearance.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r350-nine-branch-content-custody-v1'
PINS = {
 'claude/prep-food-ccdc55':'f911ff7a655de8d81535ea86ec3d65a49ee76648',
 'claude/prep-health-837444':'d5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
 'claude/prep-hist-field-9db767':'4e5caf812727953aa45e3bda2d382f2c67b6a09c',
 'claude/prep-hist-food-b81f19':'67e116e536c7410bed30f8f3b1bb8c166f3c223d',
 'claude/prep-hist-home-0e0e38':'7504a5f099594d635e3dd7332a33a2e1346c43a2',
 'claude/prep-shelter-5e1e0e':'5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
 'claude/prep-start-bbfeb8':'2122d856fce9f64887c16df3d52e64be9f59a55b',
 'claude/prep-shelter-continuation':'ac8625faf30dd5538fadc31e06cb5a2cea1defae',
 'claude/prep-shelter-followup-evidence':'6a5998ead97eca997e573ce8d3ceacf1c6aabad4',
}
HOLD = {'may_publish':False,'may_merge':False,'qualified_qd_pass':False,
        'independent_claim_support_verified':False,'native_build_verified':False,
        'commerce_offer_verified':False,'verified_paid_orders':False}
ID = re.compile(r'^(articles|tools)/([a-z0-9]+(?:-[a-z0-9]+)*)$')
CITE = re.compile(r'\{\{cite:([a-z0-9][a-z0-9-]*)\}\}')


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def ledger(snapshots, *, expected=PINS, require_full=True):
    """Use already-authenticated SHA-pinned snapshots; return redacted review-only docket."""
    errors=[]; grouped=defaultdict(list); urls=defaultdict(set); inventory={}
    if not isinstance(snapshots,dict) or not isinstance(expected,dict) or not expected:
        snapshots={}; errors.append('INVALID_SNAPSHOTS_OR_PIN_SET')
    for branch in sorted(expected):
        row=snapshots.get(branch)
        if not isinstance(row,dict):
            errors.append('MISSING_PINNED_BRANCH:'+branch); continue
        if row.get('sha')!=expected[branch]:
            errors.append('BRANCH_SHA_DRIFT:'+branch); continue
        documents=row.get('documents')
        if not isinstance(documents,list):
            errors.append('MISSING_BRANCH_DOCUMENTS:'+branch); continue
        seen=set(); inventory[branch]=len(documents)
        for item in documents:
            if not isinstance(item,dict):
                errors.append('INVALID_DOCUMENT:'+branch); continue
            key=item.get('id'); body=item.get('body'); meta=item.get('meta')
            if not isinstance(key,str) or not ID.fullmatch(key):
                errors.append('INVALID_ID:'+branch); continue
            if key in seen: errors.append('DUPLICATE_BRANCH_DOCUMENT:'+branch+':'+key)
            seen.add(key)
            if not isinstance(body,str) or not isinstance(meta,dict):
                errors.append('INVALID_BODY_OR_META:'+branch+':'+key); continue
            if not body.strip():errors.append('EMPTY_BODY:'+branch+':'+key)
            slug=key.split('/',1)[1]
            if meta.get('slug')!=slug:errors.append('META_SLUG_MISMATCH:'+branch+':'+key)
            if (meta.get('status') or {}).get('publish')!='draft' if isinstance(meta.get('status'),dict) else True:
                errors.append('UNSAFE_PUBLISH_STATE:'+branch+':'+key)
            state=meta.get('safety_review')
            if not isinstance(state,dict) or state.get('state') not in ('pending','not-required'):
                errors.append('UNSAFE_SAFETY_STATE:'+branch+':'+key)
            track=meta.get('track')
            if isinstance(state,dict) and state.get('state')=='not-required' and track!='lost-ways':
                errors.append('MODERN_WITHOUT_SAFETY_GATE:'+branch+':'+key)
            use=meta.get('source_use')
            if not isinstance(use,dict) or not all(isinstance(k,str) for k in use):
                errors.append('INVALID_SOURCE_USE:'+branch+':'+key); use={}
            citations=CITE.findall(body)
            if set(citations)-set(use):errors.append('CITATION_NOT_DECLARED:'+branch+':'+key)
            url=meta.get('canonical_url',meta.get('permalink',meta.get('url')))
            if url is not None:
                if not isinstance(url,str):errors.append('INVALID_URL:'+branch+':'+key)
                else:
                    try:
                        parsed=urlsplit(url)
                    except ValueError:
                        errors.append('MALFORMED_CANONICAL_URL:'+branch+':'+key)
                        parsed=urlsplit('/__invalid__/')
                    path=parsed.path
                    host=parsed.netloc.lower()
                    if ((parsed.scheme and parsed.scheme!='https')
                        or (host and host not in ('finalvestige.com','www.finalvestige.com'))
                        or (host and not parsed.scheme)
                        or (parsed.scheme and not host)
                        or parsed.username is not None or parsed.password is not None
                        or not path.startswith('/preparedness/')
                        or '..' in path.split('/') or '%' in path
                        or parsed.query or parsed.fragment):
                        errors.append('UNSAFE_CANONICAL_URL:'+branch+':'+key)
                    else:urls[path.rstrip('/')+'/'].add(key)
            else:errors.append('URL_NOT_AUTHENTICATED:'+branch+':'+key)
            grouped[key].append({'branch':branch,'body':digest(body),'body_words':len(body.split()),
                                'citation_ids':tuple(citations),'source_ids':tuple(sorted(use)),
                                'meta':digest(json.dumps(meta,sort_keys=True,ensure_ascii=False)),
                                'safety':state.get('state') if isinstance(state,dict) else None,
                                'url':url if isinstance(url,str) else None})
    for branch in sorted(set(snapshots)-set(expected)):
        errors.append('UNPINNED_BRANCH:'+branch)
    collisions=[{'url_sha256':digest(url),'document_ids':sorted(ids)} for url,ids in sorted(urls.items()) if len(ids)>1]
    if collisions:errors.append('DUPLICATE_CANONICAL_URL')
    reviews=[]
    for key,variants in sorted(grouped.items()):
        original=set(v['body'] for v in variants)
        changed_meta=set(v['meta'] for v in variants)
        changed_sources=set(v['source_ids'] for v in variants)
        changed_safety=set(v['safety'] for v in variants)
        changed_urls=set(v['url'] for v in variants)
        changed_cites=set(v['citation_ids'] for v in variants)
        if len(variants)>1 and any(len(s)>1 for s in (original,changed_meta,changed_sources,changed_safety,changed_urls,changed_cites)):
            reviews.append({'document_id':key,'contributors':sorted(v['branch'] for v in variants),
                            'body_sha256':sorted(original),'min_words':min(v['body_words'] for v in variants),
                            'max_words':max(v['body_words'] for v in variants),
                            'metadata_sha256':sorted(changed_meta),
                            'source_set_sha256':sorted(digest(repr(s)) for s in changed_sources),
                            'safety_variants':sorted(str(s) for s in changed_safety),
                            'url_sha256':sorted(digest(str(u)) for u in changed_urls),
                            'citation_sequence_sha256':sorted(digest(repr(s)) for s in changed_cites),
                            'review_required':True})
    if require_full and (sum(k.startswith('articles/') for k in grouped)!=35 or sum(k.startswith('tools/') for k in grouped)!=6):
        errors.append('UNION_NOT_35_ARTICLES_6_TOOLS')
    if reviews:errors.append('UNRESOLVED_MULTIBRANCH_CONTENT_CONFLICTS')
    return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if errors else 'DRAFT_REVIEW_ONLY_HARD_HOLD',
            'errors':sorted(set(errors)),'branch_count':len(inventory),'branch_documents':inventory,
            'unique_documents':len(grouped),'article_count':sum(k.startswith('articles/') for k in grouped),
            'tool_count':sum(k.startswith('tools/') for k in grouped),
            'manual_review':reviews,'duplicate_url_review':collisions,
            'private_manuscript_text_exported':False,**HOLD}


def _git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],check=True,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=30).stdout


def audit_repo(root:Path):
    """No checkout or remote fetch. Reads only exact local Git refs and tree blobs."""
    snapshots={};errors=[]
    try:
        for branch,pin in PINS.items():
            ref=_git(root,'rev-parse','--verify','refs/heads/'+branch).decode().strip()
            if ref!=pin:errors.append('LIVE_BRANCH_HEAD_CHANGED:'+branch);continue
            raw=_git(root,'ls-tree','-r','-z',pin,'--','preparedness/content/')
            files={}
            for entry in raw.split(b'\0'):
                if not entry:continue
                head,path=entry.split(b'\t',1);mode,typ,blob=head.decode().split()
                if mode!='100644' or typ!='blob':errors.append('NONREGULAR_SOURCE_OBJECT:'+branch);continue
                path=path.decode('utf-8')
                if path.endswith(('.body.html','.meta.json')):
                    files[path]=_git(root,'cat-file','blob',blob)
            docs=[]
            for path,body in sorted(files.items()):
                if not path.endswith('.body.html'):continue
                meta_path=path[:-10]+'.meta.json'
                if meta_path not in files:errors.append('MISSING_META:'+branch+':'+path);continue
                kind=path.split('/')[2];slug=Path(path).name.removesuffix('.body.html')
                docs.append({'id':kind+'/'+slug,'body':body.decode('utf-8'),'meta':json.loads(files[meta_path])})
            if len(docs)!=sum(p.endswith('.meta.json') for p in files):errors.append('UNPAIRED_METADATA:'+branch)
            snapshots[branch]={'sha':ref,'documents':docs}
    except (OSError,ValueError,KeyError,UnicodeError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        errors.append('NATIVE_GIT_CUSTODY_UNAVAILABLE:'+type(exc).__name__)
    out=ledger(snapshots)
    out['errors']=sorted(set(out['errors']+errors))
    if out['errors']:out['status']='INVALID_HARD_HOLD'
    return out


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2]);a=parser.parse_args()
    print(json.dumps(audit_repo(a.repo_root),sort_keys=True,indent=2));return 2

if __name__=='__main__':raise SystemExit(main())
