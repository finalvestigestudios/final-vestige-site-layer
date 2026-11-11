#!/usr/bin/env python3
"""R301 Preparedness: independent 35-body custody + reader/citation export fidelity.

Read-only, draft-only. This checks exact body inputs and the reader-facing main
body independently of the native builder. Never approves health/safety, QD,
WordPress publishing, products or revenue. R200 divergences remain unadjudicated.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

CUSTODY = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
CUSTODY_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
PREV = 'preparedness/tools/r300_metadata_css_pin_hold.py'
PREV_OID = 'ae83f747491ee1665d0bf5fb5272a8dd2a4d492e'
# Independent, exact integrated Git blob identity overrides. Other 21 body
# identities come from the pinned, frozen R200 custody file. These overrides
# describe current bytes; they DO NOT adjudicate the reasons for divergence.
OVERRIDES = {
 'household-emergency-plan':'f81cd43516e8295104230412f18776919148f905',
 'three-day-kit':'933f38ff3cd55a241cf9b392014fc52d4961e84f',
 'outage-heat-cold-generators':'2cd3e30b3a7e3dfdb3fd30cfd2b832355f58dfe2',
 'home-fire-escape-plan':'0412484304a3bcf08f0bb1b170110f617e3c2869',
 'shelter-or-evacuate':'de3cb805041904cf22d4f216296bd4c8ddec17c1',
 'family-communication-plan':'8ac8bd7dba3be15d477c15737e54d83364d72527',
 'go-bags':'e5910015fc6e33ad015bc5dc0605b86622b701be',
 'preparedness-real-households':'68344cf6c4022285fffb2a01f42027bf6f9ee95d',
 'pioneer-travel-rations':'058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7',
 'pemmican-and-dried-meats':'0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5',
 'root-cellars-cool-storage':'2ff8d029769aa9a97de6b1e388d937899f3af38c',
 'navigation-before-gps':'3c02e58c30d1d608224944142f31fbead44a1252',
 'sanitation-before-germ-theory':'d56df76647d2598f35cfd4609f91649cef063f12',
 'pioneer-supply-chains-failed':'ad158ee898f76d05bcb65c845b1e4a0e8103c660',
}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|([^{}]+)\}\}')
INLINE_JS = re.compile(r'\{\{inline-js:([a-z_]+\.js)\}\}')
WHITESPACE = re.compile(r'\s+')


def blob(data:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def safe(root:Path,rel:str)->bool:
 try:
  base=root.absolute();p=(base/rel).absolute()
  if not p.is_relative_to(base) or not p.is_file():return False
  while p!=base:
   if p.is_symlink():return False
   p=p.parent
  return True
 except (ValueError,OSError,RuntimeError):return False


class Reader(HTMLParser):
 """Independent main-body reader-text and citation occurrence extractor.

 Never claims CSS visibility, screen-reader equivalence, or browser safety.
 Citation IDs in the source must occur in ordinary text, not attributes/scripts.
 """
 def __init__(self,mode:str):
  super().__init__(convert_charrefs=True)
  if mode not in ('source','export'):raise ValueError('mode')
  self.mode=mode;self.main_count=0;self.depth=0;self.skips=0
  self.cite_open=False;self.cite_href=None;self.cite_label=[]
  self.cites=[];self.parts=[];self.errors=[]

 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs);classes=(attrs.get('class') or '').split()
  if self.mode=='export' and tag=='div' and attrs.get('id')=='pa-main':
   if self.depth or self.main_count:self.errors.append('MULTIPLE_OR_NESTED_MAIN_BODIES')
   else:self.main_count+=1;self.depth=1
   return
  if self.mode=='export' and not self.depth:return
  if self.mode=='export' and tag=='div':self.depth+=1
  if tag in ('script','style','template'):self.skips+=1
  if self.mode=='export' and tag=='sup' and 'pa-cite' in classes:
   if self.cite_open:self.errors.append('NESTED_CITATION')
   self.cite_open=True;self.cite_href=None;self.cite_label=[]
  elif self.mode=='export' and self.cite_open and tag=='a':
   href=attrs.get('href','') or ''
   if not re.fullmatch(r'#src-[1-9][0-9]*',href) or self.cite_href is not None:
    self.errors.append('INVALID_CITATION_ANCHOR')
   else:self.cite_href=int(href[5:])

 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  self.handle_endtag(tag)

 def handle_endtag(self,tag):
  if self.mode=='export' and not self.depth:return
  if tag in ('script','style','template') and self.skips:self.skips-=1
  if self.mode=='export' and tag=='sup' and self.cite_open:
   if self.cite_href is None or WHITESPACE.sub('', ''.join(self.cite_label))!=f'[{self.cite_href}]':
    self.errors.append('CITATION_MARKER_NOT_VERIFIED')
   else:self.cites.append(self.cite_href)
   self.cite_open=False
  if self.mode=='export' and tag=='div':self.depth-=1
  if self.depth<0:self.errors.append('UNBALANCED_BODY_DIV')

 def handle_data(self,data):
  if self.mode=='export' and not self.depth:return
  if self.skips:return
  if self.mode=='export':
   if self.cite_open:self.cite_label.append(data)
   else:self.parts.append(data)
  else:
   # Link labels are retained, but link targets are separately checked by R299.
   data=LINK.sub(lambda m:m.group(2),data)
   data=INLINE_JS.sub('',data)
   self.cites.extend(CITE.findall(data))
   self.parts.append(CITE.sub('',data))

 def finish(self):
  if self.mode=='export' and (self.main_count!=1 or self.depth or self.cite_open):
   self.errors.append('MISSING_OR_UNCLOSED_MAIN_BODY')
  return WHITESPACE.sub(' ',''.join(self.parts)).strip()


def reader_parity(source_html:str,export_html:str)->list[str]:
 src=Reader('source');src.feed(source_html);original=src.finish()
 out=Reader('export');out.feed(export_html);rendered=out.finish()
 errors=list(src.errors)+list(out.errors)
 if original!=rendered:errors.append('READER_BODY_TEXT_NOT_PRESERVED')
 numbers={};expected=[]
 for sid in src.cites:
  if sid not in numbers:numbers[sid]=len(numbers)+1
  expected.append(numbers[sid])
 if expected!=out.cites:errors.append('BODY_CITATION_OCCURRENCE_ORDER_DRIFT')
 return sorted(set(errors))


def audit(root:Path,custody:dict,previous:dict|None=None)->dict:
 errors=[];lineage=[];parity_count=0;body_count=0
 rows=custody.get('articles') if isinstance(custody,dict) else None
 if not isinstance(rows,list) or len(rows)!=35:rows=[];errors.append('R200_BODY_SLATE_INVALID')
 slugs=[];article_root=root/'preparedness/content/articles'
 for a in rows:
  if not isinstance(a,dict):errors.append('R200_ARTICLE_INVALID');continue
  slug=a.get('slug');old=a.get('body_oid')
  if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9-]+',slug) or slug in slugs:
   errors.append('R200_BODY_SLUG_INVALID');continue
  slugs.append(slug)
  expected=OVERRIDES.get(slug,old)
  if not isinstance(expected,str) or not re.fullmatch(r'[0-9a-f]{40}',expected):
   errors.append('BODY_PIN_INVALID:'+slug);continue
  if slug in OVERRIDES:
   if old==expected:errors.append('BODY_OVERRIDE_NOT_ACTUAL_DRIFT:'+slug)
   lineage.append({'slug':slug,'r200_body_oid':old,'integrated_body_oid':expected,
                   'state':'UNADJUDICATED_BODY_LINEAGE'})
  bodyrel=f'preparedness/content/articles/{slug}.body.html'
  if not safe(root,bodyrel):errors.append('BODY_MISSING_OR_SYMLINK:'+slug);continue
  try:
   raw=(root/bodyrel).read_bytes()
   if blob(raw)!=expected:errors.append('BODY_BYTES_CHANGED:'+slug);continue
   body_count+=1
   draftrel=f'preparedness/build/wp/{slug}.html'
   if not safe(root,draftrel):errors.append('DRAFT_MISSING_OR_SYMLINK:'+slug);continue
   parity=reader_parity(raw.decode('utf-8'),(root/draftrel).read_text(encoding='utf-8'))
   if parity:errors.extend(x+':'+slug for x in parity)
   else:parity_count+=1
  except (OSError,UnicodeError,ValueError) as exc:errors.append('BODY_DRAFT_UNREADABLE:'+slug+':'+type(exc).__name__)
 if set(OVERRIDES)-set(slugs):errors.append('OVERRIDE_SLUG_MISSING_FROM_R200')
 if len(set(slugs))!=35:errors.append('ARTICLE_BODY_COUNT_INVALID')
 if article_root.is_dir():
  actual={p.name for p in article_root.iterdir() if p.name.endswith('.body.html')}
  if actual!={x+'.body.html' for x in slugs}:errors.append('ARTICLE_BODY_INVENTORY_CHANGED')
 else:errors.append('ARTICLE_BODY_DIRECTORY_MISSING')
 if previous is not None and (not isinstance(previous,dict)
     or previous.get('state')!='DRAFT_HARD_HOLD' or previous.get('errors')
     or previous.get('article_metadata_pinned')!=35
     or previous.get('publication_authorized') is not False
     or previous.get('independent_qd_pass') is not False
     or previous.get('all_41_exports_independently_approved') is not False):
  errors.append('R300_UPSTREAM_CUSTODY_NOT_VERIFIED')
 return {'schema':'fv-preparedness-r301-body-reader-parity-v1',
         'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
         'errors':sorted(set(errors)),'body_pins_matched':body_count,
         'article_reader_parity_matched':parity_count,
         'body_lineage_disputes':lineage,'body_lineage_human_adjudicated':False,
         'all_41_exports_independently_approved':False,
         'publication_authorized':False,'independent_qd_pass':False,
         'medical_safety_verified':False,'privacy_verified':False,
         'merchant_approved':False,'verified_paid_orders':None,
         'net_revenue_per_1000_qualified_sessions':None}


def run(root:Path)->dict:
 for relative,want in ((CUSTODY,CUSTODY_OID),(PREV,PREV_OID)):
  if not safe(root,relative) or blob((root/relative).read_bytes())!=want:
   raise ValueError('PINNED_UPSTREAM_MISSING_OR_CHANGED:'+relative)
 custody=json.loads((root/CUSTODY).read_bytes())
 first=audit(root,custody)
 if first['errors']:return first
 spec=importlib.util.spec_from_file_location('fv_r301_upstream',root/PREV)
 if spec is None or spec.loader is None:raise RuntimeError('R300_IMPORT_FAILED')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return audit(root,custody,module.run(root))


def main(argv=None)->int:
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
 args=parser.parse_args(argv)
 try:result=run(args.repo_root)
 except (ValueError,OSError,UnicodeError,TypeError,RuntimeError,KeyError) as exc:
  result={'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_REPOSITORY_OR_BUILD_UNAVAILABLE:'+type(exc).__name__],
          'publication_authorized':False,'independent_qd_pass':False,
          'medical_safety_verified':False,'all_41_exports_independently_approved':False}
 print(json.dumps(result,indent=2,sort_keys=True))
 return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
