#!/usr/bin/env python3
"""R351 builder-derived Preparedness routes; never a publication/safety approval.

Unlike metadata-only URL audits, this verifies the actual builder's url_path logic
and derives paths from section+slug. It refuses overwritten tool/article slugs,
route drift and incomplete 35+6 inventory without touching source/CMS.
"""
from __future__ import annotations
import ast
from collections import defaultdict
from hashlib import sha1, sha256
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote
import importlib.util
_prior_path=Path(__file__).resolve().with_name('r350_nine_branch_content_custody_hold.py')
_spec=importlib.util.spec_from_file_location('r350_nine_branch_content_custody_hold',_prior_path)
prior=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prior)

SCHEMA = 'fv-preparedness-r351-canonical-route-custody-v1'
BUILDER_BLOB = '349173d1e1d735eade218d95c7a0a2649c8cccd9'
BASE = '/preparedness/'
SEG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
HOLD = {'may_publish':False,'may_merge':False,'qualified_qd_pass':False,
        'human_link_check_verified':False,'independent_claim_support_verified':False,
        'native_build_verified':False,'commerce_offer_verified':False,
        'verified_paid_orders':False,'private_manuscript_text_exported':False}

def blob(b):return sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def digest(s):return sha256(s.encode()).hexdigest()
def segment(v):return isinstance(v,str) and bool(SEG.fullmatch(v))

def builder_contract(source):
    """Require exact AST of both actual routes, no import/execution of untrusted code."""
    try:
        tree=ast.parse(source)
        lib=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Library')
        got={n.name:n for n in lib.body if isinstance(n,ast.FunctionDef)}
        sample=ast.parse('''class Library:
    def url_path(self, slug: str) -> str:
        a = self.articles.get(slug) or self.slate[slug]
        return f"{self.taxonomy['base_path']}{a['section']}/{slug}/"
    def section_path(self, section: str) -> str:
        return f"{self.taxonomy['base_path']}{section}/"
''').body[0]
        ref={n.name:n for n in sample.body}
        return all(k in got and ast.dump(got[k],include_attributes=False)==ast.dump(ref[k],include_attributes=False)
                   for k in ('url_path','section_path'))
    except (StopIteration,SyntaxError,TypeError,ValueError):return False

def audit(taxonomy, documents, source, *, full=True, exact_builder=False):
    """Documents: [{kind:'articles'|'tools',meta:{...}}]; only hashes exported."""
    err=[]; ids=set(); slugs=defaultdict(set); path_ids=defaultdict(set); path_hashes={}
    if not isinstance(taxonomy,dict) or not isinstance(documents,list):
        return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD','errors':['INVALID_INPUT'],**HOLD}
    if not isinstance(source,str) or not builder_contract(source):err.append('BUILDER_ROUTE_CONTRACT_DRIFT')
    if exact_builder and (not isinstance(source,str) or blob(source.encode())!=BUILDER_BLOB):
        err.append('INTEGRATION_BUILDER_BLOB_DRIFT')
    if taxonomy.get('base_path')!=BASE:err.append('BASE_PATH_CHANGED')
    sections=taxonomy.get('sections',[])
    sections=[s.get('slug') for s in sections] if isinstance(sections,list) else []
    if any(not segment(s) for s in sections) or len(set(sections))!=len(sections):
        err.append('UNSAFE_OR_DUPLICATE_SECTIONS')
    if full and len(sections)!=8:err.append('SECTION_INVENTORY_NOT_EIGHT')
    expected={}
    for kind,field in [('articles','slate'),('tools','tools')]:
        rows=taxonomy.get(field,[])
        if not isinstance(rows,list):rows=[];err.append('INVALID_'+field.upper())
        keys=[row.get('slug') for row in rows if isinstance(row,dict)]
        if len(keys)!=len(rows) or any(not segment(k) for k in keys) or len(keys)!=len(set(keys)):
            err.append('UNSAFE_OR_DUPLICATE_'+field.upper())
        expected[kind]=set(k for k in keys if segment(k))
    if full and (len(expected['articles'])!=35 or len(expected['tools'])!=6):
        err.append('TAXONOMY_NOT_35_PLUS_6')
    for d in documents:
        if not isinstance(d,dict) or d.get('kind') not in expected or not isinstance(d.get('meta'),dict):
            err.append('INVALID_DOCUMENT');continue
        kind=d['kind'];m=d['meta'];slug=m.get('slug');section=m.get('section')
        if not segment(slug) or not segment(section):err.append('UNSAFE_DOCUMENT_ROUTE');continue
        key=kind+'/'+slug
        if key in ids:err.append('DUPLICATE_DOCUMENT:'+key)
        ids.add(key);slugs[slug].add(kind)
        if slug not in expected[kind]:err.append('DOCUMENT_NOT_IN_TAXONOMY:'+key)
        if section not in sections:err.append('UNKNOWN_SECTION:'+key)
        if kind=='articles':
            row=next((s for s in taxonomy.get('slate',[]) if isinstance(s,dict) and s.get('slug')==slug),None)
            if row and row.get('section')!=section:err.append('TAXONOMY_SECTION_MISMATCH:'+key)
        if not isinstance(m.get('status'),dict) or m['status'].get('publish')!='draft':
            err.append('PUBLICATION_STATE_NOT_DRAFT:'+key)
        safety=m.get('safety_review')
        if not isinstance(safety,dict) or safety.get('state') not in ('pending','not-required'):
            err.append('SAFETY_STATE_NOT_PENDING:'+key)
        route=BASE+section+'/'+slug+'/'
        for hint in ('canonical_url','permalink','url'):
            if hint in m and m[hint] not in (route,'https://finalvestige.com'+route):
                err.append('EXPLICIT_URL_CONFLICT:'+key+':'+hint)
        normalized=unquote(route).casefold().rstrip('/')+'/'
        path_ids[normalized].add(key);path_hashes[key]=digest(route)
    for slug,kinds in slugs.items():
        if len(kinds)>1:err.append('BUILDER_ARTICLE_TOOL_OVERWRITE:'+slug)
    for path,names in path_ids.items():
        if len(names)>1:err.append('DUPLICATE_DERIVED_ROUTE:'+digest(path))
    if full:
        for kind in expected:
            found={k.split('/',1)[1] for k in ids if k.startswith(kind+'/')}
            if found!=expected[kind]:err.append('INCOMPLETE_'+kind.upper()+'_INVENTORY')
    return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if err else 'DRAFT_ROUTE_PARITY_ONLY_HARD_HOLD',
            'errors':sorted(set(err)),'article_count':sum(x.startswith('articles/') for x in ids),
            'tool_count':sum(x.startswith('tools/') for x in ids),
            'route_sha256_by_document':dict(sorted(path_hashes.items())),
            'routes_not_verified_on_live_wordpress':True,**HOLD}

def compare(snapshots,pins=prior.PINS):
    err=[];seen=defaultdict(set)
    if not isinstance(snapshots,dict):snapshots={};err.append('INVALID_SNAPSHOTS')
    for name,pin in sorted(pins.items()):
        item=snapshots.get(name)
        if not isinstance(item,dict):err.append('MISSING_BRANCH:'+name);continue
        if item.get('sha')!=pin:err.append('SHA_DRIFT:'+name);continue
        result=audit(item.get('taxonomy'),item.get('documents'),item.get('builder'),full=False)
        err.extend(name+':'+e for e in result['errors'])
        for key,val in result.get('route_sha256_by_document',{}).items():seen[key].add(val)
    err.extend('UNPINNED_BRANCH:'+k for k in set(snapshots)-set(pins))
    conflicts=sorted(k for k,v in seen.items() if len(v)>1)
    if conflicts:err.append('CROSS_BRANCH_ROUTE_DRIFT')
    return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if err else 'DRAFT_ROUTE_PARITY_ONLY_HARD_HOLD',
            'errors':sorted(set(err)),'route_conflict_document_ids':conflicts,'original_union_count':len(seen),**HOLD}

def _git_snapshot(root,commit):
    tax=json.loads(prior._git(root,'show',commit+':preparedness/taxonomy.json'))
    src=prior._git(root,'show',commit+':preparedness/tools/build.py').decode()
    entries=prior._git(root,'ls-tree','-r','-z',commit,'--','preparedness/content/')
    files={}
    for e in entries.split(b'\0'):
        if not e:continue
        head,name=e.split(b'\t',1);mode,typ,sha=head.decode().split();name=name.decode()
        if name.endswith(('.meta.json','.body.html')):
            if mode!='100644' or typ!='blob':raise ValueError('NONREGULAR_SOURCE_OBJECT')
            files[name]=sha
    docs=[]
    for path,obj in files.items():
        if not path.endswith('.meta.json'):continue
        body=path[:-10]+'.body.html'
        if body not in files:raise ValueError('MISSING_BODY_OBJECT')
        m=json.loads(prior._git(root,'cat-file','blob',obj))
        if m.get('slug')!=Path(path).name.removesuffix('.meta.json'):
            raise ValueError('METADATA_FILENAME_SLUG_DRIFT')
        docs.append({'kind':path.split('/')[2],'meta':m})
    if len(docs)!=sum(k.endswith('.body.html') for k in files):raise ValueError('ORPHANED_BODY_OBJECT')
    return {'taxonomy':tax,'documents':docs,'builder':src}

def audit_git_repo(root,ref='HEAD'):
    """Read only original source commit trees; never checkout or publish."""
    try:
        root=Path(root).resolve(strict=True)
        if root!=Path(prior._git(root,'rev-parse','--show-toplevel').decode().strip()).resolve():
            raise ValueError('WRONG_REPOSITORY_ROOT')
        snaps={}
        for branch,pin in prior.PINS.items():
            sha=prior._git(root,'rev-parse','--verify','refs/heads/'+branch).decode().strip()
            if sha!=pin:raise ValueError('CONTRIBUTOR_SHA_DRIFT')
            snaps[branch]={'sha':sha,**_git_snapshot(root,pin)}
        merged_ref=prior._git(root,'rev-parse','--verify',ref).decode().strip()
        integrated=audit(**_git_snapshot(root,merged_ref),full=True,exact_builder=True)
        original=compare(snaps)
        ids=set(integrated.get('route_sha256_by_document',{}))
        original_ids=set(k for s in snaps.values() for k in audit(s['taxonomy'],s['documents'],s['builder'],full=False).get('route_sha256_by_document',{}))
        err=integrated['errors']+original['errors']
        if original_ids-ids:err.append('ORIGINAL_DOCUMENTS_MISSING_FROM_INTEGRATION')
        return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if err else 'DRAFT_ROUTE_PARITY_ONLY_HARD_HOLD',
                'errors':sorted(set(err)),'integration_commit':merged_ref,'original_count':len(original_ids),
                'integrated_count':len(ids),'missing_original_ids':sorted(original_ids-ids),
                'cross_branch_conflicts':original['route_conflict_document_ids'],**HOLD}
    except (OSError,ValueError,KeyError,UnicodeError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD',
                'errors':['NATIVE_GIT_CUSTODY_UNAVAILABLE:'+type(e).__name__],**HOLD}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--integration-ref',default='HEAD')
    a=p.parse_args();print(json.dumps(audit_git_repo(a.repo_root,a.integration_ref),sort_keys=True,indent=2));raise SystemExit(2)
