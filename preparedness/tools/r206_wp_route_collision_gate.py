#!/usr/bin/env python3
"""R206: fail-closed 35-slate -> read-only WordPress inventory route overlap preflight.

Snapshot input is obtained separately by a reader with pagination; this script never
calls WordPress, creates content, approves sources, or grants a release gate.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

SCHEMA='fv-preparedness-r206-wp-route-preflight-v1'
FROZEN='5822f9dfde21d1f3bdfc26658769d852c639438c'
HOLD='DRAFT_HARD_HOLD'
INVALID='INVALID_HARD_HOLD'
SLUG=re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SHA=re.compile(r'[a-f0-9]{40}\Z')
STATES={'publish','draft','pending','private','future'}

class Invalid(ValueError): pass

def require(test,msg):
    if not test: raise Invalid(msg)

def git_oid(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def strict_json(data):
    def pairs(items):
        output={}
        for key,value in items:
            require(key not in output,'duplicate JSON key: '+str(key))
            output[key]=value
        return output
    def reject(value): raise Invalid('invalid JSON constant: '+value)
    return json.loads(data.decode('utf8'),object_pairs_hook=pairs,parse_constant=reject)

def safe_slug(value):
    require(type(value) is str and SLUG.fullmatch(value) is not None,'invalid WP slug')
    return value

def route(url):
    require(type(url) is str and len(url)<=2048,'invalid WP link')
    u=urlsplit(url)
    require(u.scheme=='https' and u.netloc.lower()=='finalvestige.com' and not u.username
            and not u.password and not u.fragment,'WP link outside canonical host')
    path=unquote(u.path)
    require(not any(x in path for x in ('\\','//','..','\x00')) and
            not re.search(r'[^/a-z0-9-]',path),'invalid canonical WP route')
    if u.query:
        require(path in ('','/') and re.fullmatch(r'(page_id|p)=[0-9]+',u.query),
                'unknown draft preview query')
        return None
    return '/'+path.strip('/')+'/' if path.strip('/') else '/'

def audit(manifest,snapshot):
    out={'schema':SCHEMA,'issue':136,'coordination_issue':820,'state':INVALID,
         'publication_authorized':False,'independent_qd_pass':False,
         'source_approved':False,'merchant_verified':False,
         'paid_orders':None,'net_revenue_per_1000':None,'errors':[],
         'confirmed_route_conflicts':[],'potential_slug_conflicts':[],
         'nonconflicting_drafts':[],'summary':{}}
    try:
        require(type(manifest) is dict and manifest.get('schema')==
                'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1'
                and manifest.get('issue')==136 and manifest.get('conversion_issue')==820,
                'R200 manifest identity invalid')
        require(manifest.get('state')==HOLD and
                manifest.get('publication_authorized') is False and
                manifest.get('independent_qd_pass') is False,
                'R200 publication/QD governance changed')
        rows=manifest.get('articles'); heads=manifest.get('branch_heads')
        require(type(rows) is list and len(rows)==35 and type(heads) is dict and
                len(heads)==7 and manifest.get('artifact_count')==35 and
                manifest.get('export_target_count_with_six_tools')==41,
                '35 articles / seven branches / 41 export targets required')
        originals={};slugs=set()
        for n,r in enumerate(rows,1):
            require(type(r) is dict and type(r.get('slug')) is str,'invalid article row')
            slug=safe_slug(r['slug']); section=safe_slug(r.get('section'))
            planned=f'/preparedness/{section}/{slug}/'
            require(type(r.get('n')) is int and r['n']==n and r.get('route')==planned
                    and planned not in originals and slug not in slugs and
                    r.get('source_cluster') in heads and
                    r.get('branch_sha')==heads[r['source_cluster']] and
                    all(type(r.get(key)) is str and SHA.fullmatch(r[key]) for key in ('body_oid','meta_oid')),
                    'duplicate/slate route/branch/blob drift')
            originals[planned]=r;slugs.add(slug)
        require(type(snapshot) is dict and snapshot.get('site')=='https://finalvestige.com'
                and snapshot.get('complete') is True and snapshot.get('read_only') is True,
                'incomplete/unauthenticated CMS snapshot')
        stamp=snapshot.get('captured_at')
        require(type(stamp) is str and stamp.endswith('Z'), 'missing UTC snapshot time')
        timestamp=dt.datetime.fromisoformat(stamp.replace('Z','+00:00'))
        require(timestamp.year>=2026 and timestamp.tzinfo is not None,
                'invalid snapshot timestamp')
        pages=snapshot.get('pages'); posts=snapshot.get('posts'); totals=snapshot.get('totals')
        require(type(pages) is list and type(posts) is list and type(totals) is dict and
                totals=={'pages':len(pages),'posts':len(posts)},
                'unpaginated or incomplete WP inventory')
        require(len(pages)+len(posts)<20000,'unreasonable CMS inventory')
        ids=set();byid={};records=[]
        for kind,items in (('page',pages),('post',posts)):
            for record in items:
                require(type(record) is dict and set(record)==
                        {'id','slug','status','parent','link','modified','title'},
                        'WP record fields incomplete/unexpected')
                ident=record['id'];slug=safe_slug(record['slug'])
                require(type(ident) is int and ident>0 and (kind,ident) not in ids and
                        record['status'] in STATES and
                        type(record['parent']) is int and record['parent']>=0 and
                        type(record['modified']) is str and record['modified'] and
                        type(record['title']) is str and record['title'].strip(),
                        'invalid/duplicate WP record')
                ids.add((kind,ident));records.append((kind,record))
                if kind=='page': byid[ident]=record
        archive=[p for p in pages if p['id']==1868]
        require(len(archive)==1 and archive[0]['slug']=='preparedness' and
                archive[0]['status']=='publish' and archive[0]['parent']==0 and
                route(archive[0]['link'])=='/preparedness/',
                'public archive anchor is missing or moved')
        computed={};published=set()
        def page_path(ident,stack=()):
            require(ident in byid,'missing WP page parent')
            require(ident not in stack,'cycle in WP pages')
            r=byid[ident]
            require(len(stack)<30,'excessive WP nesting')
            prefix=page_path(r['parent'],stack+(ident,)) if r['parent'] else '/'
            result=prefix+r['slug']+'/'
            computed[ident]=result
            return result
        for kind,p in records:
            path=page_path(p['id']) if kind=='page' else route(p['link'])
            explicit=route(p['link'])
            if p['status']=='publish':
                require(explicit is not None,'published WP entry cannot use preview route')
                if kind=='page':
                    require(explicit==path,'published page permalink/parent mismatch')
                require(explicit not in published,'duplicate published WP permalinks')
                published.add(explicit)
            if path in originals or explicit in originals:
                out['confirmed_route_conflicts'].append({'kind':kind,'wp_id':p['id'],
                    'wp_status':p['status'],'original_slug':originals.get(path,originals.get(explicit))['slug'],
                    'candidate_route':path})
            elif p['slug'] in slugs:
                out['potential_slug_conflicts'].append({'kind':kind,'wp_id':p['id'],
                    'wp_status':p['status'],'slug':p['slug'],
                    'reason':'slug matches frozen article; WordPress destination may differ'})
            elif p['status']!='publish' and kind=='page' and path.startswith('/preparedness/'):
                out['nonconflicting_drafts'].append({'wp_id':p['id'],'slug':p['slug'],
                    'candidate_route_not_live':path})
        out['confirmed_route_conflicts'].sort(key=lambda x:(x['wp_id'],x['kind']))
        out['potential_slug_conflicts'].sort(key=lambda x:(x['wp_id'],x['kind']))
        out['nonconflicting_drafts'].sort(key=lambda x:x['wp_id'])
        out['summary']={'frozen_articles':35,'export_targets_not_verified':41,
                        'wp_pages_observed':len(pages),'wp_posts_observed':len(posts),
                        'snapshot_captured_at':stamp,
                        'confirmed_conflicts':len(out['confirmed_route_conflicts']),
                        'possible_conflicts':len(out['potential_slug_conflicts']),
                        'draft_routes_not_live':len(out['nonconflicting_drafts']),
                        'native_build_executed':False,'all_public_urls_tested':False}
        out['state']=HOLD
    except (Invalid,ValueError,KeyError,TypeError,AttributeError,OverflowError) as err:
        out['errors']=[str(err)[:300]]
        out['confirmed_route_conflicts']=[];out['potential_slug_conflicts']=[]
        out['nonconflicting_drafts']=[];out['summary']={}
    return out

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True);p.add_argument('--snapshot',required=True)
    p.add_argument('--report');args=p.parse_args(argv)
    try:
        raw=Path(args.manifest).read_bytes()
        require(git_oid(raw)==FROZEN,'R200 manifest Git object drift')
        manifest=strict_json(raw)
        snapshot=strict_json(Path(args.snapshot).read_bytes())
        report=audit(manifest,snapshot)
    except (OSError,Invalid,ValueError,UnicodeError,TypeError) as err:
        report={'schema':SCHEMA,'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(err)[:300]]}
    data=json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+'\n'
    if args.report:Path(args.report).write_text(data,encoding='utf8')
    else:print(data,end='')
    return 2 if report['state']==HOLD else 3

if __name__=='__main__':raise SystemExit(main())
