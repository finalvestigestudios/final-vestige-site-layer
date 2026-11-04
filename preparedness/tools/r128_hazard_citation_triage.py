#!/usr/bin/env python3
"""Review-only triage of 35 Preparedness articles against their visible citations.

This is a heuristic reviewer queue, NOT a source-content, medical-safety, or QD PASS.
Run with the *frozen* RC #584 checkout, not a newer contributor head.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

RC_SHA = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
CITE = re.compile(r'\{\{cite:([a-z][a-z0-9-]*)\}\}')
ANY_CITE = re.compile(r'\{\{cite:[^}]*\}\}')
BLOCK = frozenset(('p','li','td','th','blockquote','figcaption','h1','h2','h3','h4','h5','h6'))
IGNORE = frozenset(('script','style','template','noscript'))
VOID = frozenset(('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'))
# Discovery triggers only. Neither this list nor a keyword hit constitutes a safety assessment.
HAZARDS = {
    'medical_cold_chain': re.compile(r'\b(?:refrigerat(?:ed|ion)|insulin|medic(?:ine|ation|al)|prescri(?:be|ption)|dialysis)\b',re.I),
    'combustion_co': re.compile(r'\b(?:generator|carbon monoxide|charcoal|gas grill|fuel.burning|camp stove)\b',re.I),
    'food_preservation': re.compile(r'\b(?:pressure cann(?:er|ing)|botulis(?:m|tic)|jerky|dehydrat(?:e|ion)|smok(?:e|ing)house|curing meat)\b',re.I),
    'water_safety': re.compile(r'\b(?:boil.water|water advis(?:ory|ories)|disinfect(?:ant|ion)?|potab(?:le|ility)|water purif(?:y|ication)|bleach)\b',re.I),
    'electric_fire': re.compile(r'\b(?:main breaker|electric(?:al|ity)?|fire escape|smoke alarm|fire extinguish(?:er|ing|ers)?)\b',re.I),
}

class Hold(ValueError): pass

def need(condition, code):
    if not condition: raise Hold(code)

def gitblob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()

def distinct_object_pairs(pairs):
    out={}
    for key,value in pairs:
        need(key not in out,'DUPLICATE_JSON_KEY:'+key)
        out[key]=value
    return out

def parse_json_bytes(raw):
    return json.loads(raw.decode('utf-8'),object_pairs_hook=distinct_object_pairs)

class VisibleBlocks(HTMLParser):
    """Count visible citation tokens separately from article block-level triage."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth=0
        self.stack=[]
        self.blocks=[]
        self.visible=[]
    def handle_starttag(self,tag,attrs):
        if tag in VOID:return
        props=dict(attrs)
        invisible = (tag in IGNORE or 'hidden' in props or
                     props.get('aria-hidden','').lower()=='true' or
                     'inert' in props or
                     re.search(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)',
                               props.get('style',''),re.I) is not None)
        self.stack.append({'tag':tag,'invisible':invisible,'block':[] if tag in BLOCK else None})
        if invisible: self.depth+=1
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        self.handle_endtag(tag)
    def handle_endtag(self,tag):
        # HTML is trusted snapshot input, but tolerate void elements / minor unbalanced markup.
        match=next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i]['tag']==tag),None)
        if match is None:return
        while len(self.stack)>match:
            entry=self.stack.pop()
            if entry['invisible']:self.depth-=1
            if entry['block'] is not None:
                paragraph=' '.join(''.join(entry['block']).split())
                if paragraph:self.blocks.append(paragraph)
    def handle_data(self,data):
        if self.depth:return
        self.visible.append(data)
        for entry in self.stack:
            if entry['block'] is not None:entry['block'].append(data)

def triage_article(slug,html,meta):
    need(meta.get('slug')==slug,'METADATA_SLUG:'+slug)
    need(meta.get('status',{}).get('publish')=='draft','ARTICLE_NOT_DRAFT:'+slug)
    safety=meta.get('safety_review',{})
    need(safety.get('state') in ('pending','approved','not-required'),'SAFETY_STATE:'+slug)
    notes=meta.get('source_use')
    need(isinstance(notes,dict) and notes,'SOURCE_USE_MISSING:'+slug)
    need(all(isinstance(k,str) and isinstance(v,str) and v.strip() for k,v in notes.items()),
         'EMPTY_SOURCE_EXPLANATION:'+slug)
    p=VisibleBlocks();p.feed(html);p.close()
    raw=ANY_CITE.findall(html)
    need(html.count('{{cite:')==len(raw),'UNTERMINATED_CITATION:'+slug)
    visible=ANY_CITE.findall(''.join(p.visible))
    need(len(raw)==len(visible) and Counter(raw)==Counter(visible),
         'HIDDEN_CITATION:'+slug)
    need(len(visible)>0,'NO_VISIBLE_CITATIONS:'+slug)
    need(all(CITE.fullmatch(x) is not None for x in visible),'MALFORMED_CITATION:'+slug)
    ids=[CITE.fullmatch(x).group(1) for x in visible]
    need(all(k in notes for k in ids),'ORPHAN_CITATION:'+slug)
    review=[]
    for index,paragraph in enumerate(p.blocks,1):
        tags=[name for name,regex in HAZARDS.items() if regex.search(paragraph)]
        if not tags:continue
        cited=tuple(dict.fromkeys(CITE.findall(paragraph)))
        review.append({'block':index,'hazard_tags':tags,'source_ids':list(cited),
                       'local_citation_present':bool(cited),
                       'review_state':'OPEN_HUMAN_SOURCE_AND_SAFETY_REVIEW',
                       'excerpt':' '.join(CITE.sub('[citation]',paragraph).split())[:220]})
    return {'slug':slug,'citation_occurrences':len(ids),'unique_cited_source_ids':len(set(ids)),
            'source_use_notes':len(notes),'safety_metadata_state':safety['state'],
            'hazard_keyword_blocks':review,'uncited_hazard_keyword_blocks':sum(
                not r['local_citation_present'] for r in review)}

def audit(root,*, expected_citations=2000,verify_ref=False):
    root=Path(root)
    if verify_ref:
        try:
            sha=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],
                                        text=True,stderr=subprocess.DEVNULL).strip()
        except (OSError,subprocess.CalledProcessError) as e:raise Hold('GIT_HEAD_UNAVAILABLE') from e
        need(sha==RC_SHA,'WRONG_CANDIDATE_GIT_HEAD')
        try:
            dirty=subprocess.check_output(
                ['git','-C',str(root),'status','--porcelain','--untracked-files=no',
                 '--','preparedness/content/articles','preparedness/taxonomy.json'],
                text=True,stderr=subprocess.DEVNULL)
        except (OSError,subprocess.CalledProcessError) as e:raise Hold('GIT_STATUS_UNAVAILABLE') from e
        need(not dirty.strip(),'DIRTY_CANDIDATE_WORKTREE')
    tax=parse_json_bytes((root/'preparedness/taxonomy.json').read_bytes())
    slate=tax.get('slate')
    need(isinstance(slate,list) and len(slate)==35,'ARTICLE_COUNT_NOT_35')
    slugs=[r.get('slug') for r in slate]
    need(all(isinstance(x,str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',x) for x in slugs),
         'INVALID_SLUG')
    need(len(set(slugs))==35,'DUPLICATE_ARTICLE_SLUG')
    need(tax.get('base_path')=='/preparedness/','BASE_PATH_DRIFT')
    required={'household-emergency-plan','three-day-kit','go-bags','preparedness-real-households'}
    need(all(x.get('gate') is True for x in slate if x.get('slug') in required) and
         required.issubset(set(slugs)),'MISSING_START_HERE_GATE')
    result=[]; blobs=[]
    for slug in slugs:
        body=root/f'preparedness/content/articles/{slug}.body.html'
        meta=root/f'preparedness/content/articles/{slug}.meta.json'
        b,m=body.read_bytes(),meta.read_bytes()
        body_text=b.decode('utf-8')
        record=triage_article(slug,body_text,parse_json_bytes(m))
        result.append(record)
        blobs.append({'slug':slug,'body_blob':gitblob(b),'meta_blob':gitblob(m)})
    total=sum(r['citation_occurrences'] for r in result)
    if expected_citations is not None:need(total==expected_citations,'CITATION_CENSUS_DRIFT')
    return {'status':'HOLD_HUMAN_REVIEW','may_publish':False,'independent_QD_PASS':False,
            'medical_safety_verified':False,'checkout_verified':False,
            'candidate_sha_expected':RC_SHA,'git_head_checked':verify_ref,
            'article_count':len(result),'visible_citation_occurrences':total,
            'keyword_blocks':sum(len(r['hazard_keyword_blocks']) for r in result),
            'uncited_keyword_blocks':sum(r['uncited_hazard_keyword_blocks'] for r in result),
            'articles':result,'evidence_git_blobs':blobs,
            'disclaimer':'Heuristic keywords / local citation proximity are NOT proof of factuality, medical safety, source accuracy, or QD approval.'}

def main(argv=None):
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--candidate-root',type=Path,required=True)
    arg.add_argument('--expected-citations',type=int,default=2000)
    arg.add_argument('--verify-ref',action='store_true')
    args=arg.parse_args(argv)
    try:
        result=audit(args.candidate_root,expected_citations=args.expected_citations,verify_ref=args.verify_ref)
        print(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False))
        return 0
    except (Hold,OSError,ValueError,UnicodeError,TypeError) as ex:
        print('HOLD: '+str(ex),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
