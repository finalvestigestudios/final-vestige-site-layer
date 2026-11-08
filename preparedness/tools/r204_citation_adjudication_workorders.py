#!/usr/bin/env python3
"""R204: lossless review workorders for original all-35 citation/source-use gaps.

Reads only immutable original Claude branch Git objects after R202 custody. Records
claim context and origin for human review; NEVER authorizes publication/safety/QD.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
PARENT = HERE / 'r203_full_slate_citation_body_gate.py'
PARENT_OID = 'c89a9b0fda60b8f3eca0b9d2273161db92e31159'
SCHEMA = 'fv-preparedness-r204-original-citation-adjudication-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
EXPECTED = {('homemade-water-filters', 'cdc-find-clean-water'): 2,
            ('preparedness-real-households', 'start-ready-plan'): 1}
TAG = re.compile(r'<[^>]+>')
WS = re.compile(r'\s+')

class Blocked(ValueError):
    pass

def demand(ok, why):
    if not ok:
        raise Blocked(why)

def oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def parent():
    raw=PARENT.read_bytes()
    demand(oid(raw)==PARENT_OID, 'R203 parser/parent identity drift')
    spec=importlib.util.spec_from_file_location('r204_r203_parent', PARENT)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def context(text, pos, width=360):
    # Context is informational only; all decisions require primary-source review.
    start=max(0,pos-width); end=min(len(text),pos+width)
    snippet=html.unescape(TAG.sub(' ',text[start:end]))
    return WS.sub(' ',snippet).strip()

def check(manifest, bodies, metadata, sources, structural, *, strict=True):
    result={'schema': SCHEMA, 'issue':136,'conversion_issue':820,
            'state':INVALID,'publication_authorized':False,
            'independent_qd_pass':False,'medical_safety_verified':False,
            'human_source_approved':False,'paid_offer_verified':False,
            'verified_orders':None,'net_revenue':None,
            'errors':[],'workorders':[],'summary':{}}
    try:
        demand(isinstance(structural,dict) and structural.get('state')==HOLD
               and not structural.get('errors')
               and structural.get('publication_authorized') is False
               and structural.get('independent_qd_pass') is False,
               'R202 prerequisite not structurally held')
        demand(isinstance(manifest,dict) and manifest.get('issue')==136
               and manifest.get('conversion_issue')==820
               and manifest.get('state')==HOLD
               and manifest.get('publication_authorized') is False
               and manifest.get('independent_qd_pass') is False,
               'frozen manifest/governance invalid')
        rows=manifest.get('articles')
        demand(isinstance(rows,list) and len(rows)==35,'original 35-article roster missing')
        slugs=[r['slug'] for r in rows]
        demand(len(set(slugs))==35 and isinstance(bodies,dict)
               and isinstance(metadata,dict) and set(bodies)==set(slugs)
               and set(metadata)==set(slugs), 'closed-world original body/metadata census failed')
        demand(isinstance(sources,dict) and 'global' in sources,
               'original source registers missing')
        registry={}
        for origin,record in sources.items():
            items=record.get('sources') if isinstance(record,dict) else None
            demand(isinstance(items,list) and all(isinstance(x,dict) for x in items),
                   'malformed source registry '+origin)
            entries={x.get('id'):x for x in items}
            demand(len(entries)==len(items) and all(isinstance(k,str) for k in entries),
                   'duplicate/invalid source id '+origin)
            registry[origin]=entries
        observed={}
        total_cites=0
        for row in rows:
            slug=row['slug']; cluster=row['source_cluster']; raw=bodies[slug]
            demand(isinstance(raw,bytes) and oid(raw)==row['body_oid']
                   and len(raw)==row['body_bytes'], 'unfrozen article body '+slug)
            demand(row.get('branch_sha')==manifest['branch_heads'].get(cluster)
                   and cluster in registry, 'source cluster/branch drift '+slug)
            meta=metadata[slug]
            demand(isinstance(meta,dict) and meta.get('slug')==slug
                   and isinstance(meta.get('source_use'),dict),
                   'unfrozen source-use document '+slug)
            text=raw.decode('utf-8','strict')
            tokens=list(re.finditer(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}',text))
            demand(tokens, 'citation-free source body '+slug)
            total_cites += len(tokens)
            for token in tokens:
                ident=token.group(1)
                if ident in meta['source_use']:
                    continue
                key=(slug,ident)
                observed[key]=observed.get(key,0)+1
                eligible=[o for o in ('global',cluster) if ident in registry[o]]
                demand(eligible,'missing-source-use citation has no eligible origin '+slug+':'+ident)
                entries=[registry[o][ident] for o in eligible]
                demand(all(s.get('human_link_check') is False for s in entries),
                       'historically unreviewed source unexpectedly changed '+slug+':'+ident)
                byte_offset=len(text[:token.start()].encode('utf-8'))
                result['workorders'].append({
                    'article':slug,'article_number':row['n'],
                    'article_git_oid':row['body_oid'],
                    'source_id':ident,'citation_byte_offset':byte_offset,
                    'claim_context':context(text,token.start()),
                    'eligible_source_origins':eligible,
                    'source_records':[{'origin':o,'url':registry[o][ident].get('url'),
                                       'publisher':registry[o][ident].get('publisher'),
                                       'human_link_check':False} for o in eligible],
                    'required_reviews':['claim_to_source_fit','human_link_check',
                                        'hazard_specific_safety_review','independent_QD'],
                    'decision':'UNREVIEWED_HARD_HOLD'})
        demand(observed==EXPECTED, 'unexpected missing-source-use census '+str(observed)) if strict else None
        demand(len(result['workorders'])==sum(observed.values()),'workorder loss')
        result['summary']={'original_articles':35,'citation_occurrences':total_cites,
                'missing_source_use_occurrences':len(result['workorders']),
                'missing_source_use_pairs':len(observed),
                'originals_modified':0,'automatically_approved_sources':0,
                'human_review_pending':True,'revenue_confirmed':False}
        result['state']=HOLD
    except (Blocked,KeyError,TypeError,ValueError,UnicodeError,AttributeError) as exc:
        result['errors']=[str(exc)[:500]]
        result['workorders']=[]
        result['summary']={}
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',default='.')
    parser.add_argument('--report')
    args=parser.parse_args(argv)
    try:
        bridge=parent()
        gate=bridge.load_r202()
        repo=Path(args.repo).resolve()
        raw=(repo/bridge.MANIFEST_PATH).read_bytes()
        demand(gate.oid(raw)==gate.MANIFEST_OID,'R200 roster blob mismatch')
        manifest=gate.strict_json(raw)
        trees={name:gate.branch_listing(repo,sha) for name,sha in gate.HEADS.items()}
        metas=gate.read_article_metadata(repo,manifest)
        sources=gate.read_source_registers(repo)
        structural=gate.check(manifest,trees,metas,sources)
        demand(structural['state']==HOLD and not structural.get('errors'),
               'R202 preflight not structurally held')
        result=check(manifest,bridge.read_bodies(repo,manifest,gate),metas,sources,structural)
    except (Blocked,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,
            ValueError,KeyError,ImportError) as exc:
        result={'schema':SCHEMA,'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(exc)[:500]],'workorders':[]}
    rendered=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if args.report:
        Path(args.report).write_text(rendered,encoding='utf-8')
    else:
        print(rendered,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
