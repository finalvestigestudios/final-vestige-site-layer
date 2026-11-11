#!/usr/bin/env python3
"""R300: fail-closed 35 metadata + CSS source integrity; no release approval."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PREV='preparedness/tools/r299_native_export_source_reproduction_hold.py'
PREV_OID='f1ba7018ac34f48e286119aa1dad38e2a669eca8'
CUSTODY='preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
CUSTODY_OID='5822f9dfde21d1f3bdfc26658769d852c639438c'
CSS='preparedness/assets/preparedness.css'
CSS_OID='e354395cdb7985eb2fe16b99ca9fd66c9885557e'
# Exact integrated metadata OIDs different from frozen R200. Derived other 23
# pins from the independently pinned R200 custody manifest: 35 exact pins total.
OVERRIDES={
 'three-day-kit':'1c69d5f1636a3a41631a5d93f11254d85cbe1b59',
 'making-water-safer':'827d861eb3beebfd010ee98fcca764b23a2de90e',
 'homemade-water-filters':'91c730bd1c7a61fa3140a86245c9bc0c88160c29',
 'outage-heat-cold-generators':'be37b602d0b82593d438083dfc8a1e5ef595dd44',
 'home-fire-escape-plan':'ff1246dcbfb0dd0bc864977f815badb9ad4e7ed8',
 'shelter-or-evacuate':'cb559141d1e4a39debad16cf5cb796b746a01f19',
 'family-communication-plan':'dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3',
 'preparedness-real-households':'ba840917f34634ccd634c488eeca4a8a6b3a8fe2',
 'salt-beef-salt-pork-age-of-sail':'1c4c5396da703f3724b584c67e49e2128ab1f4c6',
 'pioneer-travel-rations':'7191acba55d63dc405ad9c2003d66193276da89f',
 'pemmican-and-dried-meats':'03d3824e07fe51931671d0ddc7aa8c85eda58435',
 'pioneer-supply-chains-failed':'4d2dc4958736e3c5257c65dda8ed016a473ac6be',
}

def blob(b:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def safe_file(root:Path,p:Path)->bool:
 try:
  r=root.absolute();p=p.absolute()
  if not p.is_relative_to(r) or not p.is_file():return False
  while p!=r:
   if p.is_symlink():return False
   p=p.parent
  return True
 except (OSError,ValueError,RuntimeError):return False

def audit(root:Path,custody:dict,previous:dict|None=None)->dict:
 errors=[];drift=[];rows=custody.get('articles') if isinstance(custody,dict) else None
 if not isinstance(rows,list) or len(rows)!=35:rows=[];errors.append('R200_35_ARTICLES_MISSING')
 if set(OVERRIDES)-{x.get('slug') for x in rows if isinstance(x,dict)}:
  errors.append('R200_OVERRIDE_SLUG_MISSING')
 seen=set();article_dir=root/'preparedness/content/articles'
 expected={x.get('slug')+'.meta.json' for x in rows if isinstance(x,dict) and isinstance(x.get('slug'),str)}
 if not article_dir.is_dir():errors.append('ARTICLE_METADATA_DIRECTORY_MISSING')
 else:
  actual={p.name for p in article_dir.iterdir() if p.name.endswith('.meta.json')}
  if actual!=expected:errors.append('ARTICLE_METADATA_FILE_INVENTORY_CHANGED')
 for x in rows:
  if not isinstance(x,dict):errors.append('INVALID_R200_ARTICLE');continue
  slug=x.get('slug');old=x.get('meta_oid')
  if not isinstance(slug,str) or not slug or '/' in slug or slug in seen:
   errors.append('R200_SLUG_INVALID');continue
  seen.add(slug);expected_oid=OVERRIDES.get(slug,old)
  if not isinstance(expected_oid,str) or len(expected_oid)!=40:
   errors.append('EXPECTED_META_OID_INVALID:'+slug);continue
  if slug in OVERRIDES:
   if old==expected_oid:errors.append('UNEXPECTED_R200_META_IDENTITY:'+slug)
   drift.append({'slug':slug,'r200_meta_oid':old,'integrated_meta_oid':expected_oid,
                 'status':'UNADJUDICATED_METADATA_LINEAGE'})
  p=article_dir/(slug+'.meta.json')
  if not safe_file(root,p):errors.append('MISSING_OR_SYMLINK_META:'+slug)
  else:
   try:
    if blob(p.read_bytes())!=expected_oid:errors.append('CHANGED_META:'+slug)
   except OSError:errors.append('UNREADABLE_META:'+slug)
 if len(seen)!=35:errors.append('ARTICLE_SLUG_INVENTORY_INVALID')
 p=root/CSS
 if not safe_file(root,p):errors.append('MISSING_OR_SYMLINK_STYLESHEET')
 else:
  try:
   if blob(p.read_bytes())!=CSS_OID:errors.append('CHANGED_STYLESHEET')
  except OSError:errors.append('UNREADABLE_STYLESHEET')
 if previous is not None and (not isinstance(previous,dict) or previous.get('state')!='DRAFT_HARD_HOLD'
   or previous.get('errors') or previous.get('native_export_byte_matches')!=41
   or previous.get('publication_authorized') is not False
   or previous.get('independent_qd_pass') is not False
   or previous.get('all_41_exports_independently_approved') is not False):
  errors.append('R299_EXACT_EXPORT_GATE_NOT_VERIFIED')
 return {'schema':'fv-preparedness-r300-meta-style-custody-v1',
         'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
         'errors':sorted(set(errors)),'article_metadata_pinned':len(seen),
         'integrated_css_oid':CSS_OID,'r200_metadata_lineage_holds':drift,
         'lineage_reviewed':False,'all_41_exports_independently_approved':False,
         'publication_authorized':False,'independent_qd_pass':False,
         'medical_safety_verified':False,'privacy_verified':False,
         'paid_order_count':None,'net_revenue_per_1000_qualified_sessions':None}

def run(root:Path)->dict:
 for rel,want in ((CUSTODY,CUSTODY_OID),(PREV,PREV_OID)):
  p=root/rel
  if not safe_file(root,p) or blob(p.read_bytes())!=want:
   raise ValueError('PINNED_UPSTREAM_CHANGED_OR_MISSING:'+rel)
 custody=json.loads((root/CUSTODY).read_bytes())
 first=audit(root,custody)
 if first['errors']:return first
 spec=importlib.util.spec_from_file_location('fv_r300_previous',root/PREV)
 if spec is None or spec.loader is None:raise ValueError('PREVIOUS_GATE_NOT_IMPORTABLE')
 previous_module=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(previous_module)
 return audit(root,custody,previous_module.run(root))

def main(argv=None)->int:
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
 args=ap.parse_args(argv)
 try:res=run(args.repo_root)
 except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
  res={'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_REPOSITORY_UNAVAILABLE:'+type(exc).__name__],
       'publication_authorized':False,'independent_qd_pass':False,
       'all_41_exports_independently_approved':False,'medical_safety_verified':False}
 print(json.dumps(res,indent=2,sort_keys=True))
 return 2 if res['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
