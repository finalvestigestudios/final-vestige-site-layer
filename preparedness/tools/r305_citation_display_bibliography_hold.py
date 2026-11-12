#!/usr/bin/env python3
"""R305: independent citation-display ↔ bibliography parity for WP-only drafts.

This read-only Preparedness review gate verifies that each visible superscript
marker, accessible source name, target ID and rendered bibliography source title
agree. It does not approve source claims, inspect external web pages or publish.
R304's exact-predecessor chain remains mandatory. No permissive PASS state.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

UPSTREAM='preparedness/tools/r303_inline_semantic_aria_hold.py'
UPSTREAM_OID='2412b455a96bc008b2313b5f2f372c7210cc06f5'
CUSTODY='preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
CUSTODY_OID='5822f9dfde21d1f3bdfc26658769d852c639438c'
SLUG=re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
NUM=re.compile(r'src-([1-9][0-9]*)\Z')


def blob(raw:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def safe_file(root:Path,rel:str)->bool:
    try:
        base=root.absolute(); current=(base/rel).absolute()
        if not current.is_relative_to(base) or not current.is_file():return False
        while current!=base:
            if current.is_symlink():return False
            current=current.parent
        return True
    except (OSError, ValueError, RuntimeError):return False


def safe_source_link(url:str)->bool:
    if not isinstance(url,str) or not url or any(ord(c)<33 or ord(c)==127 for c in url):return False
    try:
        parsed=urlsplit(url)
        return (parsed.scheme.lower() in ('http','https') and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and parsed.port in (None,80,443) and not parsed.fragment.startswith('javascript:'))
    except ValueError:return False


class CitationDisplay(HTMLParser):
    """Capture only native builder's .pa-cite and .pa-sources OL <li id=src-N>.

    Record duplicates and malformed source anchors even when a different target
    happens to have matching words. Generated citations are never human QD.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[];self.citations=[];self.biblio={};self.source_blocks=0
        self.source_depth=0;self.source_li=None;self.li_depth=0
        self.cite=None;self.cite_depth=0
        self.all_ids=Counter()

    def start(self,tag,attrs):
        names=[n for n,_ in attrs]
        d=dict(attrs)
        if len(names)!=len(set(names)) and (self.cite is not None or self.source_li is not None or tag in ('sup','li')):
            self.errors.append('DUPLICATE_CITATION_ATTRIBUTE')
        identity=d.get('id')
        if isinstance(identity,str) and NUM.fullmatch(identity):self.all_ids[identity]+=1
        if self.cite is not None:
            self.cite_depth+=1
            if tag=='a':
                self.cite['links'].append({'href':d.get('href'),'aria':d.get('aria-label'),'text':''})
                self.cite['active_link']=True
            return
        if self.source_li is not None:
            self.li_depth+=1
            self.source_depth+=1
            if tag=='a':
                self.source_li['links'].append({'href':d.get('href'),'rel':d.get('rel'),'text':''})
                self.source_li['active_link']=True
            return
        if tag=='sup' and 'pa-cite' in (d.get('class') or '').split():
            self.cite={'links':[],'text':'','active_link':False};self.cite_depth=1;return
        if tag=='section' and 'pa-sources' in (d.get('class') or '').split():
            self.source_blocks+=1
            if self.source_depth:self.errors.append('NESTED_SOURCES_BLOCK')
            self.source_depth=1;return
        if self.source_depth:
            self.source_depth+=1
            if tag=='li':
                if not isinstance(identity,str) or not NUM.fullmatch(identity):
                    self.errors.append('BIBLIOGRAPHY_ID_MISSING_OR_INVALID')
                self.source_li={'id':identity,'links':[],'text':'','active_link':False}
                self.li_depth=1

    def handle_starttag(self,tag,attrs):self.start(tag,attrs)
    def handle_startendtag(self,tag,attrs):
        self.start(tag,attrs);self.handle_endtag(tag)

    def handle_endtag(self,tag):
        if self.cite is not None:
            if tag=='a':self.cite['active_link']=False
            self.cite_depth-=1
            if self.cite_depth==0:
                self.citations.append(self.cite);self.cite=None
            elif self.cite_depth<0:self.errors.append('CITATION_UNBALANCED')
            return
        if self.source_li is not None:
            if tag=='a':self.source_li['active_link']=False
            self.li_depth-=1
            if self.li_depth==0:
                identity=self.source_li['id']
                if identity in self.biblio:self.errors.append('DUPLICATE_BIBLIOGRAPHY_ID')
                else:self.biblio[identity]=self.source_li
                self.source_li=None
            elif self.li_depth<0:self.errors.append('SOURCE_ROW_UNBALANCED')
            # both li and section depth decrease
            if self.source_depth:self.source_depth-=1
            return
        if self.source_depth:self.source_depth-=1

    def handle_data(self,data):
        if self.cite is not None:
            self.cite['text']+=data
            if self.cite['active_link']:self.cite['links'][-1]['text']+=data
        if self.source_li is not None:
            self.source_li['text']+=data
            if self.source_li['active_link']:self.source_li['links'][-1]['text']+=data

    def finish(self):
        if self.cite is not None:self.errors.append('UNCLOSED_CITATION')
        if self.source_li is not None:self.errors.append('UNCLOSED_SOURCE_ROW')
        if self.source_depth:self.errors.append('UNCLOSED_SOURCES_BLOCK')
        if self.source_blocks!=1:self.errors.append('SOURCES_BLOCK_COUNT_INVALID')
        if not self.citations:self.errors.append('NO_VISIBLE_CITATIONS')
        nums=set()
        for c in self.citations:
            if len(c['links'])!=1:self.errors.append('CITATION_ANCHOR_COUNT_INVALID');continue
            a=c['links'][0];href=a['href']
            if not isinstance(href,str) or not re.fullmatch(r'#src-[1-9][0-9]*',href):
                self.errors.append('CITATION_TARGET_INVALID');continue
            n=int(href[5:]);nums.add(n)
            if a['text']!=f'[{n}]' or c['text']!=f'[{n}]':
                self.errors.append('VISIBLE_CITATION_NUMBER_MISMATCH')
            row=self.biblio.get(f'src-{n}')
            if row is None:
                self.errors.append('CITATION_BIBLIOGRAPHY_TARGET_MISSING');continue
            if len(row['links'])!=1:
                self.errors.append('BIBLIOGRAPHY_LINK_COUNT_INVALID');continue
            source=row['links'][0]
            if a['aria']!=f'Source {n}: {source["text"]}':
                self.errors.append('CITATION_ACCESSIBLE_TITLE_MISMATCH')
        expected=set(range(1,len(self.biblio)+1))
        if nums!=expected:self.errors.append('CITATION_SEQUENCE_OR_UNUSED_SOURCE')
        for n in expected:
            row=self.biblio.get(f'src-{n}')
            if row is None: self.errors.append('BIBLIOGRAPHY_IDS_NOT_CONTIGUOUS');continue
            if len(row['links'])!=1:
                self.errors.append('BIBLIOGRAPHY_LINK_COUNT_INVALID');continue
            link=row['links'][0]
            if not safe_source_link(link['href']):self.errors.append('BIBLIOGRAPHY_URL_UNSAFE_OR_INVALID')
            if not isinstance(link['rel'],str) or 'noopener' not in link['rel'].split():
                self.errors.append('BIBLIOGRAPHY_NOOPENER_MISSING')
            if not link['text'].strip():self.errors.append('BIBLIOGRAPHY_TITLE_EMPTY')
            if 'Used for:' not in row['text'] or not ('Human source-link check pending' in row['text'] or 'Human source-link check complete' in row['text']):
                self.errors.append('BIBLIOGRAPHY_REVIEW_SCOPE_OR_HUMAN_LINK_STATUS_MISSING')
        for name,count in self.all_ids.items():
            if count!=1:self.errors.append('DUPLICATE_SOURCE_TARGET_ID')
        return sorted(set(self.errors))


def compare_document(html:str)->list[str]:
    p=CitationDisplay()
    try:
        p.feed(html);p.close()
        return p.finish()
    except (TypeError,ValueError,AttributeError,IndexError):return ['MALFORMED_CITATION_HTML']


def audit(root:Path,custody:dict,upstream:dict|None=None)->dict:
    errors=[];checked=0
    rows=custody.get('articles') if isinstance(custody,dict) else None
    if not isinstance(rows,list) or len(rows)!=35:
        errors.append('AUTHENTIC_35_ARTICLE_CUSTODY_MISSING');rows=[]
    seen=set()
    for row in rows:
        slug=row.get('slug') if isinstance(row,dict) else None
        if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in seen:
            errors.append('INVALID_OR_DUPLICATE_SLUG');continue
        seen.add(slug);p=f'preparedness/build/wp/{slug}.html'
        if not safe_file(root,p):errors.append('MISSING_OR_SYMLINKED_WORDPRESS_DRAFT:'+slug);continue
        try:
            e=compare_document((root/p).read_text(encoding='utf-8'))
            errors.extend(f'{code}:{slug}' for code in e)
            if not e:checked+=1
        except (OSError,UnicodeError):errors.append('UNREADABLE_DRAFT:'+slug)
    if len(seen)!=35:errors.append('INCOMPLETE_SLATE')
    if upstream is not None and (not isinstance(upstream,dict)
         or upstream.get('state')!='DRAFT_HARD_HOLD'
         or upstream.get('errors')!=[]
         or upstream.get('article_inline_semantic_matches')!=35
         or upstream.get('publication_authorized') is not False
         or upstream.get('independent_qd_pass') is not False
         or upstream.get('medical_safety_verified') is not False
         or upstream.get('all_41_exports_independently_approved') is not False):
        errors.append('R304_UPSTREAM_INTEGRITY_UNRECONCILED')
    return {
        'schema':'fv-preparedness-r305-citation-display-bibliography-hold-v1',
        'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
        'errors':sorted(set(errors)),
        'citation_display_and_bibliography_matches':checked,
        'human_source_claim_review_verified':False,
        'browser_accessibility_print_qa_verified':False,
        'all_41_exports_independently_approved':False,
        'publication_authorized':False,
        'independent_qd_pass':False,
        'medical_safety_verified':False,
        'privacy_verified':False,
        'merchant_approved':False,
        'paid_orders_verified':False,
        'net_revenue_per_1000_qualified_sessions':None,
    }


def run(root:Path)->dict:
    for rel,want in ((UPSTREAM,UPSTREAM_OID),(CUSTODY,CUSTODY_OID)):
        if not safe_file(root,rel) or blob((root/rel).read_bytes())!=want:
            raise ValueError('PINNED_PREDECESSOR_OR_CUSTODY_MISSING_OR_CHANGED:'+rel)
    spec=importlib.util.spec_from_file_location('fv_r305_pinned_r304',root/UPSTREAM)
    if spec is None or spec.loader is None:raise RuntimeError('PINNED_R304_IMPORT_UNAVAILABLE')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    data=json.loads((root/CUSTODY).read_bytes())
    local=audit(root,data)
    if local['errors']:return local
    return audit(root,data,mod.run(root))


def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    a=p.parse_args(argv)
    try:result=run(a.repo_root)
    except (OSError,UnicodeError,ValueError,RuntimeError,TypeError,KeyError,ImportError) as exc:
        result={'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_REPOSITORY_OR_BUILD_UNAVAILABLE:'+type(exc).__name__],
                'publication_authorized':False,'independent_qd_pass':False,'medical_safety_verified':False,
                'all_41_exports_independently_approved':False}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
