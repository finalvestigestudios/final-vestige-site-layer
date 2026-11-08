#!/usr/bin/env python3
"""R205: fail-closed, immutable occurrence receipts and quarantined human-review notes.

Consumes R204's frozen original-article workorders, not live CMS content.
Never grants source verification, medical/safety/QD approval or commercial release.
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
PARENT = HERE / 'r204_citation_adjudication_workorders.py'
PARENT_OID = '68ef1635c0f5470af8a15cd84b434607ff4b7cb2'
SCHEMA = 'fv-preparedness-r205-immutable-occurrence-review-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
EXPECTED = {('homemade-water-filters', 'cdc-find-clean-water'): 2,
            ('preparedness-real-households', 'start-ready-plan'): 1}
CITE = re.compile(rb'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
ALIAS = re.compile(r'[A-Za-z0-9][A-Za-z0-9._ -]{0,79}\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')
NOTE_FIELDS = frozenset(('receipt_id','reviewer_alias','review_note','source_url_checked','decision'))
DECISIONS = frozenset(('NO_DECISION','NEEDS_REVISION','NEEDS_SECOND_REVIEW'))

class Blocked(ValueError):
    pass

def demand(ok, reason):
    if not ok:
        raise Blocked(reason)

def oid(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def pinned_parent():
    data = PARENT.read_bytes()
    demand(oid(data)==PARENT_OID,'R204 parent Git object drift')
    spec = importlib.util.spec_from_file_location('r205_r204_parent',PARENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def clean_context(raw, position, span=420):
    excerpt = raw[max(0,position-span):min(len(raw),position+span)].decode('utf8','replace')
    excerpt = html.unescape(re.sub(r'<[^>]*>',' ',excerpt))
    excerpt = re.sub(r'[\x00-\x1f\x7f]+',' ',excerpt)
    return re.sub(r'\s+',' ',excerpt).strip()[:650]

def build_packet(manifest, bodies, metadata, sources, structural, adjudication,
                 notes=(), *, authentic=True):
    packet={'schema':SCHEMA,'issue':136,'conversion_issue':820,
            'state':INVALID,'publication_authorized':False,
            'human_source_approved':False,'independent_qd_pass':False,
            'medical_safety_verified':False,'paid_offer_verified':False,
            'verified_paid_orders':None,'realized_net_revenue':None,
            'summary':{},'receipts':[],'quarantined_notes':[],'errors':[]}
    try:
        demand(type(manifest) is dict and manifest.get('issue')==136
               and manifest.get('conversion_issue')==820
               and manifest.get('state')==HOLD
               and manifest.get('publication_authorized') is False
               and manifest.get('independent_qd_pass') is False,
               'source custody manifest not held')
        rows=manifest.get('articles')
        demand(type(rows) is list and len(rows)==35,'35-article roster required')
        slugs=[r['slug'] for r in rows]
        demand(len(set(slugs))==35 and set(bodies)==set(slugs)
               and set(metadata)==set(slugs),'original closed-world body/metadata census failed')
        demand(type(structural) is dict and structural.get('state')==HOLD
               and structural.get('errors')==[]
               and structural.get('publication_authorized') is False
               and structural.get('independent_qd_pass') is False,
               'R202 structural prerequisite unavailable')
        demand(type(adjudication) is dict and adjudication.get('schema')==
               'fv-preparedness-r204-original-citation-adjudication-v1'
               and adjudication.get('state')==HOLD
               and adjudication.get('errors')==[]
               and adjudication.get('publication_authorized') is False
               and adjudication.get('independent_qd_pass') is False
               and adjudication.get('human_source_approved') is False
               and adjudication.get('medical_safety_verified') is False
               and adjudication.get('paid_offer_verified') is False
               and adjudication.get('verified_orders') is None
               and adjudication.get('net_revenue') is None,
               'R204 review gate invalid or unsupported approval')
        demand(type(sources) is dict and 'global' in sources,
               'frozen source registers missing')
        registry={}
        for origin, record in sources.items():
            items=record.get('sources') if type(record) is dict else None
            demand(type(items) is list and all(type(s) is dict for s in items),
                   'invalid source register: '+str(origin))
            index={s.get('id'):s for s in items}
            demand(len(index)==len(items) and all(type(i) is str for i in index),
                   'duplicate source identifiers: '+str(origin))
            registry[origin]=index
        incoming=adjudication.get('workorders')
        demand(type(incoming) is list,'missing R204 workorders')
        observed={};all_missing={};cite_total=0
        for row in rows:
            slug=row['slug']; raw=bodies[slug]; owner=row['source_cluster']
            demand(type(raw) is bytes and len(raw)==row['body_bytes']
                   and oid(raw)==row['body_oid'],'original body identity drift: '+slug)
            demand(row.get('branch_sha')==manifest['branch_heads'].get(owner),
                   'owner branch drift: '+slug)
            meta=metadata[slug]
            demand(type(meta) is dict and meta.get('slug')==slug
                   and type(meta.get('source_use')) is dict,
                   'metadata source-use unavailable: '+slug)
            tokens=list(CITE.finditer(raw));cite_total+=len(tokens)
            for token in tokens:
                ident=token.group(1).decode('ascii')
                if ident not in meta['source_use']:
                    key=(slug,ident)
                    all_missing.setdefault(key,[]).append(token.start())
                    demand(owner in registry and ident in registry.get('global',{}) or
                           ident in registry.get(owner,{}),
                           'missing citation has no eligible source: '+slug+':'+ident)
        demand(all_missing=={k:all_missing[k] for k in EXPECTED} and
               {k:len(v) for k,v in all_missing.items()}==EXPECTED,
               'new/missing original citation exceptions')
        demand(len(incoming)==sum(EXPECTED.values()),
               'workorder loss or overcount')
        summary=adjudication.get('summary')
        demand(type(summary) is dict and summary.get('original_articles')==35
               and summary.get('citation_occurrences')==cite_total
               and summary.get('missing_source_use_occurrences')==len(incoming)
               and summary.get('missing_source_use_pairs')==len(EXPECTED),
               'R204 citation census mismatch')
        if authentic:
            demand(cite_total==1971,'original 1,971-citation corpus drift')
        seen=set()
        for item in incoming:
            demand(type(item) is dict and item.get('decision')=='UNREVIEWED_HARD_HOLD'
                   and item.get('source_records') and item.get('required_reviews')==
                   ['claim_to_source_fit','human_link_check','hazard_specific_safety_review','independent_QD'],
                   'R204 workorder altered')
            slug=item.get('article'); ident=item.get('source_id');pos=item.get('citation_byte_offset')
            demand(type(pos) is int and pos>=0 and type(slug) is str and type(ident) is str
                   and (slug,ident) in EXPECTED,'unexpected workorder identity')
            demand(pos in all_missing[slug,ident] and (slug,ident,pos) not in seen,
                   'wrong/duplicate citation byte offset')
            seen.add((slug,ident,pos))
            row=next(r for r in rows if r['slug']==slug)
            raw=bodies[slug]
            token=b'{{cite:'+ident.encode('ascii')+b'}}'
            demand(raw[pos:pos+len(token)]==token
                   and item.get('article_git_oid')==row['body_oid']
                   and item.get('article_number')==row['n'],
                   'article identity/offset not backed by source bytes')
            owner=row['source_cluster']
            eligible=[o for o in ('global',owner) if ident in registry[o]]
            demand(eligible==item.get('eligible_source_origins'),
                   'eligible origins changed')
            source_records=[{'origin':o,'url':registry[o][ident].get('url'),
                             'publisher':registry[o][ident].get('publisher'),
                             'human_link_check':False} for o in eligible]
            demand(source_records==item.get('source_records') and
                   all(registry[o][ident].get('human_link_check') is False for o in eligible),
                   'source record drift or fake review')
            span=raw[max(0,pos-420):min(len(raw),pos+420)]
            digest=hashlib.sha256(span).hexdigest()
            ident_bytes='\0'.join((slug,row['body_oid'],str(pos),ident,digest)).encode()
            receipt_id=hashlib.sha256(ident_bytes).hexdigest()
            packet['receipts'].append({
                'receipt_id':receipt_id,'article':slug,'article_number':row['n'],
                'source_id':ident,'article_oid':row['body_oid'],
                'citation_byte_offset':pos,'surrounding_bytes_sha256':digest,
                'claim_context_for_review_only':clean_context(raw,pos),
                'eligible_origins':eligible,'source_records':source_records,
                'human_review_state':'UNVERIFIED_HARD_HOLD',
                'required_reviews':item['required_reviews']})
        demand(seen=={(s,i,p) for (s,i),offsets in all_missing.items() for p in offsets},
               'missing position receipts')
        packet['receipts'].sort(key=lambda r:(r['article_number'],r['citation_byte_offset']))
        ids={r['receipt_id'] for r in packet['receipts']}
        by_id={r['receipt_id']:r for r in packet['receipts']}
        demand(len(ids)==len(incoming),'duplicate receipt IDs')
        demand(type(notes) in (tuple,list),'review notes must be a list')
        noted=set()
        for note in notes:
            demand(type(note) is dict and set(note)==NOTE_FIELDS,'review note fields forbidden/missing')
            rid=note['receipt_id'];alias=note['reviewer_alias'];body=note['review_note']
            url=note['source_url_checked'];decision=note['decision']
            demand(type(rid) is str and HASH.fullmatch(rid) and rid in ids and rid not in noted,
                   'stale/duplicate review note receipt')
            demand(type(alias) is str and ALIAS.fullmatch(alias) is not None,
                   'invalid reviewer alias')
            demand(type(body) is str and 16<=len(body)<=3000 and
                   not re.search(r'[\x00-\x08\x0b-\x1f]',body),
                   'review note missing/invalid')
            demand(type(url) is str and len(url)<2048 and
                   (url=='' or (url.startswith('https://') and url in
                    [s.get('url') for s in by_id[rid]['source_records']])) and decision in DECISIONS,
                   'review note must stay non-approving')
            noted.add(rid)
            packet['quarantined_notes'].append({**note,
                'status':'UNVERIFIED_DRAFT_NOTE_NOT_SOURCE_APPROVAL'})
        packet['quarantined_notes'].sort(key=lambda x:x['receipt_id'])
        packet['summary']={'articles':35,'original_citations':cite_total,
          'missing_source_use_occurrences':len(incoming),
          'immutable_occurrence_receipts':len(ids),
          'quarantined_notes':len(packet['quarantined_notes']),
          'originals_modified':0,'automatically_approved_sources':0,
          'independent_safety_and_qd_pending':True,
          'revenue_per_1000_qualified_sessions':None}
        packet['state']=HOLD
    except (Blocked,KeyError,ValueError,TypeError,UnicodeError,AttributeError) as exc:
        packet['errors']=[str(exc)[:400]]
        packet['receipts']=[];packet['quarantined_notes']=[];packet['summary']={}
    return packet

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',default='.')
    ap.add_argument('--report')
    ap.add_argument('--notes',help='optional draft reviewer notes JSON, never approval')
    args=ap.parse_args(argv)
    try:
        parent=pinned_parent();bridge=parent.parent();gate=bridge.load_r202()
        root=Path(args.repo).resolve()
        raw=(root/bridge.MANIFEST_PATH).read_bytes()
        parent.demand(gate.oid(raw)==gate.MANIFEST_OID,'R200 manifest identity drift')
        manifest=gate.strict_json(raw)
        trees={name:gate.branch_listing(root,sha) for name,sha in gate.HEADS.items()}
        metas=gate.read_article_metadata(root,manifest)
        sources=gate.read_source_registers(root)
        structural=gate.check(manifest,trees,metas,sources)
        bodies=bridge.read_bodies(root,manifest,gate)
        adjudication=parent.check(manifest,bodies,metas,sources,structural)
        notes=gate.strict_json(Path(args.notes).read_bytes()) if args.notes else []
        packet=build_packet(manifest,bodies,metas,sources,structural,adjudication,notes)
    except (Blocked,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,
            KeyError,ValueError,ImportError,UnicodeError,TypeError) as exc:
        packet={'schema':SCHEMA,'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(exc)[:400]],
                'receipts':[],'quarantined_notes':[]}
    output=json.dumps(packet,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if args.report:
        Path(args.report).write_text(output,encoding='utf8')
    else:
        print(output,end='')
    return 2 if packet['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
