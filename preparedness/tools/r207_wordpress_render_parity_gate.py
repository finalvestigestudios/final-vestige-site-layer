#!/usr/bin/env python3
"""Fail-closed comparison of frozen authored Preparedness bodies to DRAFT WP/preview exports.

Structural parity is not evidence of source accuracy, medical safety, checkout success,
independent Quality Director signoff, or publication authorization. Issue #136 only.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import html
import json
from pathlib import Path
import re
import subprocess

HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r207-wp-body-parity-v1'
MANIFEST = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
MANIFEST_OID = '5822f9dfde21d1f3bdfc26658769d852c639438c'
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9]+(?:-[a-z0-9]+)*)\|([^{}|\r\n]+)\}\}')
ANY_TOKEN = re.compile(r'\{\{[^{}]*\}\}')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
SHA = re.compile(r'[0-9a-f]{40}\Z')

class Invalid(ValueError): pass

def require(ok, why):
    if not ok: raise Invalid(why)

def git_oid(value: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(value)).encode('ascii')+b'\0'+value).hexdigest()

def strict_json(raw: bytes):
    def unique(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,'duplicate JSON key: '+k)
            d[k]=v
        return d
    def reject(x): raise Invalid('invalid JSON constant: '+x)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=reject)

def normalize_text(value: str):
    return ' '.join(html.unescape(value).split())

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style') and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip: self.out.append(data)
    def result(self): return normalize_text(''.join(self.out))

class Export(HTMLParser):
    """Read only the article's pa-body; ignore injected chrome, bibliography, styles."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.body_level=None;self.cite_level=None
        self.cite_links=[];self.cite_seen=0;self.cite_entries=[]
        self.text=[];self.article=[];self.body_count=0
        self.script_level=None;self.scripts=[];self.script_buf=[]
    def handle_starttag(self, tag, attrs):
        att=dict(attrs); classes=set(att.get('class','').split())
        require(not (self.body_level is not None and tag in ('script','style','iframe','object','embed')),
                'unreviewed active or embedded content in rendered article body')
        if tag=='script':
            require(att.get('type')=='application/ld+json',
                    'unreviewed script or tracking inside exported draft')
        if 'pa-article' in classes:
            self.article.append({k:att.get(k) for k in ('data-slug','data-track','data-section')})
        level=len(self.stack)+1
        if 'pa-body' in classes:
            require(self.body_level is None and self.body_count==0 and att.get('id')=='pa-main',
                    'multiple or noncanonical pa-body')
            self.body_level=level;self.body_count+=1
        if tag=='script' and att.get('type')=='application/ld+json':
            self.script_level=level;self.script_buf=[]
        if self.body_level is not None and tag=='sup' and 'pa-cite' in classes:
            require(self.cite_level is None,'nested citation marker')
            self.cite_level=level;self.cite_seen=0
        if self.cite_level is not None and tag=='a':
            href=att.get('href','')
            match=re.fullmatch(r'#src-([1-9][0-9]*)',href)
            require(match is not None,'citation anchor is not a local numbered footnote')
            self.cite_links.append(int(match.group(1)));self.cite_seen+=1
        if tag not in VOID:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag in VOID:return
        require(bool(self.stack) and self.stack[-1]==tag,'malformed/unbalanced markup: '+tag)
        level=len(self.stack)
        if self.cite_level==level:
            require(self.cite_seen==1,'citation marker without exactly one source link')
            self.cite_level=None
        if self.body_level==level:self.body_level=None
        if self.script_level==level:
            self.scripts.append(''.join(self.script_buf));self.script_level=None
        self.stack.pop()
    def handle_data(self,data):
        if self.script_level is not None:self.script_buf.append(data)
        elif self.body_level is not None and self.cite_level is None:self.text.append(data)
    def result(self):
        require(not self.stack and self.body_level is None and self.cite_level is None,
                'unclosed rendered HTML elements')
        require(self.body_count==1 and len(self.article)==1,'must contain one article and one pa-body')
        return normalize_text(''.join(self.text))

def authored_text(raw: bytes, route_by_slug: dict):
    body=raw.decode('utf-8')
    citations=CITE.findall(body)
    links=LINK.findall(body)
    require(len(citations)>0,'no source markers in authored body')
    require(all(slug in route_by_slug and label.strip()==label and label.strip()
                for slug,label in links),'unknown or malformed authored crosslinks')
    stripped=CITE.sub('',body)
    stripped=LINK.sub(lambda m:m.group(2),stripped)
    require('{{' not in stripped and '}}' not in stripped and not ANY_TOKEN.search(stripped),
            'unhandled source token')
    txt=Text();txt.feed(stripped);txt.close()
    return txt.result(),citations

def expected_numbers(citations):
    ids=[];result=[]
    for sid in citations:
        if sid not in ids:ids.append(sid)
        result.append(ids.index(sid)+1)
    return ids,result

def audit(manifest, materials, wp, previews, build_report):
    out={'schema':SCHEMA,'issue':136,'coordination_issue':820,
         'state':INVALID,'publication_authorized':False,'independent_qd_pass':False,
         'human_source_approved':False,'medical_safety_verified':False,
         'merchant_offer_verified':False,'verified_paid_orders':None,
         'realized_net_revenue':None,'errors':[],'articles':[],'summary':{}}
    try:
        require(type(manifest) is dict and manifest.get('schema')==
                'fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1' and
                manifest.get('issue')==136 and manifest.get('conversion_issue')==820 and
                manifest.get('state')==HOLD,'wrong frozen original manifest')
        for f in ('publication_authorized','independent_qd_pass','human_source_approved',
                  'medical_safety_verified','merchant_offer_verified'):
            require(manifest.get(f) is False,'unfounded manifest permission: '+f)
        require(manifest.get('verified_paid_orders') is None and
                manifest.get('realized_net_revenue') is None,'unverified revenue')
        rows=manifest.get('articles');heads=manifest.get('branch_heads')
        require(type(rows) is list and len(rows)==35 and type(heads) is dict and len(heads)==7
                and manifest.get('artifact_count')==35 and
                manifest.get('export_target_count_with_six_tools')==41,
                'slate or target count drift')
        require(type(materials) is dict and type(wp) is dict and type(previews) is dict,
                'original/export inputs must be maps')
        slugs=[r.get('slug') for r in rows]
        require(len(set(slugs))==35 and set(materials)==set(wp)==set(previews)==set(slugs),
                'missing/foreign/duplicate output article')
        require(type(build_report) is dict and type(build_report.get('articles')) is list,
                'missing build-report')
        build_rows=build_report['articles']
        require(len(build_rows)>=35,'build report incomplete')
        index={r.get('slug'):r for r in build_rows if type(r) is dict}
        require(len(index)==len(build_rows) and set(slugs)<=set(index),
                'duplicate/missing article in build report')
        urls={r['slug']:r['route'] for r in rows};seen=set();total_cites=0;total_chars=0
        for n,r in enumerate(rows,1):
            slug=r['slug'];route=r['route'];src=materials[slug]
            require(r.get('n')==n and route==f'/preparedness/{r["section"]}/{slug}/' and
                    route not in seen and r['source_cluster'] in heads and
                    r['branch_sha']==heads[r['source_cluster']] and
                    r['track'] in ('modern','lost-ways') and
                    all(type(r.get(k)) is str and SHA.fullmatch(r[k]) for k in ('body_oid','meta_oid')),
                    'frozen route/head/census drift: '+slug)
            seen.add(route)
            require(type(src) is dict and set(src)=={'body','meta'} and
                    type(src['body']) is bytes and type(src['meta']) is bytes and
                    len(src['body'])==r['body_bytes'] and len(src['meta'])==r['meta_bytes'] and
                    git_oid(src['body'])==r['body_oid'] and git_oid(src['meta'])==r['meta_oid'],
                    'original author Git identity changed: '+slug)
            meta=strict_json(src['meta'])
            require(meta.get('slug')==slug and meta.get('section')==r['section'] and
                    meta.get('track')==r['track'] and
                    meta.get('status',{}).get('publish')=='draft' and
                    meta.get('safety_review',{}).get('state')=='pending',
                    'article status/identity changed: '+slug)
            original,citations=authored_text(src['body'],urls)
            unique,numbers=expected_numbers(citations)
            final=[]
            for label,payload in [('wp',wp[slug]),('preview',previews[slug])]:
                require(type(payload) is bytes,'nonbyte export: '+slug+':'+label)
                doc=payload.decode('utf-8')
                require('{{cite:' not in doc and '{{link:' not in doc and
                        'Safety review pending' in doc and 'Draft: not public' in doc and
                        'Pending. A human safety review is required before this page can be published.' in doc,
                        'missing draft/safety label or unresolved token: '+slug+':'+label)
                if label=='wp':
                    require(doc.count('<!-- wp:html -->')==1 and doc.count('<!-- /wp:html -->')==1,
                            'not exactly one WP draft HTML block: '+slug)
                parsed=Export();parsed.feed(doc);parsed.close();text=parsed.result()
                require(parsed.article==[{'data-slug':slug,'data-track':r['track'],
                                        'data-section':r['section']}],
                        'rendered article identity drift: '+slug+':'+label)
                require(text==original,'editorial/safety prose lost or altered: '+slug+':'+label)
                require(parsed.cite_links==numbers,
                        'citation occurrence/order lost: '+slug+':'+label)
                require(len(parsed.scripts)==1,'JSON-LD provenance missing: '+slug+':'+label)
                ld=strict_json(parsed.scripts[0].encode('utf-8'))
                graphs=ld.get('@graph',[])
                article=next((x for x in graphs if type(x) is dict and x.get('@type')=='Article'),None)
                require(type(article) is dict and
                        article.get('mainEntityOfPage')=='https://finalvestige.com'+route and
                        article.get('isAccessibleForFree') is True and
                        'datePublished' not in article,
                        'rendered canonical/free/draft schema drift: '+slug+':'+label)
                final.append(text)
            build=index[slug]
            require(build.get('canonical')=='https://finalvestige.com'+route and
                    build.get('sources')==unique,'build report canonical/citation drift: '+slug)
            total_cites+=len(citations);total_chars+=len(original)
            out['articles'].append({'n':n,'slug':slug,'canonical':route,
                'source_blob_oid':r['body_oid'],'source_citations':len(citations),
                'unique_sources':len(unique),'authored_text_characters':len(original),
                'normalized_text_sha256':hashlib.sha256(original.encode('utf-8')).hexdigest(),
                'wp_preview_parity':True,'safety_adjudicated':False})
        out['summary']={'original_articles':35,'rendered_articles_checked':35,
                        'wp_draft_exports_checked':35,'previews_checked':35,
                        'citation_occurrences':total_cites,'authored_text_characters':total_chars,
                        'full_41_output_targets_not_verified':True,
                        'independent_source_support_verified':False,
                        'independent_safety_qd_verified':False,
                        'published_destinations_verified':False}
        out['state']=HOLD
    except (Invalid,ValueError,KeyError,TypeError,AttributeError,UnicodeError,IndexError) as exc:
        out['errors']=[str(exc)[:260]]
        out['articles']=[];out['summary']={}
    return out

def git_show(repo: Path, rev_and_path: str):
    p=subprocess.run(['git','show',rev_and_path],cwd=repo,capture_output=True,check=True,timeout=40)
    return p.stdout

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--report',type=Path,default=None)
    args=p.parse_args(argv)
    report={'schema':SCHEMA,'state':INVALID,'errors':['not executed']}
    try:
        frozen=git_show(args.repo,'HEAD:'+MANIFEST)
        require(git_oid(frozen)==MANIFEST_OID,'frozen manifest Git identity mismatch')
        manifest=strict_json(frozen)
        materials={}
        for row in manifest['articles']:
            slug=row['slug'];sha=row['branch_sha'];root='preparedness/content/articles/'+slug
            materials[slug]={'body':git_show(args.repo,sha+':'+root+'.body.html'),
                             'meta':git_show(args.repo,sha+':'+root+'.meta.json')}
        directory=args.repo/'preparedness/build'
        wp={r['slug']:(directory/'wp'/ (r['slug']+'.html')).read_bytes() for r in manifest['articles']}
        previews={r['slug']:(directory/'preview'/(r['slug']+'.html')).read_bytes() for r in manifest['articles']}
        build_report=strict_json((directory/'build-report.json').read_bytes())
        report=audit(manifest,materials,wp,previews,build_report)
    except (OSError,subprocess.SubprocessError,Invalid,ValueError,KeyError,TypeError) as exc:
        report={'schema':SCHEMA,'issue':136,'coordination_issue':820,'state':INVALID,
                'publication_authorized':False,'independent_qd_pass':False,
                'errors':[str(exc)[:260]]}
    rendered=json.dumps(report,indent=2,sort_keys=True)
    if args.report: args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(rendered+'\n',encoding='utf-8')
    else: print(rendered)
    return 2 if report['state']==HOLD else 3

if __name__=='__main__':raise SystemExit(main())
