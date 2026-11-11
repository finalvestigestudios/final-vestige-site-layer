#!/usr/bin/env python3
"""R302: independently audit article semantic HTML and citation-to-paragraph placement.

DRAFT/HARD HOLD only. Source-byte custody and native-export reproduction are
preconditions enforced by the exact pinned R301 predecessor, not reinterpreted
as human review. Never publish, never grant safety/QD or commercial approval.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import hashlib
import importlib.util
import json
from pathlib import Path
import re

PREV = 'preparedness/tools/r301_body_custody_reader_fidelity_hold.py'
PREV_OID = '51253107b4e367cd13f679f6c70426fea9b8adb9'
CUSTODY = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
CUSTODY_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
TOKEN = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}|\{\{link:([a-z0-9-]+)\|([^{}]+)\}\}|\{\{inline-js:([a-z_]+\.js)\}\}')
WS = re.compile(r'\s+')
SEMANTIC = set(('article','section','aside','nav','header','footer','main','div','h1','h2','h3','h4','h5','h6','p',
    'ol','ul','li','dl','dt','dd','blockquote','table','caption','thead','tbody','tfoot','tr','th','td',
    'figure','figcaption','pre','code','details','summary','form','fieldset','legend','label','button',
    'input','textarea','select','option','hr','br','img'))
VOID = {'hr','br','img','input'}
SKIP = {'script','style','template'}


def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def safe_file(root:Path,rel:str)->bool:
    try:
        base=root.absolute(); p=(base/rel).absolute()
        if not p.is_relative_to(base) or not p.is_file(): return False
        while p!=base:
            if p.is_symlink():return False
            p=p.parent
        return True
    except (OSError,ValueError,RuntimeError):return False


class Semantic(HTMLParser):
    """Ordered structural/text/citation events of original body vs wp #pa-main.

    This is structural/markup integrity, not a browser CSS or medical-safety test.
    Source citation IDs are mapped by first occurrence, exactly as the pinned
    native builder numbers them. The events keep citation adjacency and HTML
    section/list/table/heading structure, which R301's flat text cannot test.
    """
    def __init__(self,mode:str):
        super().__init__(convert_charrefs=True)
        if mode not in ('source','export'):raise ValueError('invalid mode')
        self.mode=mode;self.events=[];self.errors=[];self.buf=[]
        self.active=mode=='source';self.main_count=0;self.main_depth=0
        self.skip_stack=[];self.cite=False;self.cite_anchor=None
        self.cite_num={};self.structure=[]

    def _flush(self):
        if not self.buf:return
        s=WS.sub(' ',''.join(self.buf)).strip();self.buf=[]
        if s:self.events.append(('text',s))

    def _event(self,*items):
        self._flush();self.events.append(items)

    def _source_data(self,data:str):
        pos=0
        for m in TOKEN.finditer(data):
            self.buf.append(data[pos:m.start()])
            if m.group(1):
                sid=m.group(1)
                if sid not in self.cite_num:self.cite_num[sid]=len(self.cite_num)+1
                self._event('cite',self.cite_num[sid])
            elif m.group(2):self.buf.append(m.group(3))
            # inline JS token is intentionally excluded from human reading
            pos=m.end()
        self.buf.append(data[pos:])

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if self.mode=='export' and tag=='div' and attrs.get('id')=='pa-main':
            if self.main_depth or self.main_count:self.errors.append('MULTIPLE_MAIN_BODIES')
            else:self.active=True;self.main_depth=1;self.main_count+=1
            return
        if not self.active:return
        if self.mode=='export' and tag=='div':self.main_depth+=1
        if self.skip_stack:
            if tag in SKIP:self.skip_stack.append(tag)
            return
        if tag in SKIP:self.skip_stack.append(tag);return
        if self.cite:
            if tag=='a':
                href=attrs.get('href')
                if not isinstance(href,str) or not re.fullmatch(r'#src-[1-9][0-9]*',href) or self.cite_anchor is not None:
                    self.errors.append('BAD_INLINE_SOURCE_ANCHOR')
                else:self.cite_anchor=int(href[5:])
            return
        if self.mode=='export' and tag=='sup' and 'pa-cite' in (attrs.get('class') or '').split():
            self._flush();self.cite=True;self.cite_anchor=None;return
        if tag in SEMANTIC:
            # Preserve all authored attributes, not only selected CSS classes.
            self._event('open',tag,tuple(sorted(attrs.items())))
            if tag not in VOID:self.structure.append(tag)
            else:self._event('close',tag)

    def handle_endtag(self,tag):
        if not self.active:return
        if self.skip_stack:
            if tag==self.skip_stack[-1]:self.skip_stack.pop()
            return
        if self.cite:
            if tag=='sup':
                if self.cite_anchor is None:self.errors.append('SOURCE_ANCHOR_MISSING')
                else:self._event('cite',self.cite_anchor)
                self.cite=False;self.cite_anchor=None
            return
        if self.mode=='export' and tag=='div' and self.main_depth==1:
            self._flush();self.main_depth=0;self.active=False;return
        if tag in SEMANTIC and tag not in VOID:
            self._event('close',tag)
            if not self.structure or self.structure[-1]!=tag:self.errors.append('STRUCTURE_UNBALANCED:'+tag)
            else:self.structure.pop()
        if self.mode=='export' and tag=='div':self.main_depth-=1

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)

    def handle_data(self,data):
        if not self.active or self.skip_stack or self.cite:return
        if self.mode=='source':self._source_data(data)
        else:self.buf.append(data)

    def finish(self):
        self._flush()
        if self.structure:self.errors.append('UNCLOSED_SEMANTIC_BLOCK')
        if self.skip_stack:self.errors.append('UNCLOSED_SCRIPT_STYLE')
        if self.cite:self.errors.append('UNCLOSED_CITATION')
        if self.mode=='export' and (self.main_count!=1 or self.main_depth):self.errors.append('MAIN_BODY_NOT_CLOSED')
        return self.events


def compare(source:str,export:str)->list[str]:
    a=Semantic('source');a.feed(source);ae=a.finish()
    b=Semantic('export');b.feed(export);be=b.finish()
    errors=list(a.errors)+list(b.errors)
    if ae!=be:
        # Compare structure independently of text and cited sources, enabling
        # review to triage a lost section vs changed citation-to-claim position.
        if [x for x in ae if x[0] in ('open','close')]!=[x for x in be if x[0] in ('open','close')]:
            errors.append('SEMANTIC_HTML_STRUCTURE_DRIFT')
        if [x for x in ae if x[0]=='text']!=[x for x in be if x[0]=='text']:
            errors.append('BLOCK_LOCAL_READER_TEXT_DRIFT')
        if [x for x in ae if x[0]=='cite']!=[x for x in be if x[0]=='cite']:
            errors.append('SOURCE_CITATION_OCCURRENCE_DRIFT')
        if not errors:errors.append('CITATION_PLACEMENT_OR_BLOCK_ORDER_DRIFT')
    return sorted(set(errors))


def audit(root:Path,custody:dict,previous:dict|None=None)->dict:
    errors=[];checked=0
    rows=custody.get('articles') if isinstance(custody,dict) else None
    if not isinstance(rows,list) or len(rows)!=35:errors.append('R200_35_ARTICLE_SLATE_MISSING');rows=[]
    seen=set()
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('slug'),str) or not re.fullmatch(r'[a-z0-9-]+',row['slug']):
            errors.append('BAD_CUSTODY_ARTICLE');continue
        slug=row['slug']
        if slug in seen:errors.append('DUPLICATE_ARTICLE_SLUG');continue
        seen.add(slug)
        inp=f'preparedness/content/articles/{slug}.body.html';out=f'preparedness/build/wp/{slug}.html'
        if not safe_file(root,inp):errors.append('BODY_MISSING_OR_SYMLINK:'+slug);continue
        if not safe_file(root,out):errors.append('DRAFT_MISSING_OR_SYMLINK:'+slug);continue
        try:
            diffs=compare((root/inp).read_text(encoding='utf-8'),(root/out).read_text(encoding='utf-8'))
            errors.extend(x+':'+slug for x in diffs)
            if not diffs:checked+=1
        except (OSError,UnicodeError,ValueError) as exc:errors.append('UNREADABLE:'+slug+':'+type(exc).__name__)
    if len(seen)!=35:errors.append('35_ARTICLE_INVENTORY_INVALID')
    if previous is not None and (not isinstance(previous,dict) or previous.get('state')!='DRAFT_HARD_HOLD'
        or previous.get('errors') or previous.get('body_pins_matched')!=35
        or previous.get('article_reader_parity_matched')!=35
        or previous.get('publication_authorized') is not False
        or previous.get('independent_qd_pass') is not False
        or previous.get('medical_safety_verified') is not False
        or previous.get('all_41_exports_independently_approved') is not False):
        errors.append('R301_UPSTREAM_BODY_CUSTODY_UNVERIFIED')
    return {'schema':'fv-preparedness-r302-semantic-citation-claim-location-v1',
      'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
      'errors':sorted(set(errors)),'article_semantic_matches':checked,
      'upstream_source_custody_required':True,'browser_css_qa_verified':False,
      'source_truth_verified':False,'independent_human_approval':False,
      'all_41_exports_independently_approved':False,
      'publication_authorized':False,'independent_qd_pass':False,
      'medical_safety_verified':False,'privacy_verified':False,
      'merchant_approved':False,'confirmed_paid_orders':None,
      'net_revenue_per_1000_qualified_sessions':None}


def run(root:Path)->dict:
    for rel,want in ((PREV,PREV_OID),(CUSTODY,CUSTODY_OID)):
        if not safe_file(root,rel) or blob((root/rel).read_bytes())!=want:
            raise ValueError('PINNED_PREDECESSOR_OR_CUSTODY_CHANGED:'+rel)
    custody=json.loads((root/CUSTODY).read_bytes())
    initial=audit(root,custody)
    if initial['errors']:return initial
    spec=importlib.util.spec_from_file_location('fv_r302_prev',root/PREV)
    if spec is None or spec.loader is None:raise RuntimeError('R301_MODULE_IMPORT_UNAVAILABLE')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return audit(root,custody,mod.run(root))


def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    a=p.parse_args(argv)
    try:res=run(a.repo_root)
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
        res={'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_REPOSITORY_OR_BUILD_UNAVAILABLE:'+type(exc).__name__],
             'publication_authorized':False,'independent_qd_pass':False,'medical_safety_verified':False,
             'all_41_exports_independently_approved':False}
    print(json.dumps(res,indent=2,sort_keys=True))
    return 2 if res['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
