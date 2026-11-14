#!/usr/bin/env python3
"""R367: read-only, fail-closed WordPress/preview source-output custody.

Input: untrusted private preparedness/build output plus the local manuscript tree.
No WordPress API, HTTP, social, email, merchant or analytics connections.
A structural match NEVER authorizes publishing, QD approval or safety claims.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r367-private-export-custody-v1'
HOLD = dict(may_publish=False, may_merge=False, qd_pass=False, medical_safety_verified=False,
            source_claims_human_verified=False, wp_ready_for_release=False,
            paid_sku_verified=False, verified_paid_orders=False, revenue_verified=False)
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
FOOTNOTE = re.compile(r'<sup class="pa-cite"><a href="#src-(\d+)" aria-label="Source (\d+): [^"]+">\[(\d+)\]</a></sup>')
SRC_ENTRY = re.compile(r'<li id="src-(\d+)"><a href="([^"]+)" rel="noopener">[^<]+</a>', re.S)
WP = re.compile(r'\A<!-- wp:html -->\n<style>.*?</style>\n(.*?)\n<!-- /wp:html -->\n\Z', re.S)
PREVIEW = re.compile(r'\A<!doctype html><html lang="en"><head>.*?<meta name="robots" content="noindex,nofollow">.*?</style></head><body><main>(.*?)</main></body></html>\Z', re.S)


def json_clean(path: Path):
    def unique(pairs):
        d={}
        for key,value in pairs:
            if key in d:raise ValueError('DUPLICATE_JSON_KEY')
            d[key]=value
        return d
    return json.loads(path.read_text('utf-8'),object_pairs_hook=unique)


def digest(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()


def make_report(errors,review,stats):
    return dict(schema=SCHEMA,status='INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
                errors=sorted(set(errors)),human_review=sorted(set(review)),evidence=stats,**HOLD)


def pair(wp: str, preview: str, slug: str, sources: list[str], *, source_urls=()):
    """Check deterministic paired output; match citation *occurrences* and source footnotes."""
    errors=[];review=[];stats={'slug':slug}
    if any(not isinstance(s,str) or len(s)>2_000_000 for s in (wp,preview)):
        return ['BAD_EXPORT_CONTENT'],[],stats
    if wp.count('<!-- wp:html -->')!=1 or wp.count('<!-- /wp:html -->')!=1:
        errors.append('WP_BLOCK_STRUCTURE')
    mw=WP.fullmatch(wp);mp=PREVIEW.fullmatch(preview)
    if not mw:errors.append('WP_WRAPPER_INVALID')
    if not mp:errors.append('PREVIEW_WRAPPER_OR_NOINDEX_INVALID')
    if not mw or not mp:return errors,review,stats
    body=mw.group(1);other=mp.group(1)
    if body!=other:errors.append('EXPORT_BODY_MISMATCH')
    stats['inner_sha256']=digest(body)
    stats['wp_sha256']=digest(wp)
    stats['preview_sha256']=digest(preview)
    if '{{' in body or '}}' in body:errors.append('UNRESOLVED_TEMPLATE_TOKEN')
    if not isinstance(sources,list) or any(not isinstance(s,str) or not SLUG.fullmatch(s) for s in sources):
        errors.append('BAD_SOURCE_ORDER');sources=[]
    counts=Counter(int(x) for x,y,z in FOOTNOTE.findall(body) if x==y==z)
    raw_sup=len(re.findall(r'<sup\b[^>]*class="pa-cite"',body))
    if sum(counts.values())!=raw_sup:errors.append('MALFORMED_CITATION_OUTPUT')
    idx=set(range(1,len(sources)+1))
    if set(counts)!=idx or any(counts[i]<1 for i in idx):errors.append('FOOTNOTE_NUMBER_SET_MISMATCH')
    rows=SRC_ENTRY.findall(body)
    numbers=[int(n) for n,_ in rows]
    if numbers!=list(range(1,len(sources)+1)):
        errors.append('SOURCE_LIST_NUMBER_OR_ORDER_MISMATCH')
    if len(re.findall(r'<li id="src-',body))!=len(rows):
        errors.append('SOURCE_LIST_MARKUP_INVALID')
    if source_urls and len(rows)==len(source_urls):
        for (number,url),expected in zip(rows,source_urls):
            if html.unescape(url)!=expected:
                errors.append('SOURCE_DESTINATION_CHANGED:'+number)
    elif source_urls:errors.append('SOURCE_DESTINATION_COUNT_MISMATCH')
    if not re.search(r'<div class="pa pa-article" data-slug="'+re.escape(slug)+r'"',body):
        errors.append('ARTICLE_SLUG_OR_CONTAINER_DRIFT')
    if not all(x in body for x in ('Draft: not public','Independent safety/source and QD verification pending',
                                  'Human source-link check pending','Sources and verification')):
        errors.append('RELEASE_OR_SOURCE_CAUTION_REMOVED')
    if 'Human source-link check complete' in body:
        review.append('CLAIMED_HUMAN_LINK_CHECK_REQUIRES_PROOF:'+slug)
    if not re.search(r'"isAccessibleForFree":\s*true',body):
        errors.append('FREE_ACCESS_SCHEMA_MISSING')
    if re.search(r'"isAccessibleForFree":\s*false',body):
        errors.append('GATED_CONTENT_SCHEMA')
    stats.update(citation_occurrences=sum(counts.values()),source_entry_count=len(rows),source_ids=len(sources))
    return errors,review,stats


def audit(root: Path, build: Path | None=None):
    """Audit all 41 original manuscripts and exact 50 private pairs. Read only."""
    root=Path(root)
    build=Path(build) if build is not None else root/'build'
    errs=[];review=[];evidence=[]
    if root.is_symlink() or build.is_symlink() or not root.is_dir():
        return make_report(['AUTHENTIC_NATIVE_PREPAREDNESS_ROOT_REQUIRED'],[],{})
    if not (root/'tools'/'build.py').is_file() or not (root/'taxonomy.json').is_file():
        return make_report(['AUTHENTIC_NATIVE_PREPAREDNESS_ROOT_REQUIRED'],[],{})
    try:
        report=json_clean(build/'build-report.json')
        entries=report['articles']
        if not isinstance(entries,list) or len(entries)!=41:
            errs.append('ARTICLE_TOOL_BUILD_COUNT_NOT_41');entries=[]
        meta_paths=sorted((root/'content'/'articles').glob('*.meta.json'))+sorted((root/'content'/'tools').glob('*.meta.json'))
        if len(meta_paths)!=41:errs.append('MANUSCRIPT_COUNT_NOT_41')
        metas={}
        for p in meta_paths:
            m=json_clean(p);slug=m.get('slug')
            if not isinstance(slug,str) or not SLUG.fullmatch(slug) or slug in metas or p.name!=slug+'.meta.json':
                errs.append('INVALID_OR_DUPLICATE_MANUSCRIPT_ID');continue
            body=p.with_name(slug+'.body.html')
            if body.is_symlink():errs.append('SYMLINK_SOURCE_FORBIDDEN');continue
            metas[slug]=(m,body.read_text('utf-8'))
        slugs=[x.get('slug') for x in entries if isinstance(x,dict)]
        if len(set(slugs))!=41 or set(slugs)!=set(metas):errs.append('REPORT_DOCUMENT_IDENTITIES_DRIFT')
        hubs=report.get('hubs')
        if not isinstance(hubs,list) or len(hubs)!=8:
            errs.append('PRIVATE_HUB_COUNT_NOT_8');hubs=[]
        hubids=['hub-'+x['section'] for x in hubs if isinstance(x,dict) and isinstance(x.get('section'),str) and SLUG.fullmatch(x['section'])]
        names=slugs+hubids+['landing']
        if len(set(names))!=50:errs.append('PRIVATE_EXPECTED_50_UNIQUE_NAMES')
        for folder in ('wp','preview'):
            d=build/folder
            if d.is_symlink() or not d.is_dir():errs.append('PRIVATE_EXPORT_FOLDER_MISSING:'+folder);continue
            allfiles={x.name for x in d.iterdir() if x.is_file()}
            expected={x+'.html' for x in names}
            if allfiles!=expected:errs.append('PRIVATE_EXPORT_INVENTORY_DRIFT:'+folder)
            if any(x.is_symlink() for x in d.iterdir()):errs.append('SYMLINK_EXPORT_FORBIDDEN:'+folder)
        releases=report.get('release_evidence',{})
        if not isinstance(releases,dict) or releases.get('independent_qa_verified') is not False or releases.get('wordpress_publication_performed') is not False:
            errs.append('REPORT_RELEASE_ASSERTION_UNTRUSTWORTHY')
        if releases.get('state') not in ('HOLD','REQUIRES_INDEPENDENT_QA'):
            errs.append('REPORT_RELEASE_STATE_INVALID')
        # Resolve source destinations exactly as the native builder does: a
        # document's own contributor fragment wins, else its base register.
        variants={}
        files=[('base',root/'sources'/'register.json')]
        files += [(p.stem,p) for p in sorted((root/'sources'/'fragments').glob('*.json'))]
        for origin,fn in files:
            doc=json_clean(fn)
            for row in doc['sources']:
                variants.setdefault(row['id'],[]).append((origin,row))
        crosswalk=json_clean(root/'sources'/'crosswalk.json')
        origins=crosswalk['article_origins']
        if set(origins)!=set(metas):errs.append('ARTICLE_ORIGIN_CROSSWALK_DRIFT')
        for item in entries:
            if not isinstance(item,dict) or item.get('slug') not in metas:continue
            slug=item['slug'];m,raw=metas[slug]
            if m.get('status',{}).get('publish')!='draft':errs.append('NON_DRAFT_INPUT:'+slug)
            raw_cites=CITE.findall(raw)
            expected=list(dict.fromkeys(raw_cites))
            if item.get('sources')!=expected:errs.append('RAW_CITATION_ORDER_REPORT_MISMATCH:'+slug)
            if not isinstance(item.get('canonical'),str) or not item['canonical'].startswith('https://finalvestige.com/preparedness/') or not item['canonical'].endswith('/'+slug+'/'):
                errs.append('CANONICAL_URL_DRIFT:'+slug)
            # Source-order conversion is checked, but external source attribution requires separate R362/R363 qualified review.
            wp=(build/'wp'/f'{slug}.html').read_text('utf-8')
            pv=(build/'preview'/f'{slug}.html').read_text('utf-8')
            urls=[]
            for sid in expected:
                own=[row for origin,row in variants.get(sid,[]) if origin==origins.get(slug,'base')]
                base=[row for origin,row in variants.get(sid,[]) if origin=='base']
                matches=own if own else base
                if len(matches)!=1 or not isinstance(matches[0].get('url') if matches else None,str):
                    errs.append('SOURCE_ORIGIN_AMBIGUITY:'+slug+':'+sid)
                    urls.append('INVALID_UNKNOWN_SOURCE')
                else: urls.append(matches[0]['url'])
            e,r,s=pair(wp,pv,slug,expected,source_urls=urls)
            errs += [slug+':'+x for x in e];review+=r
            if s.get('citation_occurrences')!=len(raw_cites):errs.append('CITATION_OCCURRENCE_LOST:'+slug)
            evidence.append(s)
        for slug in hubids+['landing']:
            wp=(build/'wp'/f'{slug}.html').read_text('utf-8')
            pv=(build/'preview'/f'{slug}.html').read_text('utf-8')
            mw=WP.fullmatch(wp);mp=PREVIEW.fullmatch(pv)
            if not mw or not mp or mw.group(1)!=mp.group(1):errs.append('HUB_OR_LANDING_EXPORT_MISMATCH:'+slug)
            elif '{{' in mw.group(1):errs.append('UNRESOLVED_HUB_TOKEN:'+slug)
        return make_report(errs,review,{'manuscripts':len(metas),'paired_exports_inspected':len(evidence)+len(hubids)+1,
            'source_claims_human_verified':False,'physical_print_verified':False,
            'files':evidence})
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,json.JSONDecodeError) as exc:
        return make_report(['NATIVE_PRIVATE_EXPORT_UNAVAILABLE:'+type(exc).__name__],review,{'pairs_read_before_failure':len(evidence)})


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--preparedness-root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--build-root',type=Path,default=None)
    a=p.parse_args()
    print(json.dumps(audit(a.preparedness_root,a.build_root),indent=2,sort_keys=True))
    sys.exit(2)  # A complete private export never confers publishing or safety approval.
