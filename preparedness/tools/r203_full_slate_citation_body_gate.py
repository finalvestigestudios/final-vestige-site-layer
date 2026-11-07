#!/usr/bin/env python3
"""R203: immutable all-35 body -> citations, source-use and internal-link custody.

Preparedness Archive #136 ONLY. Exit 2 = structural DRAFT_HARD_HOLD,
exit 3 = INVALID_HARD_HOLD. Neither authorizes independent safety/QD or publication.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent
R202_PATH = BASE / 'r202_directory_and_source_closure.py'
R202_BLOB = '7d05d80277a7571e67ff3bf3228635fb734c767c'
MANIFEST_PATH = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r203-all35-body-citation-link-closure-v1'
MARKER = re.compile(r'\{\{([^{}]*)\}\}')
CITE = re.compile(r'cite:([a-z0-9]+(?:-[a-z0-9]+)*)\Z')
LINK = re.compile(r'link:([a-z0-9]+(?:-[a-z0-9]+)*)\|([^{}|\r\n]+)\Z')

class Blocked(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Blocked(message)

def blob_oid(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()

def fingerprint(data):
    return hashlib.sha256(data).hexdigest()

def load_r202():
    data = R202_PATH.read_bytes()
    require(blob_oid(data)==R202_BLOB, 'R202 validator source identity drift')
    spec = importlib.util.spec_from_file_location('r202_integrity', R202_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def read_bodies(repo, manifest, gate):
    bodies = {}
    for row in manifest['articles']:
        slug = row['slug']
        commit = gate.HEADS[row['source_cluster']]
        path = gate.ROOT + slug + '.body.html'
        raw = gate.git(repo, 'show', commit+':'+path)
        require(blob_oid(raw)==row['body_oid'] and len(raw)==row['body_bytes'],
                'author body identity/length mismatch '+slug)
        bodies[slug] = raw
    return bodies

def check(manifest, bodies, metadata, sources, r202_report, *, strict=True):
    """Returns an auditable HOLD or INVALID; never returns publish eligibility.

    All inputs are untrusted here; the CLI obtains original bytes from Git at
    frozen source commit/paths after authentic R202 manifest/tree validation.
    """
    report = {'schema':SCHEMA, 'issue':136, 'conversion_issue':820,
      'state':INVALID, 'publication_authorized':False, 'independent_qd_pass':False,
      'medical_safety_verified':False, 'human_source_approved':False,
      'merchant_offer_verified':False, 'verified_paid_orders':None,
      'realized_net_revenue':None, 'errors':[], 'summary':{},
      'articles':[], 'citation_ledger':[], 'internal_link_ledger':[],
      'ambiguous_source_origins':[]}
    try:
        require(isinstance(r202_report,dict) and r202_report.get('state')==HOLD and
                not r202_report.get('errors') and
                r202_report.get('independent_qd_pass') is False and
                r202_report.get('publication_authorized') is False,
                'R202 structural custody must pass first')
        require(type(manifest) is dict and manifest.get('issue')==136 and
                manifest.get('conversion_issue')==820 and
                manifest.get('state')==HOLD and
                manifest.get('publication_authorized') is False and
                manifest.get('independent_qd_pass') is False,
                'manifest governance drift')
        rows=manifest.get('articles')
        require(type(rows) is list and (len(rows)==35 if strict else bool(rows)),
                '35-article roster mismatch')
        slugs = [r['slug'] for r in rows]
        require(len(set(slugs))==len(slugs) and
                type(bodies) is dict and set(bodies)==set(slugs) and
                type(metadata) is dict and set(metadata)==set(slugs),
                'body/metadata closed-world census mismatch')
        require(type(sources) is dict and 'global' in sources,
                'source origins unavailable')
        registry = {}
        for origin, doc in sources.items():
            items=doc.get('sources') if type(doc) is dict else None
            require(type(items) is list, 'invalid source register '+origin)
            idlist=[x.get('id') for x in items if type(x) is dict]
            require(len(idlist)==len(items) and len(set(idlist))==len(items),
                    'duplicate/malformed source IDs '+origin)
            registry[origin]=set(idlist)
        counts = Counter()
        route_map={r['slug']:r['route'] for r in rows}
        for row in rows:
            slug=row['slug']; origin=row['source_cluster']
            require(origin in registry and row['branch_sha']==manifest['branch_heads'][origin],
                    'branch/source origin mismatch '+slug)
            raw=bodies[slug]
            require(type(raw) is bytes and len(raw)==row['body_bytes'] and
                    blob_oid(raw)==row['body_oid'], 'body Git blob drift '+slug)
            try:
                content=raw.decode('utf-8', errors='strict')
            except UnicodeDecodeError as exc:
                raise Blocked('body UTF-8 decode failure '+slug) from exc
            meta=metadata[slug]
            require(type(meta) is dict and meta.get('slug')==slug,
                    'metadata/article mismatch '+slug)
            uses=meta.get('source_use')
            require(type(uses) is dict and bool(uses), 'article source-use missing '+slug)
            expected_source_ids=set(uses)
            citation_ids=[]; link_ids=[]
            markers=list(MARKER.finditer(content))
            require(len(markers)>0, 'no template tokens '+slug)
            # Remove parsed markers to catch stray double-braces and malformed forms.
            unparsed=MARKER.sub('',content)
            require('{{' not in unparsed and '}}' not in unparsed,
                    'unparsed or nested template markers '+slug)
            for marker in markers:
                token=marker.group(1)
                cite=CITE.fullmatch(token)
                link=LINK.fullmatch(token)
                require(bool(cite or link), 'unexpected/malformed template marker '+slug)
                byte_offset=len(content[:marker.start()].encode('utf-8'))
                if cite:
                    ident=cite.group(1)
                    require(ident in expected_source_ids,
                            'body citation absent from source_use '+slug+':'+ident)
                    candidates=[o for o in ('global',origin) if ident in registry[o]]
                    require(bool(candidates),
                            'citation source absent from eligible origins '+slug+':'+ident)
                    citation_ids.append(ident)
                    info={'article':slug, 'source_cluster':origin,
                          'ordinal':len(citation_ids), 'byte_offset':byte_offset,
                          'source_id':ident, 'eligible_origins':candidates,
                          'decision':'HUMAN_REVIEW_REQUIRED'}
                    report['citation_ledger'].append(info)
                    if len(candidates)>1:
                        report['ambiguous_source_origins'].append(info)
                else:
                    target,label=link.groups()
                    require(target in route_map,
                            'internal link target not in frozen roster '+slug+':'+target)
                    require(label.strip()==label and label.strip(),
                            'empty or padded link label '+slug)
                    link_ids.append(target)
                    report['internal_link_ledger'].append({
                        'article':slug,'ordinal':len(link_ids),
                        'byte_offset':byte_offset,'target_slug':target,
                        'target_route':route_map[target],
                        'label_sha256':fingerprint(label.encode('utf-8'))})
            require(bool(citation_ids), 'no evidence citations '+slug)
            # Source-use metadata may include explanatory references omitted
            # from prose; report rather than remove or silently approve them.
            unused=sorted(expected_source_ids-set(citation_ids))
            report['articles'].append({'n':row['n'],'slug':slug,'track':row['track'],
                  'canonical_route':row['route'], 'body_git_oid':row['body_oid'],
                  'body_bytes':len(raw),'body_sha256':fingerprint(raw),
                  'citation_occurrences':len(citation_ids),
                  'unique_cited_sources':len(set(citation_ids)),
                  'internal_link_occurrences':len(link_ids),
                  'unused_declared_source_ids':unused,
                  'text_characters_estimate':len(re.sub(r'<[^>]*>','',content))})
            counts['citation_occurrences']+=len(citation_ids)
            counts['internal_links']+=len(link_ids)
            counts['source_uses_declared']+=len(uses)
            counts['body_bytes']+=len(raw)
        report['summary']={
            'articles':len(rows), 'citation_occurrences':counts['citation_occurrences'],
            'internal_link_occurrences':counts['internal_links'],
            'source_use_declarations':counts['source_uses_declared'],
            'original_body_bytes':counts['body_bytes'],
            'ambiguous_citation_occurrences':len(report['ambiguous_source_origins']),
            'independent_claim_support_verified':False,
            'release_ready':False}
        report['state']=HOLD
    except (Blocked,KeyError,TypeError,ValueError,AttributeError) as exc:
        report['errors']=[str(exc)[:400]]
        report['summary']={}
        report['articles']=[]
        report['citation_ledger']=[]
        report['internal_link_ledger']=[]
        report['ambiguous_source_origins']=[]
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',default='.')
    ap.add_argument('--report')
    args=ap.parse_args(argv)
    repo=Path(args.repo).resolve()
    try:
        gate=load_r202()
        raw=(repo/MANIFEST_PATH).read_bytes()
        require(gate.oid(raw)==gate.MANIFEST_OID,
                'frozen original 35-article roster identity drift')
        manifest=gate.strict_json(raw)
        trees={name:gate.branch_listing(repo,sha) for name,sha in gate.HEADS.items()}
        metas=gate.read_article_metadata(repo,manifest)
        sources=gate.read_source_registers(repo)
        structural=gate.check(manifest,trees,metas,sources)
        require(structural['state']==HOLD and not structural['errors'],
                'R202 source/branch structural gate failed: '+str(structural.get('errors')))
        result=check(manifest,read_bodies(repo,manifest,gate),metas,sources,structural)
    except (Blocked,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,
            UnicodeError,ValueError,KeyError,ImportError) as exc:
        result={'schema':SCHEMA,'state':INVALID,
                'publication_authorized':False, 'independent_qd_pass':False,
                'errors':[str(exc)[:400]]}
    rendered=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
    if args.report:
        Path(args.report).write_text(rendered,encoding='utf-8')
    else:
        print(rendered,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
