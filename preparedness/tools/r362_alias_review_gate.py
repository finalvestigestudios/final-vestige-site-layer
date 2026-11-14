#!/usr/bin/env python3
"""R362: verify unchanged reading scopes across crosswalk URL aliases.
Read-only, review-only, always HARD HOLD. A slash alias is never source approval.
"""
import argparse
from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit

SCHEMA='fv-preparedness-r362-alias-custody-v1'
CROSSWALK_SHA='d62e493a67dedd23e04cfdf3cce762ef933c6bf9'
FILES={
 'base':('register.json','b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',34),
 'food':('fragments/food.json','a1f73c8170932d6b3192e9cd506686d516d23d30',30),
 'health':('fragments/health.json','cc29c439372b9d49debf78e63020ffe4d62baeb8',21),
 'hist-field':('fragments/hist-field.json','3dafa9425f3829c0be2e6fea00889aff95124031',28),
 'hist-food':('fragments/hist-food.json','d10628342fea5f177a8d1be00dd906d0c9c7850e',28),
 'hist-home':('fragments/hist-home.json','8d85fd868508c5caba14a839d119d55f31f14f72',29),
 'shelter':('fragments/shelter.json','2a3f1a7ddeab2782add875be1e0e378513504aa1',45),
 'start':('fragments/start.json','96140d6d1872588e5d20d9052445c9157e88934d',29)}
HOLD={'qd_pass':False,'may_merge':False,'may_publish':False,
 'verified_sale':False,'medical_safety_verified':False,'source_approval':False}

def blob(data):
 return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def pairs(items):
 out={}
 for k,v in items:
  if k in out:raise ValueError('DUPLICATE_JSON_KEY:'+k)
  out[k]=v
 return out

def alias(url):
 p=urlsplit(url)
 return urlunsplit((p.scheme,p.netloc,(p.path or '/').rstrip('/') or '/',p.query,p.fragment))

def verify(crosswalk,fragments,*,pin=False):
 errors=[]
 if not isinstance(crosswalk,dict) or not isinstance(fragments,dict):return ['INVALID_INPUT']
 if pin and set(fragments)!=set(FILES):errors.append('ORIGIN_SET_DRIFT')
 if pin and crosswalk.get('status')!='DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED':
  errors.append('UNAUTHORIZED_SOURCE_APPROVAL')
 index=defaultdict(list); exact=set(); ids=Counter();count=0
 for origin,records in fragments.items():
  if not isinstance(records,list):errors.append('BAD_FRAGMENT:'+origin);continue
  for i,s in enumerate(records):
   if not isinstance(s,dict) or not isinstance(s.get('url'),str) or not s['url'].startswith('https://'):
    errors.append('BAD_SOURCE:'+origin+':'+str(i));continue
   if not isinstance(s.get('id'),str):errors.append('BAD_SOURCE_ID:'+origin+':'+str(i));continue
   count+=1;exact.add(s['url']);ids[s['id']]+=1
   index[alias(s['url'])].append((origin,i,s))
 duplicates={u:v for u,v in index.items() if len(v)>1}
 reported={'raw_source_rows':count,'unique_source_urls':len(exact),
           'duplicate_url_groups':len(duplicates),
           'duplicate_id_groups':sum(v>1 for v in ids.values())}
 for key,value in reported.items():
  if crosswalk.get(key)!=value:errors.append('COUNT_DRIFT:'+key)
 if pin and reported!={'raw_source_rows':244,'unique_source_urls':202,
                       'duplicate_url_groups':32,'duplicate_id_groups':15}:
  errors.append('ORIGINAL_INVENTORY_DRIFT')
 groups=crosswalk.get('groups')
 if not isinstance(groups,list):return sorted(set(errors+['MISSING_GROUPS']))
 seen=set()
 for group in groups:
  if not isinstance(group,dict) or not isinstance(group.get('url'),str):
   errors.append('BAD_GROUP');continue
  url=group['url'];key=alias(url)
  if key in seen:errors.append('DUPLICATE_GROUP:'+key)
  seen.add(key)
  if key not in duplicates:errors.append('NOT_DUPLICATED:'+key);continue
  if pin and (group.get('review_status')!='pending-human-source-and-reading-scope-review'
     or group.get('reviewer') is not None or group.get('reviewed_on') is not None):
   errors.append('UNAUTHORIZED_REVIEW_CLAIM:'+key)
  source={(origin,i):(s) for origin,i,s in duplicates[key]}
  identities=group.get('identities');variants=group.get('variants')
  if not isinstance(identities,list) or not isinstance(variants,list):
   errors.append('BAD_MEMBERS:'+key);continue
  for field,members in [('IDENTITY',identities),('VARIANT',variants)]:
   if any(not isinstance(m,dict) for m in members):errors.append('BAD_'+field+':'+key);continue
   keys=[(m.get('origin'),m.get('row_index')) for m in members]
   if len(keys)!=len(source) or set(keys)!=set(source):errors.append(field+'_CLOSURE:'+key)
   for m in members:
    k=(m.get('origin'),m.get('row_index'))
    if k not in source:continue
    if field=='VARIANT' and m.get('source')!=source[k]:errors.append('READING_SCOPE_CHANGED:'+key)
    if field=='IDENTITY' and m.get('id')!=source[k]['id']:errors.append('SOURCE_ID_REASSIGNED:'+key)
 if seen!=set(duplicates):errors.append('GROUP_CLOSURE_DRIFT')
 return sorted(set(errors))

def receipt(errors):
 return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
         'errors':sorted(set(errors)),**HOLD}

def audit(root):
 root=Path(root)
 if root.is_symlink() or not (root/'.git').exists():return receipt(['AUTHENTIC_CHECKOUT_MISSING'])
 p=root/'preparedness/sources'
 if p.is_symlink() or not p.is_dir():return receipt(['SOURCES_MISSING'])
 try:
  cw=p/'crosswalk.json'
  if cw.is_symlink() or blob(cw.read_bytes())!=CROSSWALK_SHA:
   return receipt(['CROSSWALK_BLOB_DRIFT'])
  read=lambda f:json.loads(f.read_text(encoding='utf-8'),object_pairs_hook=pairs)
  c=read(cw);fragments={}
  for origin,(rel,sha,n) in FILES.items():
   f=p/rel
   if f.is_symlink() or blob(f.read_bytes())!=sha:return receipt(['FRAGMENT_BLOB_DRIFT:'+origin])
   records=read(f)['sources']
   if len(records)!=n:return receipt(['FRAGMENT_COUNT_DRIFT:'+origin])
   fragments[origin]=records
  return receipt(verify(c,fragments,pin=True))
 except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError):
  return receipt(['SOURCE_PARSE_OR_IO_ERROR'])

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2]);args=a.parse_args()
 print(json.dumps(audit(args.repo_root),indent=2,sort_keys=True));raise SystemExit(2)
