#!/usr/bin/env python3
"""R199: authenticate and bridge historical body citations to scoped source-origin custody.

Read-only review workorders; NEVER a safety, release, merchant, or QD approval.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r199-citation-origin-bridge-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
R198_BLOB = '77ca95b4140721a30370b7e851522bc0c85ef2aa'
R195_BLOB = 'e2dd19a5af2783817562a4928c82a9a1929ab83c'
DOCKET = '05d393013a952d9d2c92a6e1d9759ca53579ae8b'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
TOTALS = {'frozen': 315, 'observed': 334}

class BridgeError(ValueError):
    pass

def demand(ok, why):
    if not ok: raise BridgeError(why)

def git_oid(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def pinned_module(repo, relative, expected, alias):
    path = (Path(repo).resolve() / relative).resolve()
    demand(path.is_file() and path.is_relative_to(Path(repo).resolve()), 'missing/outside pinned module')
    demand(git_oid(path.read_bytes()) == expected, 'producer identity drift: ' + relative)
    spec = importlib.util.spec_from_file_location(alias, path)
    demand(spec is not None and spec.loader is not None, 'unimportable producer')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def bridge(scope, impact, read_blob, *, pins, strict=True):
    report = {'schema': SCHEMA, 'issue': 136, 'coordination_issue': 820,
              'state': INVALID, 'publication_authorized': False,
              'independent_qd_pass': False, 'human_source_approved': False,
              'medical_safety_verified': False, 'merchant_offer_verified': False,
              'verified_paid_orders': None, 'realized_net_revenue': None,
              'citation_occurrences': {}, 'source_origin_workorders': [],
              'article_versions': [], 'errors': []}
    try:
        for name, packet, schema in (
            ('R198', scope, 'fv-preparedness-r198-source-scope-custody-v1'),
            ('R195', impact, 'fv-preparedness-r195-claim-impact-review-v1')):
            demand(type(packet) is dict and packet.get('schema') == schema
                   and packet.get('state') == HOLD, name + ' missing hard-hold evidence')
            for flag in ('publication_authorized','independent_qd_pass',
                         'medical_safety_verified','merchant_offer_verified'):
                demand(packet.get(flag) is False, name + ' false approval: ' + flag)
            demand(packet.get('verified_paid_orders') is None
                   and packet.get('realized_net_revenue') is None,
                   name + ' invented sales or revenue')
        demand(scope.get('errors') == [] and impact.get('errors') == [], 'upstream errors')
        demand(type(pins) in (tuple,list) and len(pins) > 0, 'no immutable article roster')
        origins = scope.get('origin_scope_workorders')
        workorders = impact.get('workorders')
        demand(type(origins) is list and type(workorders) is list, 'missing upstream evidence')
        expected = {(p[0],p[1],v) for p in pins for v in TOTALS}
        demand(len(origins) == sum(x.get('source_uses',0) for x in scope.get('summary',{}).values()),
               'scope source-use census drift')
        by_version = {}
        for row in origins:
            demand(type(row) is dict, 'malformed origin row')
            key = (row.get('cluster'),row.get('slug'),row.get('version'))
            demand(key in expected and row.get('human_review') == 'PENDING',
                   'unexpected or approved source-origin row')
            sid = row.get('source_id')
            origins_list = row.get('all_original_origins')
            eligible = row.get('eligible_origins')
            demand(type(sid) is str and ID.fullmatch(sid), 'invalid source identifier')
            demand(type(origins_list) is list and origins_list == sorted(set(origins_list))
                   and type(eligible) is list and eligible == sorted(set(eligible))
                   and len(eligible) > 0 and set(eligible) <= {'base', key[0]},
                   'invalid or foreign-only source origin')
            demand(set(eligible) == set(origins_list) & {'base',key[0]},
                   'fabricated eligible source origin')
            demand(row.get('automatic_origin_selection') is False, 'source origin silently selected')
            k = (*key, sid)
            demand(k not in by_version, 'duplicate article-version/source identifier')
            by_version[k] = row
        impact_index = {}
        for row in workorders:
            demand(type(row) is dict, 'bad impact workorder')
            key=(row.get('cluster'),row.get('slug'))
            demand(key not in impact_index and row.get('manual_source_claim_review') == 'PENDING',
                   'duplicate or falsely approved impact workorder')
            impact_index[key]=row
        demand(set(impact_index) == {(p[0],p[1]) for p in pins}, 'changed impact article roster')
        counts={v:0 for v in TOTALS}
        matched=set()
        for p in pins:
            demand(len(p)==8, 'malformed article identity pin')
            group, slug = p[:2]
            impact_row=impact_index[(group,slug)]
            for version, offset in (('frozen',2),('observed',5)):
                body_oid, meta_oid, expected_count = p[offset:offset+3]
                demand(impact_row.get(version+'_blob_sha1') == body_oid,
                       'impact-body identity disagreement: '+slug)
                body, meta = read_blob(body_oid), read_blob(meta_oid)
                demand(type(body) is bytes and type(meta) is bytes and
                       git_oid(body)==body_oid and git_oid(meta)==meta_oid,
                       'missing or substituted original Git blob: '+slug)
                payload=json.loads(meta.decode('utf-8'))
                demand(type(payload) is dict and payload.get('slug') == slug
                       and payload.get('status',{}).get('publish') == 'draft'
                       and type(payload.get('source_use')) is dict,
                       'article metadata/publication drift: '+slug)
                text=body.decode('utf-8')
                hits=list(CITE.finditer(text))
                demand(text.count('{{cite:') == len(hits) and len(hits) == expected_count,
                       'malformed or lost citation occurrences: '+slug)
                ids={sid for (g,s,v,sid) in by_version if (g,s,v)==(group,slug,version)}
                demand(ids == set(payload['source_use']), 'source-use/origin bridge mismatch: '+slug)
                for index, match in enumerate(hits,1):
                    sid=match.group(1)
                    demand(sid in ids and type(payload['source_use'][sid]) is str
                           and payload['source_use'][sid].strip(),
                           'citation has no scoped source use: '+slug+'/'+sid)
                    row=by_version[(group,slug,version,sid)]
                    context=' '.join(text[max(0,match.start()-110):match.end()+110].split())
                    report['source_origin_workorders'].append({
                        'cluster':group,'slug':slug,'version':version,
                        'ordinal':index,'source_id':sid,
                        'line':text.count('\n',0,match.start())+1,
                        'context_sha256':hashlib.sha256(context.encode()).hexdigest(),
                        'eligible_origins':row['eligible_origins'],
                        'foreign_alternatives':row.get('foreign_alternatives',[]),
                        'requires_origin_adjudication':len(row['all_original_origins'])>1,
                        'human_claim_check':'PENDING', 'automatic_alias':False})
                matched.update((group,slug,version,sid) for sid in ids)
                seq='\n'.join(m.group(1) for m in hits)
                report['article_versions'].append({'cluster':group,'slug':slug,
                    'version':version,'body_git_blob':body_oid,
                    'meta_git_blob':meta_oid,'citation_occurrences':len(hits),
                    'citation_sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),
                    'human_review':'PENDING'})
                counts[version]+=len(hits)
        demand(matched==set(by_version), 'orphan source-origin workorders')
        if strict:
            demand(len(pins)==7 and counts==TOTALS, 'historical body citation census drift')
            demand(impact.get('frozen_citations')==TOTALS['frozen'] and
                   impact.get('observed_citations')==TOTALS['observed'],
                   'upstream impact citation totals disagree')
        report['citation_occurrences']=counts
        report['state']=HOLD
    except (BridgeError,UnicodeError,TypeError,ValueError,KeyError,AttributeError,OSError) as exc:
        report['errors'].append(str(exc)[:400])
        report['source_origin_workorders']=[]
        report['article_versions']=[]
    return report

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='.')
    p.add_argument('--report')
    args=p.parse_args(argv)
    repo=Path(args.repo).resolve()
    try:
        r198=pinned_module(repo,'preparedness/tools/r198_source_scope_gate.py',R198_BLOB,'fv_r199_r198')
        r195=pinned_module(repo,'preparedness/tools/r195_claim_impact_preflight.py',R195_BLOB,'fv_r199_r195')
        def read_blob(sha):
            return subprocess.run(['git','cat-file','blob',sha],cwd=repo,check=True,
                                  timeout=15,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
        r197=r198.load_pinned_r197(repo)
        scope=r198.verify(r197.audit(read_blob))
        impact=r195.evaluate(read_blob(DOCKET),read_blob)
        result=bridge(scope,impact,read_blob,pins=r195.PINS)
    except (OSError,BridgeError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        result={'schema':SCHEMA,'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'errors':[str(exc)[:400]]}
    output=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
    if args.report: Path(args.report).write_text(output,encoding='utf-8')
    else: print(output,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':raise SystemExit(main())
