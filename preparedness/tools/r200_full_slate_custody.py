#!/usr/bin/env python3
"""R200: immutable seven-cluster / 35-article source, route, citation, depth custody.

This is an offline evidence gate, NOT a safety, QD, merchant or publishing approval.
Complete Git object availability is required; a missing blob is a hard failure.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1'
REPORT_SCHEMA = 'fv-preparedness-r200-full-slate-structural-review-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
MANIFEST_SHA = '5822f9dfde21d1f3bdfc26658769d852c639438c'
TAXONOMY_SHA = '15c547bb3018ac182b12a51036389cfa39a59168'
HEADS = {
 'start':'2122d856fce9f64887c16df3d52e64be9f59a55b',
 'shelter':'5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
 'food':'f911ff7a655de8d81535ea86ec3d65a49ee76648',
 'health':'d5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
 'hist-field':'4e5caf812727953aa45e3bda2d382f2c67b6a09c',
 'hist-food':'67e116e536c7410bed30f8f3b1bb8c166f3c223d',
 'hist-home':'7504a5f099594d635e3dd7332a33a2e1346c43a2',
}
HISTORICAL_OBSERVED = {
 'navigation-before-gps':('49beb68339a6b85b07d686c0cfb9fe1d88b8de4f','40c83419760bc7bd0c4c574304e65b773b4a8423'),
 'pioneer-supply-chains-failed':('3643c50b43ca7ba6c1d9bc439e7c78730503b80f','8789c77dcc2be717f09ce0fbd340a04319aaf223'),
 'pemmican-and-dried-meats':('1febc8929f8b90c81a3fcef1e46a2811778b7e06','c19f68f2ac0988a8d0959e2d05b8ace8f9511348'),
 'pioneer-travel-rations':('a658481d828dc4c5ba85f296adbfbee0514f0611','521e56a3f18d8b211920529a88a3c3b86eb332d7'),
 'pickling-fermentation-old-recipes':('1869e37626b7463da45763d60202bd5ac0bd7700','da97f42fcabbd05dc513d26c6af289bbeb8816f3'),
 'root-cellars-cool-storage':('7f375c32d74f2828b4912f5692abc44483e4629a','c3b7425711c3953c2d6cac9eb2aabe21a6717285'),
 'sanitation-before-germ-theory':('02090fc1b773fd79f08a7ba754b6125844c37eab','3294cd9fcf59496c9ece9342e67b0d57d2ed5523'),
}
COLLISIONS = frozenset(('loc-prairie-traveler','loc-pioneer-diaries','nchfp-jerky','nchfp-home',
                       'nps-lewis-clark-salt','nps-salt-works','nchfp-historical-origins'))
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9]+(?:-[a-z0-9]+)*)\|([^{}|]+)\}\}')
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")
HEX = re.compile(r'[0-9a-f]{40}\Z')

class CustodyError(ValueError): pass

def demand(ok, why):
    if not ok: raise CustodyError(why)

def git_oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()

def strict_json(raw):
    def unique(items):
        d={}
        for k,v in items:
            demand(k not in d, 'duplicate JSON key: '+k)
            d[k]=v
        return d
    def bad_constant(x): raise CustodyError('illegal JSON constant: '+x)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=bad_constant)

def check(manifest, taxonomy_bytes, read_blob, *, strict=True):
    report={'schema':REPORT_SCHEMA,'issue':136,'conversion_issue':820,'state':INVALID,
            'publication_authorized':False,'independent_qd_pass':False,
            'human_source_approved':False,'medical_safety_verified':False,
            'merchant_offer_verified':False,'verified_paid_orders':None,
            'realized_net_revenue':None,'articles':[],'review_required':[],
            'summary':{},'errors':[]}
    try:
        demand(type(manifest) is dict and manifest.get('schema')==SCHEMA and
               manifest.get('issue')==136 and manifest.get('conversion_issue')==820,
               'manifest identity or governance mismatch')
        demand(manifest.get('state')==HOLD,'manifest must remain a hard hold')
        for flag in ('publication_authorized','independent_qd_pass','human_source_approved',
                     'medical_safety_verified','merchant_offer_verified'):
            demand(manifest.get(flag) is False,'unsupported approval flag: '+flag)
        demand(manifest.get('verified_paid_orders') is None and
               manifest.get('realized_net_revenue') is None,'unsupported sales assertion')
        demand(manifest.get('branch_heads')==HEADS,'source branch-head drift')
        demand(manifest.get('taxonomy_blob_sha1')==TAXONOMY_SHA,'taxonomy identity drift')
        demand(type(taxonomy_bytes) is bytes and git_oid(taxonomy_bytes)==TAXONOMY_SHA,
               'original taxonomy bytes unavailable or substituted')
        taxonomy=strict_json(taxonomy_bytes)
        slate=taxonomy.get('slate')
        demand(type(slate) is list and len(slate)>0,'missing slate')
        slate_by_slug={}
        for i,s in enumerate(slate,1):
            demand(type(s) is dict and s.get('n')==i and type(s.get('slug')) is str
                   and s['slug'] not in slate_by_slug,'slate numbering/slug drift')
            slate_by_slug[s['slug']]=s
        rows=manifest.get('articles')
        demand(type(rows) is list and len(rows)==len(slate),'article roster incomplete')
        demand(manifest.get('artifact_count')==len(rows) and
               manifest.get('export_target_count_with_six_tools')==len(rows)+6,
               'export census mismatch')
        if strict: demand(len(rows)==35, 'the 35-article slate is incomplete')
        routes=set();slugs=set();counts=Counter();source_uses=Counter()
        min_words=550 if strict else 1
        for n,row in enumerate(rows,1):
            demand(type(row) is dict and row.get('n')==n,'article ordering drift')
            slug=row.get('slug')
            demand(type(slug) is str and slug in slate_by_slug and slug not in slugs,
                   'article missing, duplicated or outside slate')
            slugs.add(slug)
            s=slate_by_slug[slug]
            demand(row.get('track')==s.get('track') and row.get('section')==s.get('section'),
                   'section or track mismatch: '+slug)
            route='/preparedness/'+s['section']+'/'+slug+'/'
            demand(row.get('route')==route and route not in routes,'duplicate or wrong canonical route: '+slug)
            routes.add(route)
            owner=row.get('source_cluster')
            demand(owner in HEADS and row.get('branch_sha')==HEADS[owner],
                   'unreviewed source branch: '+slug)
            witnesses=row.get('also_in')
            demand(type(witnesses) is list and len(witnesses)>0 and owner==witnesses[0] and
                   len(witnesses)==len(set(witnesses)) and all(x in HEADS for x in witnesses),
                   'invalid overlapping branch provenance: '+slug)
            for field in ('body_oid','meta_oid'):
                demand(type(row.get(field)) is str and HEX.fullmatch(row[field]),
                       'invalid blob identity: '+slug+'/'+field)
            if strict and slug in HISTORICAL_OBSERVED:
                demand((row['body_oid'],row['meta_oid'])==HISTORICAL_OBSERVED[slug],
                       'R195 observed historical object disagree: '+slug)
            body=read_blob(row['body_oid']);meta_raw=read_blob(row['meta_oid'])
            demand(type(body) is bytes and type(meta_raw) is bytes and
                   git_oid(body)==row['body_oid'] and git_oid(meta_raw)==row['meta_oid'],
                   'missing/substituted Git blob: '+slug)
            demand(len(body)==row.get('body_bytes') and len(meta_raw)==row.get('meta_bytes'),
                   'size and Git custody disagree: '+slug)
            meta=strict_json(meta_raw)
            demand(meta.get('n')==n and meta.get('slug')==slug and
                   meta.get('track')==s['track'] and meta.get('section')==s['section'],
                   'author metadata not aligned with slate: '+slug)
            demand(type(meta.get('status')) is dict and meta['status'].get('publish')=='draft',
                   'non-draft publication state: '+slug)
            safety=meta.get('safety_review')
            demand(type(safety) is dict and safety.get('state') in ('pending','approved'),
                   'missing original safety state: '+slug)
            use=meta.get('source_use')
            demand(type(use) is dict and len(use)>0 and all(type(v) is str and v.strip()
                   for v in use.values()),'missing source-use explanations: '+slug)
            body_text=body.decode('utf-8')
            citations=list(CITE.finditer(body_text))
            demand(len(citations)>0 and body_text.count('{{cite:')==len(citations),
                   'missing/malformed author citations: '+slug)
            missing={x.group(1) for x in citations}-set(use)
            demand(not missing, 'cited IDs lack explained source use: '+slug+':'+','.join(sorted(missing)))
            links=list(LINK.finditer(body_text))
            demand(body_text.count('{{link:')==len(links),'malformed internal link tokens: '+slug)
            demand(all(m.group(1) in slate_by_slug for m in links),
                   'internal article links escape 35-slate: '+slug)
            visible=html.unescape(re.sub(r'<[^>]*>', ' ',body_text))
            visible=re.sub(r'\{\{[^{}]*\}\}',' ',visible)
            words=len(WORD.findall(visible))
            demand(words>=min_words,'reading depth below minimum: '+slug)
            counts['citations']+=len(citations);counts['body_bytes']+=len(body)
            counts['words_approx']+=words;counts['links']+=len(links)
            source_uses.update(COLLISIONS.intersection(set(use)))
            report['articles'].append({'n':n,'slug':slug,'route':route,
                  'body_oid':row['body_oid'],'meta_oid':row['meta_oid'],
                  'words_approx':words,'citation_occurrences':len(citations),
                  'source_use_count':len(use),'source_conflicts':sorted(set(use)&COLLISIONS),
                  'safety_review_state_as_authored':safety['state'],
                  'human_claim_review':'PENDING','publication_authorized':False})
        demand(slugs==set(slate_by_slug),'35-article slate lost content')
        report['review_required']=[{'source_id':k,'article_count':v,'human_review':'PENDING'}
                                   for k,v in sorted(source_uses.items())]
        report['summary']=dict(counts)|{'articles':len(rows),'canonical_routes':len(routes),
                                      'distinct_colliding_source_ids':len(source_uses)}
        report['state']=HOLD
    except (CustodyError,KeyError,TypeError,AttributeError,ValueError,UnicodeError,OSError) as exc:
        report['errors'].append(str(exc)[:420]);report['articles']=[]
        report['review_required']=[];report['summary']={}
    return report

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='.')
    p.add_argument('--report')
    a=p.parse_args(argv)
    root=Path(a.repo).resolve()
    try:
        manifest_bytes=(root/'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json').read_bytes()
        demand(git_oid(manifest_bytes)==MANIFEST_SHA,'reviewed manifest Git identity has changed')
        taxonomy_bytes=(root/'preparedness/taxonomy.json').read_bytes()
        def read_blob(oid):
            p=subprocess.run(['git','cat-file','blob',oid],cwd=root,timeout=15,check=True,
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            return p.stdout
        report=check(strict_json(manifest_bytes),taxonomy_bytes,read_blob)
    except (CustodyError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        report={'schema':REPORT_SCHEMA,'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(exc)[:420]]}
    serialized=json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if a.report: Path(a.report).write_text(serialized,encoding='utf-8')
    else:print(serialized,end='')
    return 2 if report['state']==HOLD else 3

if __name__=='__main__': raise SystemExit(main())
