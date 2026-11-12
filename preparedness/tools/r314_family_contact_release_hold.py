#!/usr/bin/env python3
"""R314 dual-surface Article 15 / Tool 104 claim custody. REVIEW ONLY #136."""
import argparse, hashlib, importlib.util, json, re
from html import unescape
from pathlib import Path

HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('r313_gate',HERE/'r313_article_visible_citation_state_hold.py')
r313=importlib.util.module_from_spec(s);s.loader.exec_module(r313)
read=r313.r310.file_bytes; oid=r313.r310.oid
PRED=('preparedness/tools/r313_article_visible_citation_state_hold.py','209457045d1d44a18a26c1e2e31ddb8541bad49c')
PINS={
 'article':('preparedness/content/articles/family-communication-plan.body.html','8ac8bd7dba3be15d477c15737e54d83364d72527'),
 'article_meta':('preparedness/content/articles/family-communication-plan.meta.json','dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3'),
 'tool':('preparedness/content/tools/family-reunification-card.body.html','be8698ac5d020476ff649d85813810e2000c6f98'),
 'tool_meta':('preparedness/content/tools/family-reunification-card.meta.json','47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'),
 'js':('preparedness/tools/reunion_card.js','b1a09b1eda1ae26f081de65b400a37bc19538035')}
CITE=re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
NOTE=re.compile(r'<p\b[^>]*\bclass="pa-act-note"[^>]*>(.*?)</p>',re.S)
def prose(s):
 s=re.sub(r'<!--.*?-->','',s,flags=re.S)
 return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]*>',' ',s))).strip()
def inspect(a,am,t,tm):
 """Static review signals. Clean copy STILL needs human+native review."""
 errors=[];witness=[]
 for name,body,meta,slug in [('ARTICLE',a,am,'family-communication-plan'),('TOOL',t,tm,'family-reunification-card')]:
  if not isinstance(meta,dict) or meta.get('slug')!=slug or meta.get('status')!={'editorial':'drafted','publish':'draft'} or meta.get('safety_review',{}).get('state')!='pending':
   errors.append(name+'_DRAFT_SAFETY_STATE')
  if not isinstance(meta,dict) or set(CITE.findall(body))!=set(meta.get('source_use',{})):
   errors.append(name+'_CITATION_PARITY')
  notes=NOTE.findall(re.sub(r'<!--.*?-->','',body,flags=re.S))
  if len(notes)!=1:errors.append(name+'_NOTE_STRUCTURE')
  for note in notes:
   txt=prose(re.sub(r'\{\{cite:[^{}]+\}\}','',note))
   witness.append({'surface':name,'note_sha256':hashlib.sha256(txt.encode()).hexdigest()})
   if re.search(r'call\s+911\s+for\s+anything\s+life.threatening',txt,re.I):errors.append(name+'_NARROW_911')
   if re.search(r'text\s+messages?\s+rather\s+than\s+calls?\s+for\s+everything\s+else',txt,re.I):errors.append(name+'_UNCONDITIONAL_TEXT')
  txt=prose(body)
  if name=='ARTICLE':
   if re.search(r'keeps?\s+what\s+you\s+type\s+on\s+your\s+own\s+device',txt,re.I):errors.append('ARTICLE_PRIVACY_UNVERIFIED')
   if re.search(r'\bis\s+calmer\s+than\s+a\s+child\b',txt,re.I):errors.append('ARTICLE_CHILD_COMPARISON_UNSOURCED')
   if '{{link:family-reunification-card|' not in body:errors.append('ARTICLE_TOOL_LINK_MISSING')
  else:
   if re.search(r'what\s+you\s+type\s+stays\s+on\s+this\s+page|it\s+is\s+not\s+sent\s+or\s+saved|closing\s+the\s+tab\s+clears\s+it',txt,re.I):errors.append('TOOL_PRIVACY_UNVERIFIED')
   if re.search(r'\bnothing\s+is\s+stored\b',str(meta.get('description','')),re.I):errors.append('TOOL_META_PRIVACY_UNVERIFIED')
   if 'form below still works and prints' in txt.lower() and re.search(r'<noscript>\s*<style>[^<]*#rc\s*,[^<]*display\s*:\s*none',body,re.S|re.I):errors.append('TOOL_NOSCRIPT_CONTRADICTION')
   if '<noscript>' not in body or 'pa-foldcard' not in body:errors.append('TOOL_PRINT_FALLBACK_UNPROVEN')
 return {'state':'REVIEW_REDLINE_HARD_HOLD' if errors else 'COPY_REVIEW_HARD_HOLD','errors':sorted(set(errors)),'note_witnesses':witness,'publication_authorized':False,'independent_qd_pass':False,'medical_safety_verified':False,'actual_41_exports_verified':False,'paid_order_verified':False}
def run(root):
 problems=[];data={}
 for k,(p,sha) in {**PINS,'predecessor':PRED}.items():
  b=read(root,p)
  if b is None or oid(b)!=sha:problems.append('MISSING_OR_DRIFT:'+k)
  else:data[k]=b
 if problems:return {'state':'INVALID_HARD_HOLD','errors':problems,'publication_authorized':False,'independent_qd_pass':False}
 try:
  old=r313.run(root)
  result=inspect(data['article'].decode(),json.loads(data['article_meta']),data['tool'].decode(),json.loads(data['tool_meta']))
  result['inherited_state']=old.get('state')
  if old.get('state')!='DRAFT_HARD_HOLD':result['state']='INVALID_HARD_HOLD';result['errors']+=old.get('errors',[])
  return result
 except (ValueError,UnicodeError,KeyError,TypeError) as exc:
  return {'state':'INVALID_HARD_HOLD','errors':['INHERITED_OR_SOURCE_FAILURE:'+type(exc).__name__],'publication_authorized':False,'independent_qd_pass':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=HERE.parent.parent.parent)
 print(json.dumps(run(p.parse_args().root),indent=2,sort_keys=True));raise SystemExit(1)
