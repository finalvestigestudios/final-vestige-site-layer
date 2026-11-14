#!/usr/bin/env python3
"""R364: read-only, exact-Git-ref Preparedness 41-document integration firewall.

Compares original authored material against a candidate without checkout mutations.
No output can authorize publication, safety/QD review, or revenue claims.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

SCHEMA = 'fv-preparedness-r364-exact-ref-release-firewall-v1'
ORIGINAL = '02d344d9c1a1e9f68a2bcd6c0ab03859acf78232'
CITE = re.compile(r'\{\{cite:([a-z][a-z0-9-]*)\}\}')
ANY_CITE = re.compile(r'\{\{cite:')
SAFE_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
REQUIRED_QA_GATES = frozenset(('household-emergency-plan', 'three-day-kit',
                               'go-bags', 'preparedness-real-households'))
UNCLEARED_APPROVALS = frozenset(('making-water-safer', 'salt-beef-salt-pork-age-of-sail'))
SOURCE_FILES = ('register.json','fragments/food.json','fragments/health.json',
                'fragments/hist-field.json','fragments/hist-food.json',
                'fragments/hist-home.json','fragments/shelter.json','fragments/start.json',
                'crosswalk.json')
DENY = dict(qd_pass=False, may_merge=False, may_publish=False,
            safety_verified=False, medical_safety_verified=False,
            source_approval=False, sale_verified=False, revenue_verified=False)

class WordsAndAnchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.words = []
        self.ids = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'a' and 'href' in a: self.links.append(a['href'])
    def handle_data(self, data):
        self.words.extend(re.findall(r"\b[\w'-]+\b", data, flags=re.UNICODE))

def parse_html(body):
    if not isinstance(body, str) or len(body) > 500_000:
        raise ValueError('INVALID_BODY')
    obj = WordsAndAnchors(); obj.feed(body); obj.close()
    return obj

def pairs(values):
    result = {}
    for k, v in values:
        if k in result: raise ValueError('DUPLICATE_JSON_KEY:'+k)
        result[k] = v
    return result

def load_json(raw):
    return json.loads(raw, object_pairs_hook=pairs)

def compare_doc(kind, original, candidate, old_html, new_html):
    """(errors, human review, evidence) preserving *per-ID* citation custody."""
    errors, review = set(), set()
    if not isinstance(original, dict) or not isinstance(candidate, dict):
        return ['INVALID_METADATA'], [], {}
    slug = original.get('slug')
    if not isinstance(slug, str) or not SAFE_SLUG.fullmatch(slug) or candidate.get('slug') != slug:
        return ['SLUG_DRIFT'], [], {}
    if original.get('n') != candidate.get('n') or original.get('kind') != candidate.get('kind'):
        errors.add('IDENTITY_DRIFT')
    for label, meta in [('ORIGINAL', original), ('CANDIDATE', candidate)]:
        st = meta.get('status')
        if not isinstance(st, dict) or st.get('publish') != 'draft':
            errors.add(label+'_PUBLICATION_STATE')
        sr = meta.get('safety_review')
        if not isinstance(sr, dict) or sr.get('state') not in ('pending','approved','not-required'):
            errors.add(label+'_INVALID_SAFETY_STATE')
    if isinstance(original.get('status'),dict) and isinstance(candidate.get('status'),dict):
        if original['status'].get('editorial') != candidate['status'].get('editorial'):
            errors.add('EDITORIAL_STATUS_DRIFT')
    osr = original.get('safety_review', {})
    csr = candidate.get('safety_review', {})
    if isinstance(osr,dict) and isinstance(csr,dict):
        if osr.get('state') != csr.get('state'):
            errors.add('SAFETY_STATE_CHANGED_WITHOUT_QD_PROOF')
        if (osr.get('reviewer'),osr.get('date'),osr.get('scope')) != (
              csr.get('reviewer'),csr.get('date'),csr.get('scope')):
            review.add('SAFETY_REVIEW_EVIDENCE_CHANGED')
        if osr.get('state') != 'pending': review.add('ORIGINAL_NONPENDING_SAFETY_STATE_REQUIRES_QD')
    if slug in UNCLEARED_APPROVALS:
        review.add('FOUNDER_CHAT_APPROVAL_NOT_INDEPENDENT_SAFETY_REVIEW')
        scope = str(osr.get('scope','')) if isinstance(osr, dict) else ''
        if 'NOT an independent safety' not in scope and 'NOT an independent' not in scope:
            errors.add('MISSING_ORIGINAL_APPROVAL_CAVEAT')
    if original.get('track') != candidate.get('track') or original.get('section') != candidate.get('section'):
        errors.add('CONTENT_CLASSIFICATION_DRIFT')
    for k in ('source_use', 'related'):
        if not isinstance(original.get(k), (dict if k=='source_use' else list)) or not isinstance(candidate.get(k), (dict if k=='source_use' else list)):
            errors.add('INVALID_'+k.upper())
    if isinstance(original.get('related'),list) and isinstance(candidate.get('related'),list):
        if any(x not in candidate['related'] for x in original['related']):
            errors.add('RELATED_RESOURCE_REMOVED')
        if any(x not in original['related'] for x in candidate['related']):
            review.add('RELATED_RESOURCE_ADDED_RECHECK')
    old_use = original.get('source_use') if isinstance(original.get('source_use'),dict) else {}
    new_use = candidate.get('source_use') if isinstance(candidate.get('source_use'),dict) else {}
    for sid, desc in old_use.items():
        if sid not in new_use: errors.add('SOURCE_USE_REMOVED:'+str(sid))
        elif desc != new_use[sid]: review.add('SOURCE_READING_SCOPE_EDIT:'+str(sid))
    for sid in new_use.keys()-old_use.keys(): review.add('NEW_SOURCE_REQUIRES_REGISTRATION:'+str(sid))
    try:
        a, b = parse_html(old_html), parse_html(new_html)
    except (TypeError, ValueError) as exc:
        return sorted(errors|{'INVALID_HTML:'+str(exc)}), sorted(review), {}
    ac = Counter(CITE.findall(old_html)); bc = Counter(CITE.findall(new_html))
    if len(CITE.findall(old_html)) != len(ANY_CITE.findall(old_html)):
        errors.add('MALFORMED_ORIGINAL_CITATION')
    if len(CITE.findall(new_html)) != len(ANY_CITE.findall(new_html)):
        errors.add('MALFORMED_CANDIDATE_CITATION')
    if set(ac)-set(old_use): errors.add('ORIGINAL_CITATION_UNDECLARED')
    if set(bc)-set(new_use): errors.add('CANDIDATE_CITATION_UNDECLARED')
    for sid, n in ac.items():
        if bc[sid] < n: errors.add('CITATION_OCCURRENCE_LOST:'+sid)
    if bc-ac: review.add('ADDED_CITATION_OCCURRENCES_RECHECK')
    if len(a.ids) != len(set(a.ids)) or len(b.ids) != len(set(b.ids)):
        errors.add('DUPLICATE_HEADING_ID')
    if set(a.ids)-set(b.ids): errors.add('ORIGINAL_ANCHOR_REMOVED')
    if len(b.words) < len(a.words):
        review.add('READING_DEPTH_REVIEW')
        if len(a.words) and len(b.words)/len(a.words) < 0.95:
            errors.add('SUBSTANTIAL_READING_DEPTH_LOSS')
    if len(set(a.links)-set(b.links)):
        review.add('ORIGINAL_LINK_REMOVED_REVIEW')
    if not isinstance(candidate.get('source_use'),dict):
        errors.add('MISSING_CANDIDATE_SOURCES')
    return sorted(errors), sorted(review), dict(
        kind=kind, slug=slug, original_words=len(a.words), candidate_words=len(b.words),
        original_citations=sum(ac.values()), candidate_citations=sum(bc.values()),
        original_source_ids=len(ac), candidate_source_ids=len(bc),
        original_anchors=len(a.ids), candidate_anchors=len(b.ids),
        original_sha256=hashlib.sha256(old_html.encode()).hexdigest(),
        candidate_sha256=hashlib.sha256(new_html.encode()).hexdigest())

def compare_taxonomy(old, new):
    errors, review = set(), set()
    if not isinstance(old,dict) or not isinstance(new,dict):
        return ['TAXONOMY_INVALID'], []
    a, b = old.get('slate'), new.get('slate')
    if not isinstance(a,list) or not isinstance(b,list) or len(a)!=35 or len(b)!=35:
        return ['SLATE_NOT_35'], []
    def index(rows):
        out={}
        for r in rows:
            if not isinstance(r,dict) or not isinstance(r.get('slug'),str) or r['slug'] in out:
                raise ValueError('DUPLICATE_OR_BAD_SLUG')
            out[r['slug']]=r
        return out
    try: ao, bo = index(a), index(b)
    except ValueError: return ['DUPLICATE_OR_BAD_SLUG'], []
    if set(ao)!=set(bo): errors.add('SLATE_IDENTITY_CHANGE')
    for slug, r in ao.items():
        s = bo.get(slug)
        if s is None: continue
        if r.get('n')!=s.get('n') or r.get('section')!=s.get('section'):
            errors.add('SLATE_NUMBER_OR_SECTION_DRIFT:'+slug)
        if r.get('gate') is True and s.get('gate') is not True:
            errors.add('SAFETY_GATE_WEAKENED:'+slug)
        if slug in REQUIRED_QA_GATES and s.get('gate') is not True:
            errors.add('INDEPENDENT_QA_GATE_DROPPED:'+slug)
        if r.get('gate') is False and s.get('gate') is True:
            review.add('SAFETY_GATE_STRENGTHENED:'+slug)
    if old.get('base_path') != '/preparedness/' or new.get('base_path') != '/preparedness/':
        errors.add('CANONICAL_BASE_PATH_CHANGED')
    return sorted(errors),sorted(review)

def result(errors, review=(), dockets=(), evidence=None):
    return dict(schema=SCHEMA,
      status='INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
      errors=sorted(set(errors)), human_review=sorted(set(review)),
      dockets=list(dockets), evidence=evidence or {}, **DENY)

def run_git(root, *args):
    env = {**os.environ,'GIT_OPTIONAL_LOCKS':'0', 'GIT_TERMINAL_PROMPT':'0'}
    r = subprocess.run(['git','-C',str(root),*args], capture_output=True,
                       text=False, timeout=35, env=env, check=False)
    if r.returncode != 0: raise ValueError('GIT_OBJECT_NOT_AVAILABLE')
    if len(r.stdout)>3_000_000: raise ValueError('GIT_RESPONSE_OVERSIZED')
    return r.stdout

def audit(root, candidate_ref):
    root=Path(root)
    if root.is_symlink() or not (root/'.git').exists():
        return result(['AUTHENTIC_GIT_CHECKOUT_REQUIRED'])
    if (not isinstance(candidate_ref,str) or not re.fullmatch(r'[a-zA-Z0-9_./-]{1,120}',candidate_ref)
        or candidate_ref.startswith('-') or '..' in candidate_ref or candidate_ref.startswith('/')):
        return result(['INVALID_CANDIDATE_REF'])
    try:
        old_sha = run_git(root,'rev-parse','--verify',ORIGINAL+'^{commit}').decode().strip()
        new_sha = run_git(root,'rev-parse','--verify',candidate_ref+'^{commit}').decode().strip()
        if old_sha!=ORIGINAL: raise ValueError('ORIGINAL_COMMIT_DRIFT')
        old_paths=run_git(root,'ls-tree','-r','--name-only',ORIGINAL,'--','preparedness/content').decode().splitlines()
        new_paths=run_git(root,'ls-tree','-r','--name-only',new_sha,'--','preparedness/content').decode().splitlines()
        wanted=lambda ps,kind: sorted(p for p in ps if p.startswith('preparedness/content/'+kind+'/') and p.endswith('.meta.json'))
        olda, oldt = wanted(old_paths,'articles'),wanted(old_paths,'tools')
        newa, newt = wanted(new_paths,'articles'),wanted(new_paths,'tools')
        if len(olda)!=35 or len(oldt)!=6 or olda!=newa or oldt!=newt:
            return result(['41_DOCUMENT_IDENTITY_OR_COUNT_DRIFT'])
        errors,review,dockets=[],[],[]
        def read(ref,path): return run_git(root,'show',ref+':'+path).decode('utf-8')
        for path in olda+oldt:
            kind='article' if '/articles/' in path else 'tool'
            bp=path[:-10]+'.body.html'
            o=load_json(read(ORIGINAL,path)); c=load_json(read(new_sha,path))
            e,h,d=compare_doc(kind,o,c,read(ORIGINAL,bp),read(new_sha,bp))
            errors += [o.get('slug','?')+':'+z for z in e]
            review += [o.get('slug','?')+':'+z for z in h]
            dockets.append(d)
        oe=load_json(read(ORIGINAL,'preparedness/taxonomy.json'))
        ce=load_json(read(new_sha,'preparedness/taxonomy.json'))
        e,h=compare_taxonomy(oe,ce); errors+=e;review+=h
        for src in SOURCE_FILES:
            p='preparedness/sources/'+src
            if run_git(root,'rev-parse',ORIGINAL+':'+p)!=run_git(root,'rev-parse',new_sha+':'+p):
                errors.append('SOURCE_CORPUS_CHANGED_WITHOUT_QD:'+src)
        if len(dockets)!=41: errors.append('INCOMPLETE_DOCUMENT_DOCKET')
        return result(errors,review,dockets,{'original_commit':old_sha,
          'candidate_commit':new_sha,'articles':35,'tools':6,'total':len(dockets),
          'original_source_files':len(SOURCE_FILES),'qualified_review_executed':False})
    except (OSError,ValueError,TypeError,KeyError,UnicodeError,subprocess.TimeoutExpired) as exc:
        return result(['GIT_OR_SOURCE_INTEGRITY_UNAVAILABLE:'+type(exc).__name__])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--candidate-ref',default='HEAD')
    args=p.parse_args()
    print(json.dumps(audit(args.repo_root,args.candidate_ref),sort_keys=True,indent=2))
    raise SystemExit(2)
