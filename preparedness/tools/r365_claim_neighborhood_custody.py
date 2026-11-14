#!/usr/bin/env python3
"""R365: citation-to-claim custody across 41 Preparedness source drafts.

Read-only admission evidence; this tool does not approve QD, safety, publishing,
merchant acceptance, social attribution, or any live change. A citation remaining
in the document is NOT enough if it migrates to an unrelated assertion.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r365-claim-neighborhood-v1'
ORIGINAL = '02d344d9c1a1e9f68a2bcd6c0ab03859acf78232'
CITE = re.compile(r'\{\{cite:([a-z][a-z0-9-]*)\}\}')
ANY_CITE = re.compile(r'\{\{cite:')
WORD = re.compile(r"[a-z0-9]+(?:['-][a-z0-9]+)?", re.I)
BLOCK = frozenset(('p','li','h1','h2','h3','h4','h5','h6','blockquote','td','th','figcaption'))
HIDE = frozenset(('script', 'style', 'template'))
POLARITY = frozenset(('not','never','no','only','must','cannot','can','always','immediately',
                      'avoid','do','safe','unsafe','required','optional','should','shouldnt',
                      'may','maynot','dangerous','emergency','call','wait'))
HOLD = {'qd_pass':False,'may_merge':False,'may_publish':False,
        'safety_verified':False,'source_verified':False,
        'merchant_verified':False,'sale_verified':False,
        'net_revenue_verified':False}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def words(text):
    return WORD.findall(text.lower())


def common(a,b):
    a=set(words(a)); b=set(words(b))
    if not a and not b: return 1.0
    return len(a & b) / len(a | b) if a | b else 0.0


class Blocks(HTMLParser):
    """Collect leaf-block claims with source tokens; never interpret hidden scripts."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.open = []
        self.blocks = []
        self.fallback = []
        self.hidden = 0
        self.hidden_citations = []
        self.current_heading = 'body'
        self.problems = []

    def handle_starttag(self,tag,attrs):
        tag=tag.lower()
        if tag in HIDE: self.hidden += 1
        if tag in BLOCK: self.open.append({'tag':tag,'text':[], 'heading':self.current_heading})
        for name,value in attrs:
            if isinstance(value,str) and ANY_CITE.search(value):
                self.problems.append('CITATION_IN_HTML_ATTRIBUTE')

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag in HIDE or tag in BLOCK: self.handle_endtag(tag)

    def handle_data(self,text):
        if self.hidden:
            if ANY_CITE.search(text): self.hidden_citations.append(text)
            return
        if self.open: self.open[-1]['text'].append(text)
        elif text.strip(): self.fallback.append(text)

    def handle_endtag(self,tag):
        tag=tag.lower()
        if tag in HIDE:
            self.hidden=max(0,self.hidden-1)
        if tag in BLOCK:
            if not self.open or self.open[-1]['tag']!=tag:
                self.problems.append('UNBALANCED_CLAIM_BLOCK')
                return
            block=self.open.pop()
            full=' '.join(block['text']).strip()
            heading=block['heading']
            if tag.startswith('h') and len(tag)==2 and tag[1].isdigit():
                self.current_heading=' '.join(words(CITE.sub('',full)))[:180] or 'untitled'
            self.blocks.append({'text':full,'heading':heading,'tag':tag})
            if self.open and self.open[-1]['tag'] not in ('blockquote','li'):
                self.open[-1]['text'].append(' ')

    def complete(self,html):
        self.feed(html); self.close()
        if self.open: self.problems.append('UNCLOSED_CLAIM_BLOCK')
        if self.hidden_citations: self.problems.append('HIDDEN_SCRIPT_CITATION')
        if self.fallback: self.blocks.append({'text':' '.join(self.fallback),'heading':'unscoped','tag':'unscoped'})
        return self


def occurrences(body):
    if not isinstance(body,str) or len(body)>500_000: raise ValueError('INVALID_HTML')
    obj=Blocks().complete(body)
    found=[]
    for n,block in enumerate(obj.blocks):
        plain=' '.join(words(CITE.sub('',block['text'])))
        for match in CITE.finditer(block['text']):
            found.append({'id':match.group(1), 'block':n, 'tag':block['tag'],
                'heading':block['heading'], 'claim':plain,
                'claim_sha256':sha(plain),
                'polarity':sorted(set(words(plain)) & POLARITY)})
    raw=CITE.findall(body)
    errors=set(obj.problems)
    if len(ANY_CITE.findall(body)) != len(raw): errors.add('MALFORMED_CITATION_TOKEN')
    if Counter(x['id'] for x in found) != Counter(raw): errors.add('UNSCOPED_OR_HIDDEN_CITATION')
    return found, sorted(errors)


def compare(old_meta,new_meta,old_body,new_body):
    """Thematic changes are human-review evidence, NOT implied source approval."""
    errors,review=set(),set()
    if not isinstance(old_meta,dict) or not isinstance(new_meta,dict):
        return ['INVALID_META'], [], {}
    slug=old_meta.get('slug')
    if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) or new_meta.get('slug')!=slug:
        return ['SLUG_DRIFT'], [], {}
    if old_meta.get('n')!=new_meta.get('n') or old_meta.get('kind')!=new_meta.get('kind'):
        errors.add('DOCUMENT_IDENTITY_DRIFT')
    for label,meta in (('OLD',old_meta),('NEW',new_meta)):
        st=meta.get('status'); safety=meta.get('safety_review')
        if not isinstance(st,dict) or st.get('publish')!='draft': errors.add(label+'_NOT_DRAFT')
        if not isinstance(safety,dict) or safety.get('state') not in ('pending','approved','not-required'):
            errors.add(label+'_INVALID_SAFETY')
        uses=meta.get('source_use')
        if not isinstance(uses,dict) or not all(isinstance(k,str) and isinstance(v,str) and v.strip() for k,v in uses.items()):
            errors.add(label+'_INVALID_SOURCE_USE')
    a=old_meta.get('source_use') if isinstance(old_meta.get('source_use'),dict) else {}
    b=new_meta.get('source_use') if isinstance(new_meta.get('source_use'),dict) else {}
    for k in a:
        if k not in b: errors.add('SOURCE_BINDING_REMOVED:'+k)
        elif a[k]!=b[k]: review.add('SOURCE_SCOPE_CHANGED:'+k)
    for k in b.keys()-a.keys(): review.add('NEW_SOURCE_REVIEW:'+k)
    try: old,oe=occurrences(old_body); new,ne=occurrences(new_body)
    except (TypeError,ValueError): return ['INVALID_BODY'], sorted(review), {}
    errors.update('OLD_'+x for x in oe); errors.update('NEW_'+x for x in ne)
    ac=Counter(x['id'] for x in old); bc=Counter(x['id'] for x in new)
    for sid in ac:
        if bc[sid]<ac[sid]: errors.add('CITATION_COUNT_LOST:'+sid)
    for sid in bc:
        if sid not in b: errors.add('UNDECLARED_CITATION:'+sid)
    for sid in ac:
        if sid not in a: errors.add('ORIGINAL_UNDECLARED_CITATION:'+sid)
    docket=[]
    for sid in sorted(ac.keys() | bc.keys()):
        old_items=[x for x in old if x['id']==sid]
        pool=[x for x in new if x['id']==sid]
        for entry in old_items:
            if not pool:
                docket.append({'source_id':sid,'outcome':'LOST','original_claim_sha256':entry['claim_sha256']})
                continue
            exact=next((i for i,p in enumerate(pool) if p['claim_sha256']==entry['claim_sha256']),None)
            i=exact if exact is not None else max(range(len(pool)),key=lambda j:common(entry['claim'],pool[j]['claim']))
            chosen=pool.pop(i)
            score=common(entry['claim'],chosen['claim'])
            outcome='EXACT' if entry['claim_sha256']==chosen['claim_sha256'] else 'EDIT_REVIEW'
            if outcome!='EXACT':
                review.add('CITATION_CLAIM_CHANGED:'+sid)
                if score<0.18:
                    errors.add('CITATION_REASSIGNED_UNRELATED_CLAIM:'+sid)
                    outcome='UNRELATED_HARD_HOLD'
                if entry['polarity']!=chosen['polarity']:
                    review.add('SAFETY_MODALITY_CHANGED:'+sid)
            if entry['heading']!=chosen['heading']:
                review.add('CITATION_SECTION_CHANGED:'+sid)
            docket.append({'source_id':sid,'outcome':outcome,
              'original_claim_sha256':entry['claim_sha256'],'candidate_claim_sha256':chosen['claim_sha256'],
              'shared_word_ratio':round(score,3),'old_heading':entry['heading'],
              'new_heading':chosen['heading']})
        for entry in pool: review.add('NEW_CITATION_OCCURRENCE_REVIEW:'+sid)
    return sorted(errors),sorted(review), {'slug':slug, 'original_citations':sum(ac.values()),
        'candidate_citations':sum(bc.values()),'claim_matches':docket,
        'original_body_sha256':sha(old_body),'candidate_body_sha256':sha(new_body)}


def report(errors,review=(),dockets=(),evidence=None):
    return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
       'errors':sorted(set(errors)),'human_review':sorted(set(review)),
       'dockets':list(dockets),'evidence':evidence or {}, **HOLD}


def git(root,*args):
    env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}
    out=subprocess.run(['git','-C',str(root),*args],capture_output=True,timeout=35,env=env)
    if out.returncode: raise ValueError('GIT_OBJECT_NOT_AVAILABLE')
    if len(out.stdout)>3_000_000: raise ValueError('GIT_OBJECT_TOO_LARGE')
    return out.stdout.decode('utf-8')


def load_json(raw):
    def unique(items):
        obj={}
        for k,v in items:
            if k in obj: raise ValueError('DUPLICATE_JSON_KEY')
            obj[k]=v
        return obj
    return json.loads(raw, object_pairs_hook=unique)


def audit(root,candidate_ref='HEAD'):
    root=Path(root)
    if root.is_symlink() or not (root/'.git').exists(): return report(['AUTHENTIC_CHECKOUT_REQUIRED'])
    if not isinstance(candidate_ref,str) or not re.fullmatch(r'[a-zA-Z0-9_./-]{1,120}',candidate_ref) or '..' in candidate_ref or candidate_ref.startswith('-'):
        return report(['UNSAFE_REF'])
    try:
        orig=git(root,'rev-parse','--verify',ORIGINAL+'^{commit}').strip()
        candidate=git(root,'rev-parse','--verify',candidate_ref+'^{commit}').strip()
        if orig!=ORIGINAL: raise ValueError('PINNED_ORIGINAL_MISMATCH')
        old_paths=git(root,'ls-tree','-r','--name-only',ORIGINAL,'--','preparedness/content').splitlines()
        new_paths=git(root,'ls-tree','-r','--name-only',candidate,'--','preparedness/content').splitlines()
        meta_paths=lambda paths,kind:sorted(p for p in paths if p.startswith('preparedness/content/'+kind+'/') and p.endswith('.meta.json'))
        paths=meta_paths(old_paths,'articles')+meta_paths(old_paths,'tools')
        if len(meta_paths(old_paths,'articles'))!=35 or len(meta_paths(old_paths,'tools'))!=6 or paths!=meta_paths(new_paths,'articles')+meta_paths(new_paths,'tools'):
            return report(['41_DOCUMENT_CLOSURE_CHANGED'])
        errors=[]; review=[]; dockets=[]
        for path in paths:
            bp=path[:-10]+'.body.html'
            read=lambda ref,p:git(root,'show',ref+':'+p)
            e,r,d=compare(load_json(read(ORIGINAL,path)),load_json(read(candidate,path)),
                          read(ORIGINAL,bp),read(candidate,bp))
            errors.extend(path+':'+x for x in e)
            review.extend(path+':'+x for x in r)
            dockets.append(d)
        if len(dockets)!=41: errors.append('INCOMPLETE_EVIDENCE_DOCKET')
        return report(errors,review,dockets,{'original_commit':orig,'candidate_commit':candidate,
             'authored_articles':35,'authored_tools':6,'source_review_executed':False})
    except (OSError,ValueError,TypeError,UnicodeError,subprocess.TimeoutExpired,KeyError) as exc:
        return report(['NATIVE_SOURCE_UNAVAILABLE:'+type(exc).__name__])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--candidate-ref',default='HEAD')
    args=p.parse_args()
    print(json.dumps(audit(args.repo_root,args.candidate_ref),sort_keys=True,indent=2))
    raise SystemExit(2)
