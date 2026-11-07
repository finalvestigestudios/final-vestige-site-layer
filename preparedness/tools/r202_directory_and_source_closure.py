#!/usr/bin/env python3
"""Fail-closed Preparedness seven-branch directory and scoped-source custody.

DRAFT_HARD_HOLD is structural custody, never QD/safety/commerce approval.
Do not execute against a synthetic fixture in place of a trusted repo build.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = 'preparedness/content/articles/'
MANIFEST_PATH = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
MANIFEST_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
BASE_SOURCES_OID = 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'
SCHEMA = 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1'
REPORT_SCHEMA = 'fv-preparedness-r202-directory-and-source-closure-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
HEADS = {
 'start': '2122d856fce9f64887c16df3d52e64be9f59a55b',
 'shelter': '5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
 'food': 'f911ff7a655de8d81535ea86ec3d65a49ee76648',
 'health': 'd5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
 'hist-field': '4e5caf812727953aa45e3bda2d382f2c67b6a09c',
 'hist-food': '67e116e536c7410bed30f8f3b1bb8c166f3c223d',
 'hist-home': '7504a5f099594d635e3dd7332a33a2e1346c43a2',
}
OID = re.compile(r'[0-9a-f]{40}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')

class Blocked(ValueError):
    pass

def demand(ok, why):
    if not ok:
        raise Blocked(why)

def oid(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def strict_json(data):
    def unique(pairs):
        d = {}
        for k,v in pairs:
            demand(k not in d, 'duplicate JSON key '+k)
            d[k] = v
        return d
    def constant(x):
        raise Blocked('invalid JSON constant '+x)
    return json.loads(data.decode('utf8'),object_pairs_hook=unique,parse_constant=constant)

def git(repo,*args):
    return subprocess.run(['git',*args],cwd=repo,check=True,timeout=60,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout

def exact_blob(repo,sha):
    demand(bool(OID.fullmatch(sha)),'invalid blob SHA')
    data=git(repo,'cat-file','blob',sha)
    demand(oid(data)==sha,'Git blob identity mismatch')
    return data

def branch_listing(repo,commit):
    demand(bool(OID.fullmatch(commit)),'invalid branch commit')
    raw=git(repo,'ls-tree','-r','-l','-z',commit,'--',ROOT)
    result={}
    for record in raw.split(b'\0'):
        if not record:
            continue
        header,sep,name=record.partition(b'\t')
        demand(bool(sep),'malformed ls-tree entry')
        mode,kind,sha,size=header.decode('ascii').split()
        path=name.decode('utf-8')
        demand(path not in result,'duplicate branch path')
        demand(size.isdigit(),'nonblob directory entry')
        result[path]=(mode,kind,sha,int(size))
    return result

def read_article_metadata(repo,manifest):
    result={}
    for row in manifest['articles']:
        slug=row['slug']; commit=HEADS[row['source_cluster']]
        path=ROOT+slug+'.meta.json'
        data=git(repo,'show',commit+':'+path)
        demand(oid(data)==row['meta_oid'] and len(data)==row['meta_bytes'],
               'unfrozen metadata '+slug)
        result[slug]=strict_json(data)
    return result

def read_source_registers(repo):
    src={'global':strict_json(exact_blob(repo,BASE_SOURCES_OID))}
    for cluster,sha in HEADS.items():
        path='preparedness/sources/fragments/'+cluster+'.json'
        src[cluster]=strict_json(git(repo,'show',sha+':'+path))
    return src

def check(manifest,trees,metadata,sources,*,strict=True):
    report={'schema':REPORT_SCHEMA,'issue':136,'conversion_issue':820,'state':INVALID,
      'publication_authorized':False,'independent_qd_pass':False,
      'human_source_approved':False,'medical_safety_verified':False,
      'merchant_offer_verified':False,'verified_paid_orders':None,
      'realized_net_revenue':None,'summary':{},'source_crosswalk':[],
      'ambiguous_origins':[], 'errors':[]}
    try:
        demand(type(manifest) is dict and manifest.get('schema')==SCHEMA,'wrong manifest schema')
        demand(manifest.get('issue')==136 and manifest.get('conversion_issue')==820,'governance drift')
        demand(manifest.get('state')==HOLD and manifest.get('branch_heads')==HEADS,'state/head drift')
        for flag in ('publication_authorized','independent_qd_pass','human_source_approved',
                     'medical_safety_verified','merchant_offer_verified'):
            demand(manifest.get(flag) is False,'unsupported approval '+flag)
        demand(manifest.get('verified_paid_orders') is None and manifest.get('realized_net_revenue') is None,
               'unsupported sales assertion')
        rows=manifest.get('articles')
        demand(type(rows) is list and (len(rows)==35 if strict else len(rows)>0),'article census')
        demand(manifest.get('artifact_count')==len(rows) and
               manifest.get('export_target_count_with_six_tools')==len(rows)+6,'export count')
        demand(type(trees) is dict and set(trees)==set(HEADS),'missing branch tree')
        demand(type(sources) is dict and set(sources)==set(HEADS)|{'global'},'source origins')
        demand(type(metadata) is dict and set(metadata)=={r['slug'] for r in rows},'metadata census')
        registry={}
        for origin,doc in sorted(sources.items()):
            entries=doc.get('sources') if type(doc) is dict else None
            demand(type(entries) is list,'source register malformed '+origin)
            registry[origin]={}
            for item in entries:
                ident=item.get('id') if type(item) is dict else None
                demand(type(ident) is str and SLUG.fullmatch(ident) and
                       ident not in registry[origin],'duplicate/invalid source '+origin)
                registry[origin][ident]=item
        expected={key:{} for key in HEADS}; seen=set();routes=set();total_uses=0
        for i,row in enumerate(rows,1):
            slug=row.get('slug');owner=row.get('source_cluster')
            demand(row.get('n')==i and type(slug) is str and SLUG.fullmatch(slug) and slug not in seen,
                   'duplicate/invalid article')
            seen.add(slug)
            demand(owner in HEADS and row.get('branch_sha')==HEADS[owner],'owner drift '+slug)
            section=row.get('section');route=row.get('route')
            demand(type(section) is str and SLUG.fullmatch(section) and
                   route==f'/preparedness/{section}/{slug}/' and route not in routes,'route drift '+slug)
            routes.add(route)
            witnesses=row.get('also_in')
            demand(type(witnesses) is list and witnesses and witnesses[0]==owner and
                   len(set(witnesses))==len(witnesses) and set(witnesses)<=set(HEADS),'witness drift')
            meta=metadata[slug]
            demand(type(meta) is dict and (meta.get('n'),meta.get('slug'),meta.get('section'),
                   meta.get('track'))==(i,slug,section,row.get('track')),'article metadata drift '+slug)
            status=meta.get('status');safety=meta.get('safety_review')
            demand(type(status) is dict and status.get('publish')=='draft','published metadata '+slug)
            demand(type(safety) is dict and safety.get('state')=='pending' and
                   safety.get('reviewer') is None and safety.get('date') is None,
                   'unapproved safety transition '+slug)
            uses=meta.get('source_use')
            demand(type(uses) is dict and bool(uses),'empty source-use '+slug)
            for sid,note in sorted(uses.items()):
                demand(type(sid) is str and SLUG.fullmatch(sid) and
                       type(note) is str and len(note.strip())>=12,
                       'unsupported source-use justification '+slug)
                possible=[origin for origin in ('global',owner) if sid in registry[origin]]
                demand(bool(possible),'source absent from article scope '+slug+': '+sid)
                item={'article':slug,'cluster':owner,'source_id':sid,
                      'eligible_origins':possible,
                      'reason_sha256':hashlib.sha256(note.encode('utf8')).hexdigest(),
                      'decision':'HUMAN_REVIEW_REQUIRED'}
                report['source_crosswalk'].append(item)
                if len(possible)>1:
                    report['ambiguous_origins'].append(item)
                total_uses+=1
            for b in witnesses:
                for suffix,field,sizefield in (('.body.html','body_oid','body_bytes'),
                                                ('.meta.json','meta_oid','meta_bytes')):
                    path=ROOT+slug+suffix
                    expected[b][path]=('100644','blob',row[field],row[sizefield])
        # Closed-world inventory: no hidden, orphaned, duplicate-case, or partial
        # article files may ride along in any of the seven contributor branches.
        all_paths=0
        for name in HEADS:
            demand(type(trees[name]) is dict,'invalid branch listing')
            observed=trees[name]
            demand(set(observed)==set(expected[name]),
                   'undeclared/missing article paths '+name+': extra='+
                   ','.join(sorted(set(observed)-set(expected[name])))[:180]+': missing='+
                   ','.join(sorted(set(expected[name])-set(observed)))[:180])
            for path,entry in expected[name].items():
                demand(observed[path]==entry,'branch Git OID/mode/size drift '+name+':'+path)
            all_paths+=len(observed)
        if strict:
            demand(all_paths==142 and len(seen)==35 and len(routes)==35,
                   '35-article directory census mismatch')
        report['summary']={'articles':len(seen),'routes':len(routes),'branches':len(HEADS),
            'closed_world_paths':all_paths,'source_use_relationships':total_uses,
            'ambiguous_origin_relationships':len(report['ambiguous_origins']),
            'release_ready':False}
        report['state']=HOLD
    except (Blocked,KeyError,TypeError,ValueError,AttributeError) as exc:
        report['errors']=[str(exc)[:400]]
        report['source_crosswalk']=[]
        report['ambiguous_origins']=[]
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',default='.')
    ap.add_argument('--report')
    args=ap.parse_args(argv); root=Path(args.repo).resolve()
    try:
        raw=(root/MANIFEST_PATH).read_bytes()
        demand(oid(raw)==MANIFEST_OID,'independent frozen manifest identity drift')
        manifest=strict_json(raw)
        trees={name:branch_listing(root,sha) for name,sha in HEADS.items()}
        result=check(manifest,trees,read_article_metadata(root,manifest),
                     read_source_registers(root))
    except (Blocked,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,
            UnicodeError,ValueError,KeyError) as exc:
        result={'schema':REPORT_SCHEMA,'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(exc)[:400]]}
    output=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if args.report:
        Path(args.report).write_text(output,encoding='utf8')
    else:
        print(output,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
