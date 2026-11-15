"""R388 Preparedness: authenticated source-URL identity and alias review custody.

Read-only, non-authorizing forensic review of BASE and seven original Claude
source fragments. An apparent URL alias is NOT proof of source equivalence;
redirects, changed documents, and qualified safety need separate human review.
No publication, paid-offer, or QD approval is ever returned.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import ipaddress
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parent
PINS = ('5e7d9a8972872c82b4bc46ac13aab18883d8149a',
        '24b49f0a423119c2f612455f021669709a3f22b5',
        'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77')
ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
HEX = re.compile(r'^[a-f0-9]{40}$')
CONTROL = re.compile(r'[\x00-\x20\x7f]')
BAD_ESCAPE = re.compile(r'%(?![a-fA-F0-9]{2})')
PCT = re.compile(r'%[a-fA-F0-9]{2}')
UNRESERVED = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
TRACKERS = frozenset({'gclid','fbclid','msclkid','mc_cid','mc_eid','_hsenc','_hsmi'})
PROVENANCE_STATUS = 'SOURCE_IMPACT_REVIEW_HARD_HOLD'


def _load(name):
    spec = importlib.util.spec_from_file_location('r388_dep_'+name, ROOT / (name+'.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8')).hexdigest()


def _normalize_pct(value):
    def one(match):
        c = chr(int(match.group()[1:],16))
        return c if c in UNRESERVED else match.group().upper()
    return PCT.sub(one, value)


def url_identity(raw):
    """Conservative *review key*, not a redirect resolver or URL rewriter.

    Query order and all nontracking parameters remain significant; paths are
    only compared after unreserved percent-decoding and trailing slash trim.
    Normalization can yield false positives: humans must approve the evidence.
    """
    if not isinstance(raw, str) or len(raw) > 4000 or CONTROL.search(raw) or BAD_ESCAPE.search(raw):
        raise ValueError('UNSAFE_URL_CHARS')
    try:
        part = urlsplit(raw)
        host = part.hostname
        port = part.port
        if part.scheme != 'https' or not host or part.username is not None or part.password is not None or part.fragment:
            raise ValueError('NON_HTTPS_OR_CREDENTIALS_OR_FRAGMENT')
        domain = host.encode('idna').decode('ascii').lower().rstrip('.')
        if not domain or len(domain)>253 or '.' not in domain or domain.endswith(('.local','.internal','.test','.invalid')):
            raise ValueError('NON_PUBLIC_DOMAIN')
        try:
            addr=ipaddress.ip_address(domain.strip('[]'))
        except ValueError:
            addr=None
        if addr is not None and not addr.is_global:
            raise ValueError('NON_PUBLIC_IP_ADDRESS')
        if port is not None and port != 443:
            raise ValueError('NON_STANDARD_PORT_REVIEW')
        # Reject ambiguous slash escapes, which might change path routing.
        path=part.path or '/'
        if re.search(r'%2f|%5c',path,re.I) or '\\' in path or '/./' in path or '/../' in path:
            raise ValueError('AMBIGUOUS_PATH')
        path=_normalize_pct(path)
        if '/./' in path or '/../' in path or path.endswith(('/.','/..')):
            raise ValueError('NORMALIZED_PATH_TRAVERSAL')
        if path != '/': path=path.rstrip('/')
        kept=[]; dropped=[]
        for k,v in parse_qsl(part.query, keep_blank_values=True, strict_parsing=False):
            low=k.lower()
            if low.startswith('utm_') or low in TRACKERS: dropped.append(low)
            else: kept.append((k,v))
        # Keep the original order to avoid declaring order-sensitive URLs equal.
        query=json.dumps(kept, ensure_ascii=False, separators=(',', ':'))
        key=domain+path+'?'+query
        return {'key':key,'host':domain,'path':path,'query_keys':[k for k,_ in kept],
                'ignored_tracking_keys':sorted(set(dropped)),
                'raw_sha256':hashlib.sha256(raw.encode('utf-8')).hexdigest(),
                'nontracking_query_count':len(kept)}
    except (ValueError, UnicodeError, OverflowError) as exc:
        raise ValueError(str(exc)) from exc


def build_alias_docket(source_crosswalk, base_register, impact):
    errors=[]; rows=[]; grouped=defaultdict(list); by_id=defaultdict(list)
    if not isinstance(source_crosswalk,dict) or not isinstance(base_register,dict) or not isinstance(impact,dict):
        return {'status':'INVALID_HARD_HOLD','errors':['INVALID_INPUT_TYPES'],'publication_approved':False}
    if impact.get('status')!=PROVENANCE_STATUS or impact.get('publication_approved') is not False or impact.get('qualified_safety_approved') is not False:
        errors.append('UNAUTHENTIC_CLAIM_IMPACT')
    if impact.get('counts',{}).get('original_articles')!=35 or impact.get('counts',{}).get('source_collision_groups')!=5:
        errors.append('SOURCE_CLAIM_COVERAGE_DRIFT')
    if not isinstance(impact.get('claims'),list) or not impact['claims']:
        errors.append('MISSING_ORIGINAL_CLAIMS')
    source_groups = source_crosswalk.get('source_id_variants')
    base_sources = base_register.get('sources')
    if not isinstance(source_groups,list) or not isinstance(base_sources,list):
        return {'status':'INVALID_HARD_HOLD','errors':['SOURCE_INVENTORY_INVALID'], 'publication_approved':False}
    if source_crosswalk.get('original_fragment_count')!=7:
        errors.append('NOT_SEVEN_ORIGINAL_FRAGMENTS')
    seen=set(); raw_count=0; original_ids=set()
    def consume(sid, origin, raw, source_blob):
        nonlocal raw_count
        raw_count+=1
        if not isinstance(sid,str) or not ID.fullmatch(sid):
            errors.append('BAD_SOURCE_ID'); return
        try:
            ident=url_identity(raw)
        except ValueError:
            errors.append('UNSAFE_URL:'+sid+':'+origin); return
        identity=(sid,origin,source_blob,ident['raw_sha256'])
        if identity in seen: errors.append('DUPLICATED_SOURCE_RECORD:'+sid)
        seen.add(identity)
        entry={'id':sid,'origin':origin,'source_blob':source_blob,
               'raw_sha256':ident['raw_sha256'],'host':ident['host'],
               'path':ident['path'],'query_keys':ident['query_keys'],
               'ignored_tracking_keys':ident['ignored_tracking_keys']}
        rows.append(entry)
        grouped[ident['key']].append(entry)
        by_id[sid].append((ident['key'],entry))
    for r in base_sources:
        if not isinstance(r,dict):errors.append('BAD_BASE_ROW');continue
        consume(r.get('id'),'BASE',r.get('url'),'BASE_PINNED_REGISTRY')
    for group in source_groups:
        if not isinstance(group,dict) or not isinstance(group.get('variants'),list):
            errors.append('BAD_SOURCE_GROUP');continue
        sid=group.get('id')
        if sid in original_ids:errors.append('DUPLICATE_SOURCE_GROUP:'+str(sid))
        original_ids.add(sid)
        for v in group['variants']:
            if not isinstance(v,dict) or v.get('id')!=sid or not HEX.fullmatch(str(v.get('source_blob'))):
                errors.append('INVALID_VARIANT_PROVENANCE:'+str(sid));continue
            if not isinstance(v.get('branch'),str) or not isinstance(v.get('fragment'),str):
                errors.append('INVALID_VARIANT_BRANCH:'+str(sid));continue
            consume(sid,v['branch'],v.get('url'),v['source_blob'])
    cites=defaultdict(list)
    for row in impact.get('claims',[]):
        if not isinstance(row,dict) or not isinstance(row.get('source_id'),str):
            errors.append('INVALID_ORIGINAL_CLAIM');continue
        cites[row['source_id']].append({'article':row.get('article'),'branch':row.get('branch'),
            'citation_ordinal':row.get('citation_ordinal'), 'claim_sha256':row.get('claim_sha256')})
    docket=[]
    for key, group in sorted(grouped.items()):
        ids=sorted({r['id'] for r in group})
        raws={r['raw_sha256'] for r in group}
        if len(ids)<2 and len(raws)<2: continue
        sidclaims=[]
        for sid in ids: sidclaims.extend(cites[sid])
        sidclaims.sort(key=lambda r:(str(r['article']),str(r['branch']),str(r['citation_ordinal'])))
        docket.append({'review_key_sha256':hashlib.sha256(key.encode()).hexdigest(),
            'host':group[0]['host'],'path':group[0]['path'],
            'ids':ids,'origin_records':sorted(group,key=lambda r:(r['id'],r['origin'],r['raw_sha256'])),
            'cross_id_alias':len(ids)>1,'url_form_variants':len(raws),
            'impacted_claims':sidclaims, 'claim_occurrences':len(sidclaims),
            'human_adjudicated':False,'source_equivalence_proven':False,'source_safe_for_advice':False})
    # One source ID pointing to multiple materially distinct URL identities is a
    # separate high-priority review; do not silently pick the newest URL.
    identity_drift=[]
    for sid, pairs in sorted(by_id.items()):
        if len({key for key,_ in pairs})>1:
            identity_drift.append({'id':sid,'distinct_url_identities':len({k for k,_ in pairs}),
                'raw_url_fingerprints':sorted({e['raw_sha256'] for _,e in pairs}),
                'impacted_claims':sorted(cites[sid],key=lambda x:(str(x['article']),str(x['branch']),str(x['citation_ordinal']))),
                'human_adjudicated':False,'source_equivalence_proven':False})
    result={'schema':1, 'status':'INVALID_HARD_HOLD' if errors else 'SOURCE_URL_ALIAS_REVIEW_HARD_HOLD',
        'release_state':'DRAFT_HARD_HOLD', 'errors':sorted(set(errors)),
        'counts':{'source_records':raw_count,'valid_url_records':len(rows),
                  'alias_review_groups':len(docket), 'identity_drift_ids':len(identity_drift), 'impacted_claim_occurrences':sum(x['claim_occurrences'] for x in docket),
                  'original_articles':impact.get('counts',{}).get('original_articles'),
                  'unselected_source_collisions':impact.get('counts',{}).get('source_collision_groups')},
        'alias_review':docket,'source_id_identity_drift':identity_drift, 'provenance_digest':digest(rows),
        'publication_approved':False,'qualified_safety_approved':False,
        'merchant_offer_verified':False,'live_release_allowed':False}
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',default='.')
    a=ap.parse_args(argv)
    try:
        docs=[]
        for sha in PINS:
            raw=subprocess.run(['git','-C',a.repo,'cat-file','blob',sha],check=True,
                 capture_output=True,timeout=20).stdout
            if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw,usedforsecurity=False).hexdigest()!=sha:
                raise ValueError('GIT_BLOB_IDENTITY_MISMATCH')
            docs.append(json.loads(raw))
        r385=_load('r385_source_claim_blast_radius')
        def read(sha):
            return subprocess.run(['git','-C',a.repo,'cat-file','blob',sha],check=True,
                   capture_output=True,timeout=20).stdout
        impact=r385.build_original_docket(*docs,read)
        result=build_alias_docket(docs[1],docs[2],impact)
    except (OSError, ValueError, TypeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        result={'status':'INVALID_HARD_HOLD','errors':['ORIGINAL_AUTHENTIC_GIT_INPUT_UNAVAILABLE:'+type(exc).__name__],
                'publication_approved':False,'qualified_safety_approved':False}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2  # Review packets never grant publication clearance.

if __name__=='__main__':
    raise SystemExit(main())
