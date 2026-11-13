#!/usr/bin/env python3
"""R344 frozen source URL-to-citation identity. READ ONLY; NEVER safety/QD approval."""
from __future__ import annotations
from collections import defaultdict
from datetime import date
from hashlib import sha1,sha256
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlsplit,urlunsplit,unquote

SCHEMA='fv-preparedness-r344-source-url-citation-custody-v1'
SOURCE_PINS={
'register.json':'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
'fragments/food.json':'a1f73c8170932d6b3192e9cd506686d516d23d30',
'fragments/health.json':'cc29c439372b9d49debf78e63020ffe4d62baeb8',
'fragments/hist-field.json':'3dafa9425f3829c0be2e6fea00889aff95124031',
'fragments/hist-food.json':'d10628342fea5f177a8d1be00dd906d0c9c7850e',
'fragments/hist-home.json':'8d85fd868508c5caba14a839d119d55f31f14f72',
'fragments/shelter.json':'2a3f1a7ddeab2782add875be1e0e378513504aa1',
'fragments/start.json':'96140d6d1872588e5d20d9052445c9157e88934d'}
ID=re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
DATE=re.compile(r'\d{4}-\d{2}-\d{2}\Z')
SHA=re.compile(r'[0-9a-f]{64}\Z')
CUTOFF=date(2026,11,13)
HOLD={'qualified_qd_pass':False,'source_claim_support_verified':False,
'emergency_or_medical_advice_approved':False,'may_merge':False,'may_publish':False,
'paid_preparedness_sku_verified':False,'confirmed_paid_orders_verified':False,
'net_revenue_verified':False,'native_100_wordpress_preview_build_verified':False}

def git_blob(b:bytes)->str:
 return sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def canonical_url(raw:object)->tuple[str,list[str],list[str]]:
 if not isinstance(raw,str) or not raw or raw!=raw.strip() or len(raw)>4096:
  return '',['INVALID_SOURCE_URL'],[]
 if any(ord(c)<32 or ord(c)==127 for c in raw) or '\\' in raw:
  return '',['UNSAFE_CONTROL_OR_BACKSLASH_URL'],[]
 errors=[];notes=[]
 try:
  p=urlsplit(raw);scheme=p.scheme.lower()
  if scheme not in ('https','http') or not p.netloc or not p.hostname:
   return '',['NON_HTTP_OR_RELATIVE_SOURCE_URL'],[]
  if p.username is not None or p.password is not None or '@' in p.netloc:
   errors.append('SOURCE_URL_CREDENTIAL_OR_ATSIGN')
  host=p.hostname.lower().rstrip('.')
  if not host or '%' in host or host.startswith('.') or '..' in host or '_' in host:
   errors.append('INVALID_SOURCE_HOST')
  try:host=host.encode('idna').decode('ascii')
  except UnicodeError:errors.append('UNENCODABLE_SOURCE_HOST')
  if not re.fullmatch(r'[a-z0-9.-]+',host):errors.append('INVALID_SOURCE_HOST_CHARACTERS')
  try:
   ip=ipaddress.ip_address(host)
   if not ip.is_global or ip.is_multicast or ip.is_reserved or ip.is_loopback or ip.is_link_local:
    errors.append('PRIVATE_OR_RESERVED_SOURCE_IP')
   else:notes.append('PUBLIC_IP_SOURCE_URL_REQUIRES_HUMAN_REVIEW')
  except ValueError:
   if host in ('localhost','localhost.localdomain') or host.endswith(('.localhost','.local','.internal','.test','.invalid','.example')) or '.' not in host:
    errors.append('NONPUBLIC_SOURCE_HOST')
  port=p.port
  if port not in (None,80,443):errors.append('NONSTANDARD_SOURCE_PORT')
  if scheme!='https':notes.append('HTTP_SOURCE_LINK_REQUIRES_HUMAN_CHECK')
  if raw.count('#')>1:notes.append('MULTIPLE_FRAGMENT_MARKERS_REVIEW')
  if any(x in p.query.lower() for x in ('utm_','fbclid=','gclid=')):
   notes.append('URL_CAMPAIGN_QUERY_NOT_A_SOURCE_IDENTITY_SIGNAL')
  if unquote(p.path).startswith('//') or '/..' in unquote(p.path):
   errors.append('AMBIGUOUS_SOURCE_URL_PATH')
  netloc=host if port is None or port == (443 if scheme=='https' else 80) else host+':'+str(port)
  return urlunsplit((scheme,netloc,p.path or '/',p.query,p.fragment)),sorted(set(errors)),sorted(set(notes))
 except (ValueError,UnicodeError):
  return '',['INVALID_OR_AMBIGUOUS_URL_AUTHORITY'],[]

def _hash_fields(record:dict,keys:tuple[str,...])->str:
 return sha256(json.dumps({k:record.get(k) for k in keys},sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def record_errors(record:object,file_key:str,cutoff:date=CUTOFF)->tuple[list[str],dict|None]:
 errors=[]
 if not isinstance(record,dict):return ['INVALID_SOURCE_RECORD:'+file_key],None
 sid=record.get('id')
 if not isinstance(sid,str) or not ID.fullmatch(sid):
  return ['INVALID_SOURCE_ID:'+file_key],None
 for field in ('title','publisher','kind','supports'):
  v=record.get(field)
  if not isinstance(v,str) or not v.strip():
   errors.append('MISSING_SOURCE_FIELD:'+sid+':'+field)
 url,ue,notes=canonical_url(record.get('url'))
 errors.extend(x+':'+sid for x in ue)
 verified=record.get('verified_on')
 if verified is not None:
  if not isinstance(verified,str) or not DATE.fullmatch(verified):
   errors.append('BAD_VERIFICATION_DATE:'+sid)
  else:
   try:
    if date.fromisoformat(verified)>cutoff:errors.append('FUTURE_VERIFICATION_CLAIM:'+sid)
   except ValueError:errors.append('BAD_VERIFICATION_DATE:'+sid)
 hlc=record.get('human_link_check')
 if hlc is not None and type(hlc) is not bool:
  errors.append('NONBOOLEAN_HUMAN_LINK_CHECK:'+sid)
 if hlc is True:notes.append('HUMAN_LINK_FLAG_REQUIRES_INDEPENDENT_REVIEW_RECORD')
 if verified is None:notes.append('UNVERIFIED_RESEARCH_SOURCE_DO_NOT_CITE')
 return errors,{'id':sid,'source_file':file_key,'canonical_source_url':url,
 'source_identity_sha256':_hash_fields(record,('id','title','publisher','kind','url','verified_on','supports')),
 'substantive_sha256':_hash_fields(record,('id','title','publisher','kind','url','supports')),
 'verified_on':verified,'human_link_check':hlc is True,'notes':sorted(set(notes)),
 'publisher':record.get('publisher'),'kind':record.get('kind')}

def catalog_from_records(records:dict[str,list],*,cutoff:date=CUTOFF)->dict:
 errors=[];rows={};events=[];warnings=[]
 if not isinstance(records,dict):
  return {'errors':['INVALID_SOURCE_RECORD_MAPPING'],'rows':{},'events':[],'warnings':[]}
 for name,items in sorted(records.items(),key=lambda x:(x[0]!='register.json',x[0])):
  if not isinstance(items,list):errors.append('SOURCES_NOT_LIST:'+str(name));continue
  local=set()
  for item in items:
   e,row=record_errors(item,name,cutoff)
   errors.extend(e)
   if row is None:continue
   sid=row['id']
   if sid in local:errors.append('DUPLICATE_SOURCE_ID_IN_ONE_FILE:'+sid)
   local.add(sid)
   if sid not in rows:rows[sid]=row;continue
   prev=rows[sid]
   same_url=bool(prev['canonical_source_url']) and prev['canonical_source_url']==row['canonical_source_url']
   if prev['verified_on'] is None and row['verified_on'] is not None and same_url:
    events.append({'source_id':sid,'event':'UNVERIFIED_PLACEHOLDER_TO_RESEARCH_FETCH_REQUIRES_REVIEW',
      'from_file':prev['source_file'],'to_file':name,
      'source_metadata_changed':prev['substantive_sha256']!=row['substantive_sha256'],
      'not_a_human_link_or_claim_check':True})
    rows[sid]=row
   elif prev['verified_on'] is not None and row['verified_on'] is not None:
    events.append({'source_id':sid,'event':'MULTIPLE_VERIFIED_FRAGMENTS_REQUIRE_HUMAN_RECONCILIATION',
      'from_file':prev['source_file'],'to_file':name,
      'verified_date_conflict':prev['verified_on']!=row['verified_on'],
      'source_metadata_conflict':prev['substantive_sha256']!=row['substantive_sha256']})
    errors.append('VERIFIED_SOURCE_ID_MULTI_FRAGMENT_CONFLICT:'+sid)
   else:errors.append('SOURCE_ID_DUPLICATE_OR_UNAUTHORIZED_REDEFINITION:'+sid)
 byurl=defaultdict(list)
 for row in rows.values():
  if row['canonical_source_url']:byurl[row['canonical_source_url']].append(row['id'])
 for url,ids in sorted(byurl.items()):
  if len(ids)>1:warnings.append({'url_sha256':sha256(url.encode()).hexdigest(),
       'source_ids':sorted(ids),'review':'SAME_URL_DISTINCT_SOURCE_IDENTITIES_REVIEW'})
 return {'errors':sorted(set(errors)),'rows':rows,'events':events,'warnings':warnings}

def read_frozen_catalog(prep:Path,pins:dict[str,str]=SOURCE_PINS)->dict:
 source=prep/'sources';errors=[];records={}
 try:
  actual={p.relative_to(source).as_posix() for p in source.glob('*.json')}
  actual|={p.relative_to(source).as_posix() for p in (source/'fragments').glob('*.json')}
 except OSError:actual=set()
 if actual!=set(pins):
  errors.append('FROZEN_SOURCE_FILE_SET_DRIFT:'+';'.join(sorted(actual.symmetric_difference(set(pins)))))
 for rel,sha in sorted(pins.items()):
  p=source/rel
  if p.is_symlink() or not p.is_file():errors.append('MISSING_OR_SYMLINK_SOURCE_FILE:'+rel);continue
  try:
   blob=p.read_bytes()
   if git_blob(blob)!=sha:errors.append('SOURCE_GIT_BLOB_DRIFT:'+rel)
   records[rel]=json.loads(blob.decode('utf-8'))['sources']
  except (OSError,ValueError,UnicodeError,KeyError,TypeError):
   errors.append('INVALID_SOURCE_JSON:'+rel)
 catalog=catalog_from_records(records)
 catalog['errors']=sorted(set(errors+catalog['errors']))
 return catalog

def bind_tickets(catalog:dict,tickets:object)->dict:
 if not isinstance(tickets,list) or not tickets:
  return {'errors':['CITATION_TICKETS_MISSING'],'crosswalk':[]}
 errors=[];crosswalk=[];seen=set();rows=catalog.get('rows',{})
 for t in tickets:
  if not isinstance(t,dict):errors.append('INVALID_CLAIM_REVIEW_TICKET');continue
  sid=t.get('source_id');tid=t.get('ticket_id')
  if not isinstance(tid,str) or not re.fullmatch(r'[0-9a-f]{24}',tid) or tid in seen:
   errors.append('CLAIM_TICKET_ID_INVALID_OR_COLLIDING');continue
  seen.add(tid)
  if t.get('human_claim_source_adjudication')!='UNREVIEWED_REQUIRED':
   errors.append('UNAUTHORIZED_CLAIM_ADJUDICATION:'+tid)
  if not isinstance(sid,str) or sid not in rows:
   errors.append('CITED_SOURCE_WITHOUT_FROZEN_IDENTITY:'+str(sid));continue
  row=rows[sid]
  if row['verified_on'] is None:errors.append('CITED_SOURCE_HAS_NO_RESEARCH_VERIFICATION:'+sid)
  if not SHA.fullmatch(str(t.get('claim_text_sha256',''))):
   errors.append('INVALID_CLAIM_FINGERPRINT:'+tid)
  if not SHA.fullmatch(str(t.get('source_use_sha256',''))):
   errors.append('INVALID_SOURCE_USE_FINGERPRINT:'+tid)
  crosswalk.append({'ticket_id':tid,'source_id':sid,
      'source_identity_sha256':row['source_identity_sha256'],
      'registered_url_sha256':sha256(row['canonical_source_url'].encode()).hexdigest(),
      'research_verification_date':row['verified_on'],
      'human_link_check_verified':False,'claim_source_support_verified':False,
      'qualified_safety_review_verified':False,'adjudication':'UNREVIEWED_REQUIRED'})
 return {'errors':sorted(set(errors)),'crosswalk':crosswalk}

def report(errors:list[str],catalog:dict|None=None,binding:dict|None=None)->dict:
 c=catalog or {};b=binding or {}
 return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
  'errors':sorted(set(errors)),'frozen_source_files_expected':len(SOURCE_PINS),
  'distinct_registered_source_ids':len(c.get('rows',{})),
  'citation_occurrences_crosswalked':len(b.get('crosswalk',[])),
  'source_identity_crosswalk':b.get('crosswalk',[]),
  'duplicate_url_reviewer_docket':c.get('warnings',[]),
  'unverified_placeholder_promotions_requiring_review':c.get('events',[]),
  'human_source_link_checks_established':0,'original_contributor_conflicts_unresolved':15,
  'original_article15_tool104_claim_holds_unresolved':17,
  'safety_policy':'NO_FETCH_OR_CITATION_ADJACENCY_IS_MEDICAL_OR_CLAIM_SUPPORT',
  'known_limits':['URL parsing does not verify redirects/page content',
  'historical research dates do not prove source support',
  'qualified human safety and private WordPress build are separate'],**HOLD}

def audit_native(root:Path)->dict:
 prep=root/'preparedness' if (root/'preparedness').is_dir() else root
 try:
  from preparedness.tools import r343_claim_citation_review_crosswalk_hold as prior
  prior_report=prior.audit_native(root)
  if prior_report.get('state')!='DRAFT_HARD_HOLD' or prior_report.get('entries_inspected')!=41:
   return report(['R343_41_ENTRY_CLAIM_TICKET_GUARD_FAILED']+prior_report.get('errors',[]))
  catalog=read_frozen_catalog(prep);binding=bind_tickets(catalog,prior_report.get('review_tickets'))
  errors=catalog['errors']+binding['errors']
  if len(binding['crosswalk'])!=prior_report.get('citation_claim_review_tickets'):
   errors.append('SOURCE_CITATION_CROSSWALK_INCOMPLETE')
  return report(errors,catalog,binding)
 except (OSError,ValueError,TypeError,ImportError,KeyError,UnicodeError) as exc:
  return report(['AUTHENTIC_R343_AND_FROZEN_SOURCE_CHECKOUT_REQUIRED:'+type(exc).__name__])

def main()->int:
 import argparse
 p=argparse.ArgumentParser(description='R344 source URL identity HOLD, not release approval')
 p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
 res=audit_native(p.parse_args().repo_root)
 print(json.dumps(res,indent=2,sort_keys=True))
 return 2 if res['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
