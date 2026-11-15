"""R383 Preparedness citation-delivery context / concealment audit.

Read-only, immutable original manuscript variants. Static evidence is never qualified
source/safety review, real CSS/browser accessibility, or publication permission.
"""
from __future__ import annotations
import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

MANIFEST = '5e7d9a8972872c82b4bc46ac13aab18883d8149a'
REGISTER = 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'
TOKEN = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SHA = re.compile(r'[a-f0-9]{40}\Z')
ARTICLE = re.compile(r'preparedness/content/articles/([a-z0-9-]+)\.(body\.html|meta\.json)\Z')
CONTEXT = {'p','li','td','th','blockquote','figcaption','dt','dd','h1','h2','h3','h4','h5','h6'}
INTERACTIVE = {'button','select','option','textarea','form','input','label','summary','nav'}
UNKNOWN_RENDER = {'noscript','template','canvas','svg','iframe','object'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


def style_risks(style: str) -> list[str]:
    """Detect extra literal inline hiding; external CSS remains unknowable."""
    s = re.sub(r'/\*.*?\*/','',style or '',flags=re.S).lower()
    d = {}
    for item in s.split(';'):
        if ':' in item:
            k,v = item.split(':',1)
            d[k.strip()] = re.sub(r'\s+','',v).replace('!important','')
    hits = []
    for prop, values in {
        'display': {'none'}, 'visibility': {'hidden','collapse'},
        'content-visibility': {'hidden'}, 'opacity': {'0','0.0','0.00'},
        'font-size': {'0','0px','0pt','0em','0rem','0%'},
        'transform': {'scale(0)','scale(0,0)'},
        'clip-path': {'inset(100%)','circle(0)'},
    }.items():
        if d.get(prop) in values: hits.append(prop.upper().replace('-','_'))
    if d.get('overflow')=='hidden' and (d.get('height') in {'0','0px'} or d.get('width') in {'0','0px'}):
        hits.append('ZERO_SIZE_OVERFLOW')
    if d.get('position')=='absolute' and re.fullmatch(r'-\d{4,}px',d.get('left','')):
        hits.append('OFFSCREEN_POSITION')
    return hits


class DeliveryParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.blocks = []
        self.citations = []
        self.comments = []
        self.fragments = []
        self._block_id = 0

    def handle_starttag(self,tag,attrs):
        a = dict(attrs)
        parent = self.stack[-1] if self.stack else None
        blockers = (parent['blockers'] if parent else ()) + tuple(style_risks(a.get('style') or ''))
        if 'hidden' in a or 'inert' in a or (a.get('aria-hidden') or '').lower() == 'true':
            blockers += ('ATTRIBUTE_HIDDEN',)
        if tag in {'script','style','head'} or tag in UNKNOWN_RENDER:
            blockers += ('NON_READER_REGION',)
        if tag in INTERACTIVE: blockers += ('INTERACTIVE_CONTROL',)
        if tag == 'a': blockers += ('LINK_TEXT_CITATION',)
        if '{{cite:' in (self.get_starttag_text() or ''): self.fragments.append('ATTRIBUTE_CITATION')
        block = parent['block'] if parent else None
        if tag in CONTEXT:
            self._block_id += 1
            block = {'id':self._block_id,'text':[],'citations':[],'tag':tag}
            self.blocks.append(block)
        if tag not in VOID:
            self.stack.append({'tag':tag,'block':block,'blockers':blockers})

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID: self.stack.pop()

    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag:
                del self.stack[i:]
                return

    def handle_data(self,data):
        f = self.stack[-1] if self.stack else None
        block = f['block'] if f else None
        for match in TOKEN.finditer(data):
            event = {'id':match.group(1),'block':block['id'] if block else None,
                     'blockers':tuple(sorted(set(f['blockers'] if f else ())))}
            self.citations.append(event)
            if block: block['citations'].append(match.group(1))
        if block: block['text'].append(TOKEN.sub('',data))

    def handle_comment(self,data):
        if '{{cite:' in data: self.comments.append('COMMENT_CITATION')


def examine(body: bytes, meta: dict, known_ids: set[str]) -> dict:
    errors=[]; warnings=['EXTERNAL_CSS_JS_BROWSER_SCREENREADER_AND_PRINT_UNVERIFIED']
    try: raw=body.decode('utf-8')
    except (AttributeError,UnicodeError): raw=''; errors.append('BODY_UTF8_INVALID')
    if not isinstance(meta,dict): meta={}; errors.append('METADATA_INVALID')
    if not isinstance(meta.get('status'),dict) or meta['status'].get('publish')!='draft':
        errors.append('NOT_DRAFT')
    safety=meta.get('safety_review')
    if not isinstance(safety,dict) or safety.get('state') not in {'pending','approved','not-required'}:
        errors.append('HISTORICAL_SAFETY_STATE_INVALID')
    if isinstance(safety,dict) and safety.get('state')=='approved':
        warnings.append('HISTORICAL_LABEL_NOT_INDEPENDENT_QD')
    scopes=meta.get('source_use')
    if not isinstance(scopes,dict): scopes={}; errors.append('SOURCE_USE_INVALID')
    p=DeliveryParser()
    try: p.feed(raw); p.close()
    except (ValueError,AssertionError,TypeError): errors.append('HTML_PARSE_FAILURE')
    original=TOKEN.findall(raw)
    if raw.count('{{cite:')!=len(original): errors.append('INVALID_LITERAL_CITATION')
    if len(original)!=len(p.citations): errors.append('CITATION_NOT_READER_DATA')
    if p.comments or p.fragments: errors.append('CITATION_IN_NONCONTENT')
    rendered=unescape(raw)
    if len(TOKEN.findall(rendered))!=len(original): errors.append('ENTITY_ESCAPED_CITATION')
    for c in p.citations:
        if c['block'] is None: errors.append('CITATION_OUTSIDE_CLAIM_BLOCK')
        for reason in c['blockers']: errors.append('CITATION_'+reason)
    for sid in sorted(set(original)):
        if sid not in known_ids: errors.append('UNKNOWN_SOURCE:'+sid)
        if not isinstance(scopes.get(sid),str) or not scopes[sid].strip():
            errors.append('MISSING_SOURCE_USE:'+sid)
    for b in p.blocks:
        if not b['citations']: continue
        claim = re.sub(r'\s+',' ',''.join(b['text'])).strip()
        if len(claim)<18: errors.append('CITATION_WITHOUT_SUBSTANTIVE_CLAIM:'+str(b['id']))
        if len(set(b['citations']))<len(b['citations']):
            warnings.append('REPEATED_SOURCE_WITHIN_CLAIM:'+str(b['id']))
    return {'status':'INVALID_HARD_HOLD' if errors else 'STATIC_DELIVERY_REVIEW_HARD_HOLD',
            'errors':sorted(set(errors)), 'warnings':sorted(set(warnings)),
            'citations':len(original),'claim_blocks_with_citations':sum(bool(b['citations']) for b in p.blocks),
            'historical_safety_state':safety.get('state') if isinstance(safety,dict) else None,
            'publication_approved':False,'qualified_safety_approved':False,
            'verified_human_source':False}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data,usedforsecurity=False).hexdigest()


def collect_source_ids(register: dict, objects: dict, read) -> set[str]:
    """Resolve BASE plus all seven original contributor source fragments, without choosing a fork."""
    base=register.get('sources')
    if not isinstance(base,list): raise ValueError('BASE_SOURCE_REGISTRY_INVALID')
    ids=set()
    for src in base:
        if not isinstance(src,dict) or not isinstance(src.get('id'),str):
            raise ValueError('BASE_SOURCE_ID_INVALID')
        if src['id'] in ids: raise ValueError('BASE_DUPLICATE_SOURCE_ID')
        ids.add(src['id'])
    for path,obj in objects.items():
        if not path.startswith('preparedness/sources/fragments/'): continue
        for variant in obj['variants']:
            document=json.loads(read(variant['sha']))
            rows=document.get('sources')
            if not isinstance(rows,list): raise ValueError('FRAGMENT_SOURCES_INVALID')
            local=set()
            for src in rows:
                if not isinstance(src,dict) or not isinstance(src.get('id'),str):
                    raise ValueError('FRAGMENT_SOURCE_ID_INVALID')
                if src['id'] in local: raise ValueError('FRAGMENT_DUPLICATE_SOURCE_ID')
                local.add(src['id'])
            ids.update(local)
    return ids



def audit(manifest: dict, register: dict, reader) -> dict:
    """Read every original article variation from pinned Git objects; no selection."""
    if not isinstance(manifest,dict) or not isinstance(register,dict):
        return {'status':'INVALID_HARD_HOLD','errors':['UNTRUSTED_INPUT'],'publication_approved':False}
    objs=manifest.get('objects',[]); pins=manifest.get('branch_pins',[])
    if (manifest.get('release_state')!='DRAFT_HARD_HOLD' or manifest.get('article_count')!=35
        or manifest.get('conflict_count')!=9 or len(pins)!=9 or len(objs)!=77):
        return {'status':'INVALID_HARD_HOLD','errors':['ORIGINAL_MANIFEST_DRIFT'],'publication_approved':False}
    bypath={o['path']:o for o in objs}
    bodies={p[:-10]:v for p,v in bypath.items() if p.endswith('.body.html')}
    metas={p[:-10]:v for p,v in bypath.items() if p.endswith('.meta.json')}
    if len(bodies)!=35 or set(bodies)!=set(metas) or any(x.get('selected_sha') is not None for x in objs):
        return {'status':'INVALID_HARD_HOLD','errors':['ARTICLE_PAIR_OR_FORK_DRIFT'],'publication_approved':False}
    rows=[]; errors=[]
    def read(sha):
        if not isinstance(sha,str) or not SHA.fullmatch(sha): raise ValueError('BAD_SHA')
        raw=reader(sha)
        if not isinstance(raw,bytes) or git_blob(raw)!=sha: raise ValueError('GIT_BLOB_MISMATCH')
        return raw
    try: ids=collect_source_ids(register,bypath,read)
    except (ValueError,KeyError,TypeError,UnicodeError):
        return {'status':'INVALID_HARD_HOLD','errors':['SOURCE_REGISTRY_OR_FRAGMENT_INTEGRITY'],'publication_approved':False}
    for prefix,obj in sorted(bodies.items()):
        branchmeta={v['branch']:v['sha'] for v in metas[prefix]['variants']}
        if {v['branch'] for v in obj['variants']}!=set(branchmeta):
            errors.append('UNPAIRED_BRANCH:'+prefix)
        for v in obj['variants']:
            try:
                md=json.loads(read(branchmeta[v['branch']]))
                d=examine(read(v['sha']),md,ids)
                d.update({'article':prefix,'branch':v['branch'],'body_blob':v['sha'],'meta_blob':branchmeta[v['branch']]})
                rows.append(d)
            except (ValueError,KeyError,TypeError,UnicodeError):
                errors.append('READ_FAILED:'+prefix)
    return {'status':'INVALID_HARD_HOLD' if errors or any(d['errors'] for d in rows) else 'STATIC_DELIVERY_REVIEW_HARD_HOLD',
            'article_count':len(bodies),'variants_checked':len(rows),'errors':errors,
            'review_rows':rows,'publication_approved':False,'qualified_safety_approved':False}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',default='.')
    args=ap.parse_args(); root=Path(args.repo)
    def reader(sha):
        return subprocess.run(['git','-C',str(root),'cat-file','blob',sha],capture_output=True,check=True,timeout=20).stdout
    try: result=audit(json.loads(reader(MANIFEST)),json.loads(reader(REGISTER)),reader)
    except (subprocess.SubprocessError,OSError,ValueError,TypeError,KeyError):
        result={'status':'INVALID_HARD_HOLD','errors':['FULL_AUTHENTIC_GIT_OBJECTS_UNAVAILABLE'],'publication_approved':False}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__': raise SystemExit(main())
