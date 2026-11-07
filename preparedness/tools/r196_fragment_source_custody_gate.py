#!/usr/bin/env python3
"""R196 six-fragment source custody: structure only, NEVER editorial/safety clearance.

Read-only, locked against R194's authentic Git blob identities. Differences are
human workorders. Successful admission remains DRAFT_HARD_HOLD (exit 2).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r196-fragment-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
DOCKET_OID = '05d393013a952d9d2c92a6e1d9759ca53579ae8b'
PINS = {
 'hist-field': ('4f369122cc0e230ee39654c215f18ffc79b5cc85','6b65e0aaa777b4c5ebc57fbeade0386b4ab6c32f',26,28),
 'hist-food': ('d10628342fea5f177a8d1be00dd906d0c9c7850e','c1856c998c6c728f0de72221e5654a238df994a9',28,28),
 'hist-home': ('6460d4b0734991675c889f28be2f73a19e3c42c0','8d85fd868508c5caba14a839d119d55f31f14f72',27,29),
}
EXPECTED = {
 'hist-field':({'hist-field-oac-breen-diary','hist-field-ia-hastings-guide'},set(),{'loc-prairie-traveler':{'supports','notes'}}),
 'hist-food':({'nchfp-jerky'},{'hist-food-nchfp-jerky'},{}),
 'hist-home':({'hist-home-wellcome-chadwick-1842','hist-home-msu-simmons-1798'},set(),{'hist-home-loc-simmons-1796':{'notes'}}),
}
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
class CustodyError(ValueError): pass

def insist(ok, why):
    if not ok: raise CustodyError(why)

def oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()

def strict_json(raw):
    def pairs(items):
        result={}
        for k,v in items:
            insist(k not in result,'duplicate JSON key')
            result[k]=v
        return result
    def bad_constant(v): raise CustodyError('nonstandard JSON constant '+str(v))
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=bad_constant)

def source_map(raw, count):
    insist(type(raw) is bytes and len(raw)<200_000,'source fragment missing or oversize')
    data=strict_json(raw)
    insist(type(data) is dict and set(data)=={'sources'} and type(data['sources']) is list
           and len(data['sources'])==count,'source fragment roster/shape changed')
    mapped={}
    for entry in data['sources']:
        insist(type(entry) is dict and type(entry.get('id')) is str and ID.fullmatch(entry['id'])
               and entry['id'] not in mapped,'invalid or duplicate source identifier')
        for field in ('title','publisher','kind','url','supports','notes'):
            insist(type(entry.get(field)) is str and entry[field].strip(),
                   'missing source claim/URL/publisher: '+entry['id']+'/'+field)
        u=urlsplit(entry['url'])
        insist(u.scheme=='https' and bool(u.hostname) and not u.username and not u.password,
               'unsafe source URL '+entry['id'])
        insist(type(entry.get('human_link_check')) is bool,
               'human link-review flag must be literal boolean')
        mapped[entry['id']]=entry
    return mapped

def inspect(docket_bytes, blob_reader, *, docket_oid=DOCKET_OID, pins=PINS,
            expected=EXPECTED):
    result={'schema':SCHEMA,'issue':136,'coordination_issue':820,'state':INVALID,
      'publication_authorized':False,'independent_qd_pass':False,'source_claims_human_approved':False,
      'medical_safety_verified':False,'merchant_offer_verified':False,'verified_paid_orders':None,
      'realized_net_revenue':None,'source_aliases_approved':0,'fragments_checked':0,
      'old_sources':0,'observed_sources':0,'workorders':[],'cross_cluster_conflicts':[],
      'human_adjudication':'PENDING','errors':[]}
    try:
        insist(type(docket_bytes) is bytes and oid(docket_bytes)==docket_oid,
               'docket changed; explicit human rebaseline required')
        docket=strict_json(docket_bytes)
        insist(docket.get('schema')=='fv-preparedness-r194-seven-delta-citation-custody-v1'
               and docket.get('state')==HOLD and docket.get('issue')==136,
               'wrong docket authority/status')
        for k in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                  'source_claims_human_approved','merchant_offer_verified'):
            insist(docket.get(k) is False,'unauthorized approval '+k)
        fr=docket.get('source_fragments')
        insist(type(fr) is dict and set(fr)==set(pins)==set(expected),'source fragment roster drift')
        versions={}
        for group in sorted(pins):
            old_oid,new_oid,old_count,new_count=pins[group]
            row=fr[group]
            insist(type(row) is dict and row=={'frozen':old_oid,'observed':new_oid},
                   'untrusted fragment Git identifiers '+group)
            records=[]
            for blob_id,n in ((old_oid,old_count),(new_oid,new_count)):
                raw=blob_reader(blob_id)
                insist(type(raw) is bytes and oid(raw)==blob_id,
                       'missing/substituted fragment Git object '+group)
                records.append(source_map(raw,n))
            a,b=records
            added=set(b)-set(a); removed=set(a)-set(b)
            changed={sid:{k for k in set(a[sid])|set(b[sid]) if a[sid].get(k)!=b[sid].get(k)}
                     for sid in set(a)&set(b) if a[sid]!=b[sid]}
            want_add,want_remove,want_changed=expected[group]
            insist(added==want_add and removed==want_remove and changed==want_changed,
                   'unreviewed source roster or evidence delta '+group)
            result['workorders'].append({'cluster':group,'frozen_blob':old_oid,
              'observed_blob':new_oid,'frozen_count':len(a),'observed_count':len(b),
              'added_ids_unreviewed':sorted(added),'removed_ids_unaliased':sorted(removed),
              'changed_record_fields':[{'source_id':s,'changed_fields':sorted(changed[s]),
                'human_review':'PENDING'} for s in sorted(changed)],
              'unapproved_source_substitution':bool(removed),'human_review':'PENDING'})
            result['old_sources']+=len(a);result['observed_sources']+=len(b)
            result['fragments_checked']+=2
            versions[group]=b
        # Identical IDs reused across fragments can carry materially different claims.
        # Preserve versions separately: NEVER pick one without editorial adjudication.
        groups=sorted(versions)
        for i,g in enumerate(groups):
            for h in groups[i+1:]:
                for sid in sorted(set(versions[g])&set(versions[h])):
                    a,b=versions[g][sid],versions[h][sid]
                    if a!=b:
                        result['cross_cluster_conflicts'].append({
                          'source_id':sid,'clusters':[g,h],
                          'differing_fields':sorted(k for k in set(a)|set(b)
                                                  if a.get(k)!=b.get(k)),
                          'automatic_merge_prohibited':True,'human_review':'PENDING'})
        insist(result['fragments_checked']==6 and result['old_sources']==81
               and result['observed_sources']==85,'source census mismatch')
        result['state']=HOLD
    except (CustodyError,ValueError,TypeError,UnicodeError,KeyError,OSError,
            subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        result['errors'].append(str(exc)[:350])
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--docket',type=Path,required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args(argv)
    def gitread(blob_id):
        return subprocess.run(['git','cat-file','blob',blob_id],cwd=args.repo,
           check=True,timeout=15,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    try:
        result=inspect(args.docket.read_bytes(),gitread)
    except (OSError,ValueError,TypeError) as e:
        result={'schema':SCHEMA,'state':INVALID,'errors':[str(e)[:350]],
                'publication_authorized':False,'independent_qd_pass':False}
    output=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    if args.report: args.report.write_text(output,encoding='utf-8')
    else: print(output,end='')
    return 2 if result['state']==HOLD else 3

if __name__=='__main__': raise SystemExit(main())
