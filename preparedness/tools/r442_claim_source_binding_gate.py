#!/usr/bin/env python3
"""R442 read-only citation claim / original-source variant custody.

A clean structural comparison is NOT permission to publish, approve hazardous advice,
or activate commerce.  The baseline must be independently reviewed and frozen; this
program cannot create its own trust anchor.  No I/O except bounded local reads.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

DRAFT = 'DRAFT_HARD_HOLD'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
BLOCKS = {'p','li','h1','h2','h3','h4','h5','h6','td','th','blockquote','figcaption'}
MAX_BODY = 2_000_000


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def normalize(text: str) -> str:
    return ' '.join(text.split())


class VisibleBlocks(HTMLParser):
    """Collect cited blocks; reject citations not visible in a regular text block."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ignored = 0
        self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','template'):
            self.ignored += 1
        if tag in BLOCKS:
            self.stack.append([tag, []])
    def handle_endtag(self, tag):
        if tag in BLOCKS and self.stack:
            idx = next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i][0] == tag),None)
            if idx is not None:
                _, parts = self.stack[idx]
                self.blocks.append(normalize(''.join(parts)))
                del self.stack[idx:]
        if tag in ('script','style','template') and self.ignored:
            self.ignored -= 1
    def handle_data(self, data):
        if not self.ignored:
            for _, parts in self.stack:
                parts.append(data)


def extract_citations(body: bytes):
    """Ordered (source, block index, occurrence, context hash) from visible text."""
    if not isinstance(body,bytes) or not 0 < len(body) <= MAX_BODY:
        return [], ['BODY_MISSING_OR_OVERSIZED']
    try:
        text = body.decode('utf-8','strict')
    except UnicodeError:
        return [], ['BODY_NOT_UTF8']
    parser = VisibleBlocks()
    try:
        parser.feed(text)
        parser.close()
    except (ValueError,AssertionError):
        return [], ['HTML_CONTEXT_PARSE_FAILURE']
    records = []
    counts = Counter()
    for block_index, block in enumerate(parser.blocks):
        for match in CITE.finditer(block):
            sid = match.group(1)
            counts[sid] += 1
            records.append({'source_id':sid,'block_index':block_index,
                            'occurrence':counts[sid],
                            'context_sha256':hashlib.sha256(block.encode('utf-8')).hexdigest()})
    errors = []
    raw_citations = CITE.findall(text)
    if Counter(raw_citations) != Counter(x['source_id'] for x in records):
        errors.append('HIDDEN_OR_UNSCOPED_CITATION_MARKER')
    if parser.stack or parser.ignored:
        errors.append('UNBALANCED_CITED_DOCUMENT_STRUCTURE')
    return records, errors


def variant_key(v):
    if not isinstance(v,dict): return None
    return (v.get('branch'),v.get('source_blob'),v.get('url'))


def review_bundle(docket:dict, bodies:dict[str,bytes]|None=None,
                  annotations:dict|None=None)->dict:
    """Fail-closed, deterministic source-to-claim binding check; never grants QD PASS."""
    errors=[]; blockers=['INDEPENDENT_QUALIFIED_SAFETY_AND_SOURCE_REVIEW_REQUIRED',
                         'NATIVE_WORDPRESS_EXPORT_AND_BROWSER_QA_REQUIRED',
                         'FOUNDER_RELEASE_APPROVAL_REQUIRED']
    if not isinstance(docket,dict) or docket.get('schema')!=1:
        errors.append('INVALID_ORIGINAL_DOCKET'); docket={}
    originals=docket.get('original_articles',[])
    cross=docket.get('all_original_source_id_crosswalk',[])
    disputes=docket.get('source_evidence_disputes',[])
    groups=docket.get('shared_exact_url_review_groups',[])
    if not isinstance(originals,list) or len(originals)!=35 or any(not isinstance(x,dict) for x in originals):
        errors.append('THIRTY_FIVE_ORIGINAL_ARTICLE_IDENTITIES_REQUIRED'); originals=[]
    if not isinstance(cross,list) or len(cross)!=203 or any(not isinstance(x,dict) for x in cross):
        errors.append('TWO_HUNDRED_THREE_ORIGINAL_SOURCE_IDENTITIES_REQUIRED'); cross=[]
    if not isinstance(disputes,list) or len(disputes)!=5:
        errors.append('FIVE_DISPUTES_MUST_REMAIN_UNSELECTED'); disputes=[]
    if not isinstance(groups,list) or len(groups)!=17:
        errors.append('SEVENTEEN_SHARED_URL_GROUPS_MUST_REMAIN_VISIBLE'); groups=[]
    by_article={a.get('slug'):a for a in originals}
    by_source={s.get('source_id'):s for s in cross}
    disputed={x.get('source_id') for x in disputes if isinstance(x,dict)}
    shared_ids={sid for g in groups if isinstance(g,dict) for sid in g.get('ids',[]) if isinstance(sid,str)}
    if len(by_article)!=len(originals):errors.append('ARTICLE_SLUG_COLLISION')
    if len(by_source)!=len(cross):errors.append('SOURCE_ID_COLLISION')
    if bodies is None:
        errors.append('AUTHENTIC_ORIGINAL_BODY_BYTES_MISSING'); bodies={}
    if annotations is None:
        errors.append('INDEPENDENT_FROZEN_CITATION_BASELINE_MISSING'); annotations={}
    if not isinstance(bodies,dict):errors.append('INVALID_BODY_MAPPING');bodies={}
    if not isinstance(annotations,dict) or annotations.get('schema')!=1 or annotations.get('release_state')!=DRAFT:
        errors.append('INVALID_FROZEN_CITATION_BASELINE'); annotations={}
    annotation_rows=annotations.get('articles',{})
    if not isinstance(annotation_rows,dict):
        errors.append('INVALID_BASELINE_ARTICLE_MAP');annotation_rows={}
    if set(bodies)!=set(by_article):errors.append('ORIGINAL_BODY_SET_NOT_EXACTLY_35')
    if set(annotation_rows)!=set(by_article):errors.append('BASELINE_ARTICLE_SET_NOT_EXACTLY_35')
    compared=0; citations=0; unknown_ids=set(); shared_in_use=set(); disputed_in_use=set()
    for slug in sorted(by_article):
        orig=by_article[slug]; body=bodies.get(slug)
        if not isinstance(body,bytes):
            errors.append('MISSING_AUTHENTIC_BODY:'+str(slug));continue
        if git_blob(body) not in orig.get('body_candidate_git_blobs',[]):
            errors.append('BODY_NOT_IN_FROZEN_CANDIDATE_SET:'+str(slug))
        live,issues=extract_citations(body)
        errors.extend(issue+':'+str(slug) for issue in issues)
        citations+=len(live)
        baseline=annotation_rows.get(slug)
        if not isinstance(baseline,dict):
            errors.append('ARTICLE_CITATION_ATTESTATION_MISSING:'+str(slug));continue
        if baseline.get('body_git_blob')!=git_blob(body):
            errors.append('ATTESTATION_BODY_HASH_MISMATCH:'+str(slug))
        rows=baseline.get('citations')
        if not isinstance(rows,list):
            errors.append('ATTESTATION_CITATIONS_NOT_LIST:'+str(slug));continue
        if len(rows)!=len(live):
            errors.append('CITATION_OCCURRENCE_COUNT_DRIFT:'+str(slug))
        for index,actual in enumerate(live):
            if index>=len(rows):break
            row=rows[index]
            if not isinstance(row,dict):
                errors.append('INVALID_CITATION_ATTESTATION_ROW:'+str(slug));continue
            for key in ('source_id','block_index','occurrence','context_sha256'):
                if type(row.get(key))!=type(actual[key]) or row.get(key)!=actual[key]:
                    errors.append('CITATION_CLAIM_BINDING_CHANGED:'+str(slug)+':'+str(index));break
            if not isinstance(row.get('context_sha256'),str) or not HEX64.fullmatch(row['context_sha256']):
                errors.append('INVALID_CONTEXT_DIGEST:'+str(slug))
            sid=actual['source_id']
            entry=by_source.get(sid)
            if entry is None:
                unknown_ids.add(sid);continue
            candidate=row.get('source_variant')
            variants=entry.get('variants')
            if not isinstance(variants,list) or not variants:
                errors.append('ORIGINAL_SOURCE_VARIANTS_MISSING:'+sid);continue
            matching=[v for v in variants if variant_key(v)==variant_key(candidate)]
            if not isinstance(candidate,dict) or len(matching)!=1 or not all(
                isinstance(candidate.get(k),str) and candidate.get(k) for k in ('branch','source_blob','url')):
                errors.append('CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT:'+str(slug)+':'+sid)
            if not isinstance(row.get('reading_scope_exact'),str) or not row['reading_scope_exact'].strip():
                errors.append('MISSING_CITATION_READING_SCOPE:'+str(slug)+':'+sid)
            if row.get('review_state')!='HUMAN_REVIEW_REQUIRED':
                errors.append('PREMATURE_CITATION_REVIEW_CLAIM:'+str(slug)+':'+sid)
            if sid in disputed:disputed_in_use.add(sid)
            if sid in shared_ids:shared_in_use.add(sid)
        compared+=1
    if unknown_ids:errors.extend('CITED_SOURCE_NOT_IN_ORIGINAL_DOCKET:'+s for s in sorted(unknown_ids))
    if disputed_in_use:blockers.append('ORIGINAL_CONTESTED_SOURCE_USED_REQUIRES_ADJUDICATION')
    if shared_in_use:blockers.append('SHARED_EXACT_URL_IDS_REQUIRE_IDENTITY_REVIEW')
    blockers.extend(['FIVE_ORIGINAL_SOURCE_DISPUTES_UNRESOLVED','NINE_ORIGINAL_MANUSCRIPT_FORKS_UNRESOLVED'])
    return {'schema':1,'release_state':DRAFT,'eligible':False,'qd_pass':False,
            'publication_approved':False,'merchant_offer_verified':False,
            'reviewed_articles':compared,'citation_occurrences':citations,
            'disputed_ids_cited':sorted(disputed_in_use),'shared_url_ids_cited':sorted(shared_in_use),
            'errors':sorted(set(errors)),'blockers':sorted(set(blockers))}


def main(argv=None)->int:
    ap=argparse.ArgumentParser(description='Original citation-to-claim/source custody (never a release gate PASS)')
    ap.add_argument('--docket',type=Path,required=True)
    ap.add_argument('--repo-root',type=Path)
    ap.add_argument('--frozen-citation-baseline',type=Path)
    args=ap.parse_args(argv)
    try:
        docket=json.loads(args.docket.read_text(encoding='utf-8'))
        baseline=json.loads(args.frozen_citation_baseline.read_text(encoding='utf-8')) if args.frozen_citation_baseline else None
        bodies=None
        if args.repo_root:
            # Reuse the frozen R441 bounded reader; never follow symlinks or external paths.
            from r440_original_slate_evidence_replay import bounded_read
            bodies={a['slug']:bounded_read(args.repo_root,'preparedness/content/articles/'+a['slug']+'.body.html')
                    for a in docket['original_articles']}
        result=review_bundle(docket,bodies,baseline)
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,json.JSONDecodeError):
        result=review_bundle({},None,None)
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':
    raise SystemExit(main())
