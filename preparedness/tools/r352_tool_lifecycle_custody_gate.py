#!/usr/bin/env python3
"""R352: fail-closed Planned-vs-Authored tool custody; review-only, never QD PASS.

Corrects the R351 assumption that the nine-tool taxonomy is a six-tool list.
Six tools are authored and three are not-started placeholders. Neither fact is
release approval; duplicate display numbers require an independent decision.
No filesystem mutation, publishing, merchant, navigation, or analytics actions.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('r351_canonical_route_gate', Path(__file__).resolve().with_name('r351_canonical_route_gate.py'))
r351 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r351)
SCHEMA = 'fv-preparedness-r352-planned-authored-tool-custody-v1'
TAXONOMY_BLOB = '15c547bb3018ac182b12a51036389cfa39a59168'
BUILDER_BLOB = r351.BUILDER_BLOB
BASE = '/preparedness/'
EXPECTED_TOOL_PLAN = frozenset({'water-planner','pantry-worksheet','home-fire-escape-worksheet',
                                'power-outage-planner','family-reunification-card',
                                'reunification-plan','kit-builder','checklists','offline-reference'})
EXPECTED_DRAFTED = frozenset({'water-planner','home-fire-escape-worksheet','power-outage-planner',
                              'family-reunification-card','reunification-plan','kit-builder'})
EXPECTED_NOT_STARTED = EXPECTED_TOOL_PLAN - EXPECTED_DRAFTED
SEG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
HOLD = {'may_merge':False,'may_publish':False,'qualified_qd_pass':False,
        'independent_emergency_or_medical_claim_approval':False,
        'native_validation_build_pass':False,'live_wordpress_routes_verified':False,
        'paid_offer_verified':False,'verified_paid_orders':False,
        'private_body_text_in_report':False}

def digest(s): return sha256(s.encode('utf-8')).hexdigest()
def blob(raw): return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def safe_slug(v): return isinstance(v,str) and bool(SEG.fullmatch(v))

def audit(taxonomy, documents, builder, *, strict=True, exact_builder=False,
          taxonomy_raw=None):
    """Non-mutating review of full article/tool inventory and tool numbering.

    documents: [{'kind':'articles'|'tools','meta':dict,'body':str}].
    Never outputs manuscript text; all putative approvals remain false.
    """
    errors=[]; notices=[]; plan={}; tools={}; ids=set(); routes={}; numbers=defaultdict(list)
    if not isinstance(taxonomy,dict) or not isinstance(documents,list) or not isinstance(builder,str):
        return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD','errors':['INVALID_INPUT'],**HOLD}
    if not r351.builder_contract(builder): errors.append('ROUTE_BUILDER_CONTRACT_DRIFT')
    if exact_builder and blob(builder.encode('utf-8')) != BUILDER_BLOB: errors.append('BUILDER_BLOB_DRIFT')
    if taxonomy_raw is not None and (not isinstance(taxonomy_raw,bytes) or blob(taxonomy_raw)!=TAXONOMY_BLOB):
        errors.append('TAXONOMY_BLOB_DRIFT')
    if taxonomy.get('base_path') != BASE: errors.append('BASE_PATH_DRIFT')
    sections=taxonomy.get('sections')
    sec=[x.get('slug') for x in sections if isinstance(x,dict)] if isinstance(sections,list) else []
    if len(sec)!=8 or len(set(sec))!=len(sec) or any(not safe_slug(x) for x in sec):
        errors.append('INVALID_SECTION_TAXONOMY')
    slate=taxonomy.get('slate')
    if not isinstance(slate,list): slate=[]; errors.append('INVALID_ARTICLE_SLATE')
    expected_articles={}
    for row in slate:
        if not isinstance(row,dict) or not safe_slug(row.get('slug')) or not safe_slug(row.get('section')):
            errors.append('INVALID_ARTICLE_TAXONOMY_ROW');continue
        k=row['slug']
        if k in expected_articles: errors.append('DUPLICATE_ARTICLE_TAXONOMY:'+k)
        expected_articles[k]=row['section']
    if len(expected_articles)!=35: errors.append('ARTICLE_SLATE_NOT_35')
    rows=taxonomy.get('tools')
    if not isinstance(rows,list): rows=[];errors.append('INVALID_TOOL_PLAN')
    for row in rows:
        if not isinstance(row,dict) or not safe_slug(row.get('slug')):
            errors.append('INVALID_TOOL_PLAN_ROW');continue
        slug=row['slug'];state=row.get('status')
        if slug in plan: errors.append('DUPLICATE_TOOL_PLAN:'+slug)
        if state not in ('drafted-pending-safety-review','not-started'):
            errors.append('UNRECOGNIZED_TOOL_LIFECYCLE:'+slug)
        if state=='drafted-pending-safety-review' and row.get('gate') is not True:
            errors.append('DRAFTED_TOOL_WITHOUT_GATE:'+slug)
        if state=='not-started' and row.get('gate') is True:
            notices.append('NOT_STARTED_TOOL_PREDECLARED_GATE:'+slug)
        plan[slug]=state
    if len(plan)!=9 or frozenset(plan)!=EXPECTED_TOOL_PLAN: errors.append('TOOL_PLAN_NOT_NINE_AUTHENTIC_SLUGS')
    drafted={k for k,v in plan.items() if v=='drafted-pending-safety-review'}
    not_started={k for k,v in plan.items() if v=='not-started'}
    if strict and (drafted!=EXPECTED_DRAFTED or not_started!=EXPECTED_NOT_STARTED):
        errors.append('PLANNED_AUTHORED_STATUS_DRIFT')
    article_ids=set(); tool_ids=set()
    for item in documents:
        if not isinstance(item,dict) or item.get('kind') not in ('articles','tools') or not isinstance(item.get('meta'),dict):
            errors.append('INVALID_DOCUMENT');continue
        kind=item['kind'];meta=item['meta'];slug=meta.get('slug');body=item.get('body')
        if not safe_slug(slug): errors.append('UNSAFE_DOCUMENT_SLUG');continue
        k=kind+'/'+slug
        if k in ids: errors.append('DUPLICATE_MANUSCRIPT_ID:'+k)
        ids.add(k)
        (article_ids if kind=='articles' else tool_ids).add(slug)
        if not isinstance(body,str) or not body.strip(): errors.append('EMPTY_OR_MISSING_BODY:'+k)
        status=meta.get('status')
        if not isinstance(status,dict) or status.get('publish')!='draft':
            errors.append('NON_DRAFT_PUBLICATION_STATE:'+k)
        safety=meta.get('safety_review')
        if not isinstance(safety,dict) or safety.get('state') not in ('pending','not-required'):
            errors.append('UNACCEPTABLE_SAFETY_STATE:'+k)
        if kind=='tools':
            if slug not in plan: errors.append('UNLISTED_AUTHORED_TOOL:'+slug)
            if plan.get(slug)=='not-started': errors.append('NOT_STARTED_TOOL_HAS_MANUSCRIPT:'+slug)
            if meta.get('section')!='field-tools' or meta.get('track')!='modern' or not isinstance(safety,dict) or safety.get('state')!='pending':
                errors.append('TOOL_SAFETY_OR_SECTION_DRIFT:'+slug)
            n=meta.get('n')
            if type(n) is not int or n < 1: errors.append('INVALID_TOOL_NUMBER:'+slug)
            else: numbers[n].append(slug)
            tools[slug]={'meta_sha256':digest(json.dumps(meta,sort_keys=True,ensure_ascii=False)),
                         'body_sha256':digest(body) if isinstance(body,str) else None}
        elif slug not in expected_articles: errors.append('UNLISTED_ARTICLE:'+slug)
        elif meta.get('section')!=expected_articles[slug]: errors.append('ARTICLE_SECTION_DRIFT:'+slug)
        section=meta.get('section')
        if safe_slug(section):
            route=BASE+section+'/'+slug+'/'
            if route in routes and routes[route]!=k: errors.append('DERIVED_ROUTE_COLLISION:'+digest(route))
            routes[route]=k
            for hint in ('url','canonical_url','permalink'):
                if hint in meta and meta[hint] not in (route,'https://finalvestige.com'+route):
                    errors.append('CONTRADICTORY_URL:'+k)
    if article_ids!=set(expected_articles): errors.append('ARTICLE_BODY_SLATE_MISMATCH')
    if tool_ids!=drafted: errors.append('AUTHORED_TOOLS_DO_NOT_MATCH_DRAFTED_PLAN')
    if tool_ids & not_started: errors.append('PLANNED_ONLY_TOOL_HAS_BODY')
    collisions={str(n):sorted(slugs) for n,slugs in sorted(numbers.items()) if len(slugs)>1}
    if collisions: errors.append('DUPLICATE_TOOL_DISPLAY_NUMBERS_REQUIRE_REVIEW')
    if len(article_ids)!=35 or len(tool_ids)!=6: errors.append('AUTHORED_COUNT_NOT_35_PLUS_6')
    return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if errors else 'DRAFT_CUSTODY_ONLY_HARD_HOLD',
            'errors':sorted(set(errors)),'notices':sorted(set(notices)),
            'planned_tool_count':len(plan),'drafted_tool_count':len(drafted),
            'not_started_tool_count':len(not_started),'authored_tool_count':len(tool_ids),
            'authored_article_count':len(article_ids),
            'planned_only_slugs':sorted(not_started),'authored_tool_slugs':sorted(tool_ids),
            'duplicate_tool_display_numbers':collisions,
            'tools_fingerprints':dict(sorted(tools.items())),**HOLD}

def git_audit(repo:Path, integration_ref='HEAD'):
    """Exact read-only Git-object audit; fails with no authenticated full checkout."""
    try:
        repo=Path(repo).resolve(strict=True)
        if repo!=Path(r351.prior._git(repo,'rev-parse','--show-toplevel').decode().strip()).resolve():
            raise ValueError('WRONG_GIT_ROOT')
        for branch,pin in sorted(r351.prior.PINS.items()):
            got=r351.prior._git(repo,'rev-parse','--verify','refs/heads/'+branch).decode().strip()
            if got!=pin: raise ValueError('ORIGINAL_BRANCH_SHA_DRIFT:'+branch)
        ref=r351.prior._git(repo,'rev-parse','--verify',integration_ref).decode().strip()
        tax_raw=r351.prior._git(repo,'show',ref+':preparedness/taxonomy.json')
        builder=r351.prior._git(repo,'show',ref+':preparedness/tools/build.py').decode('utf-8')
        tree=r351.prior._git(repo,'ls-tree','-r','-z',ref,'--','preparedness/content/')
        files={}
        for item in tree.split(b'\0'):
            if not item: continue
            descriptor,path=item.split(b'\t',1);mode,typ,sha=descriptor.decode().split();p=path.decode()
            if p.startswith(('preparedness/content/articles/','preparedness/content/tools/')) and p.endswith(('.body.html','.meta.json')):
                if mode!='100644' or typ!='blob': raise ValueError('NONREGULAR_CANONICAL_DOCUMENT')
                files[p]=sha
        documents=[]
        for path in sorted(files):
            if not path.endswith('.meta.json'):continue
            base=path[:-10];body_path=base+'.body.html'
            if body_path not in files:raise ValueError('MISSING_CANONICAL_BODY')
            m=json.loads(r351.prior._git(repo,'cat-file','blob',files[path]))
            if m.get('slug')!=Path(base).name: raise ValueError('FILENAME_SLUG_DRIFT')
            body=r351.prior._git(repo,'cat-file','blob',files[body_path]).decode('utf-8')
            documents.append({'kind':path.split('/')[2],'meta':m,'body':body})
        if len(documents)!=sum(p.endswith('.body.html') for p in files):
            raise ValueError('ORPHAN_CANONICAL_BODY')
        out=audit(json.loads(tax_raw),documents,builder,strict=True,exact_builder=True,taxonomy_raw=tax_raw)
        out['integration_commit']=ref
        return out
    except (OSError,ValueError,KeyError,UnicodeError,json.JSONDecodeError,
            subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD',
                'errors':['NATIVE_GIT_CUSTODY_UNAVAILABLE:'+type(e).__name__],**HOLD}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=ROOT)
    p.add_argument('--integration-ref',default='HEAD');a=p.parse_args()
    print(json.dumps(git_audit(a.repo_root,a.integration_ref),sort_keys=True,indent=2))
    raise SystemExit(2)
