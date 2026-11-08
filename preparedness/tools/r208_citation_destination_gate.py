#!/usr/bin/env python3
"""R208: Fail-closed original-to-rendered citation destination and source-use custody.

Offline draft gate only: no safety/QD approval, no live requests, no CMS or commerce writes.
Expects independently authenticated R200 source inputs and source-register evidence.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import re
import subprocess

HOLD='DRAFT_HARD_HOLD'; INVALID='INVALID_HARD_HOLD'
SCHEMA='fv-preparedness-r208-reference-destination-v1'
CITE=re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
LINK=re.compile(r'\{\{link:([a-z0-9]+(?:-[a-z0-9]+)*)\|([^{}|\r\n]+)\}\}')
VOID={'br','hr','img','input','meta','link','source','wbr','area','col','embed'}
FORBIDDEN={'script','iframe','object','embed','form','input','textarea','button','select','svg','math','video','audio'}

class GateError(ValueError): pass

def check(flag, msg):
    if not flag: raise GateError(msg)

def norm(s):return ' '.join(html.unescape(s).split())

def safe_href(href):
    check(type(href) is str and href.strip()==href and bool(href), 'missing or padded href')
    check(not any(ord(c)<32 or ord(c)==127 for c in href), 'control byte in href')
    check(not href.startswith('//'), 'protocol-relative URL')
    p=urlsplit(href)
    check(p.scheme in ('','https') and not p.username and not p.password, 'unapproved URL scheme or credentials')
    check(not p.scheme or (p.scheme=='https' and bool(p.netloc)), 'malformed HTTPS URL')
    check(p.scheme or href[0] in ('/','#'), 'relative URL not root/fragment anchored')
    check(not p.netloc or p.scheme=='https', 'unapproved external host')
    return href

class Inspector(HTMLParser):
    """Extract complete pa-body link sequence and source list without reading other chrome."""
    def __init__(self, fragment=False):
        super().__init__(convert_charrefs=True)
        self.fragment=fragment;self.stack=[];self.body=fragment;self.sources=False
        self.body_seen=0;self.sources_seen=0;self.body_links=[];self.entries=[]
        self.current_a=None;self.current_li=None;self.unsafe=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); classes=set((a.get('class') or '').split())
        if not self.fragment and 'pa-body' in classes:
            check(not self.body and not self.body_seen, 'duplicate pa-body')
            self.body=True;self.body_seen+=1
        if not self.fragment and 'pa-sources' in classes:
            check(not self.sources and not self.sources_seen,'duplicate pa-sources')
            self.sources=True;self.sources_seen+=1
        if self.body or self.sources:
            check(tag not in FORBIDDEN,'active/embedded tag inside instructional content: '+tag)
            check(not any(k.lower().startswith('on') or k.lower() in ('srcdoc','formaction') for k in a),
                  'event handler/active attribute inside instructional content')
            for k in ('href','src','action'):
                if k in a: safe_href(a[k])
            if tag=='a':
                check(self.current_a is None,'nested anchor')
                self.current_a={'href':safe_href(a.get('href')), 'text':[]}
            if self.sources and tag=='li':
                check(self.current_li is None,'nested source list item')
                self.current_li={'id':a.get('id'), 'text':[], 'links':[]}
        if tag not in VOID:self.stack.append((tag,self.body,self.sources))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_data(self, data):
        if self.current_a is not None:self.current_a['text'].append(data)
        if self.current_li is not None:self.current_li['text'].append(data)
    def handle_endtag(self,tag):
        if tag in VOID:return
        check(bool(self.stack) and self.stack[-1][0]==tag,'malformed rendered markup')
        if tag=='a' and self.current_a is not None:
            rec={'href':self.current_a['href'],'text':norm(''.join(self.current_a['text']))}
            if self.body:self.body_links.append(rec)
            if self.sources and self.current_li is not None:self.current_li['links'].append(rec)
            self.current_a=None
        if tag=='li' and self.current_li is not None:
            self.current_li['text']=norm(''.join(self.current_li['text']))
            self.entries.append(self.current_li);self.current_li=None
        self.stack.pop()
        if not self.fragment and self.body and not any(b for _,b,_ in self.stack):self.body=False
        if self.sources and not any(s for _,_,s in self.stack):self.sources=False
    def result(self):
        check(not self.stack and self.current_a is None and self.current_li is None,'unclosed HTML')
        if not self.fragment:check(self.body_seen==1 and self.sources_seen==1,'missing article or bibliography')
        return self

def expected_body(body, route_map):
    order=[]
    def cite(m):
        sid=m.group(1)
        if sid not in order:order.append(sid)
        n=order.index(sid)+1
        return f'<sup class="pa-cite"><a href="#src-{n}">[{n}]</a></sup>'
    body=CITE.sub(cite,body)
    def link(m):
        slug,label=m.groups()
        check(slug in route_map,'unknown internal article: '+slug)
        return '<a href="'+html.escape(route_map[slug],quote=True)+'">'+label+'</a>'
    body=LINK.sub(link,body)
    check('{{' not in body and '}}' not in body,'unresolved authored template')
    parser=Inspector(fragment=True);parser.feed(body);parser.close();parser.result()
    return order,parser.body_links

def audit(rows, materials, wp, previews, source_inventory):
    report={'schema':SCHEMA,'issue':136,'coordination_issue':820,'state':INVALID,
            'publication_authorized':False,'independent_qd_pass':False,
            'human_source_approved':False,'medical_safety_verified':False,
            'merchant_offer_verified':False,'confirmed_orders':None,'realized_net_revenue':None,
            'articles':[],'exceptions':[],'errors':[]}
    try:
        check(type(rows) is list and len(rows)==35,'requires frozen 35-original slate')
        slugs=[r['slug'] for r in rows]
        check(len(set(slugs))==35 and all(type(x) is dict for x in rows),'duplicate/invalid original articles')
        check(type(materials) is dict and type(wp) is dict and type(previews) is dict
              and set(materials)==set(wp)==set(previews)==set(slugs),'missing or extra source/export rows')
        check(type(source_inventory) is dict,'source inventory is missing')
        routes={r['slug']:r['route'] for r in rows}
        check(len(set(routes.values()))==35,'duplicate original route')
        for row in rows:
            slug=row['slug'];doc=materials[slug]
            check(type(doc) is dict and type(doc.get('body')) is str and
                  type(doc.get('meta')) is dict,'missing authenticated original '+slug)
            meta=doc['meta'];body=doc['body']
            check(meta.get('slug')==slug and meta.get('status',{}).get('publish')=='draft' and
                  meta.get('safety_review',{}).get('state')=='pending','unreviewed safety state changed '+slug)
            expected,links=expected_body(body,routes)
            check(expected,'no original citations: '+slug)
            use=meta.get('source_use',{})
            check(type(use) is dict,'missing source_use mapping '+slug)
            for label,files in [('wp',wp),('preview',previews)]:
                raw=files[slug]
                check(type(raw) is str,'non-UTF8 render '+slug+':'+label)
                parser=Inspector();parser.feed(raw);parser.close();parser.result()
                check(parser.body_links==links,'body anchor destination/text mutation '+slug+':'+label)
                check(len(parser.entries)==len(expected),'footnote count changed '+slug+':'+label)
                for n,sid in enumerate(expected,1):
                    item=parser.entries[n-1]
                    check(item['id']==f'src-{n}' and len(item['links'])==1,
                          f'footnote anchor count/id changed {slug}:{label}:{n}')
                    source=source_inventory.get(sid)
                    check(type(source) is dict, 'unknown registered source '+sid)
                    for k in ('url','title','publisher'):
                        check(type(source.get(k)) is str and source[k], 'incomplete source record '+sid+':'+k)
                    check(item['links'][0]=={'href':safe_href(source['url']),'text':norm(source['title'])},
                          f'footnote URL/title substituted {slug}:{label}:{sid}')
                    check(norm(source['publisher']) in item['text'],
                          f'publisher lost from footnote {slug}:{label}:{sid}')
                    explanation=use.get(sid)
                    if not explanation:
                        report['exceptions'].append({'slug':slug,'source_id':sid,'type':'missing_article_source_use',
                                                    'review_required':True})
                    else:
                        check(type(explanation) is str and
                              'Used for: '+norm(explanation) in item['text'],
                              f'article-specific source explanation mutated {slug}:{label}:{sid}')
                    if source.get('human_link_check') is not True:
                        report['exceptions'].append({'slug':slug,'source_id':sid,'type':'source_human_link_check_unverified',
                                                    'review_required':True})
            report['articles'].append({'slug':slug,'source_count':len(expected),
                                       'body_link_count':len(links),'rendered_drafts_checked':2,
                                       'source_support_or_safety_approved':False})
        report['state']=HOLD
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError) as exc:
        report['errors']=[str(exc)[:300]];report['articles']=[]
    return report

def git_show(repo, token):
    return subprocess.run(['git','show',token],cwd=repo,capture_output=True,
                          check=True,timeout=40).stdout

def gather(repo):
    """Never infer complete provenance from HTML; re-run R207 on real Git objects."""
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    import r207_wordpress_render_parity_gate as prior
    raw=git_show(repo,'HEAD:'+prior.MANIFEST)
    check(prior.git_oid(raw)==prior.MANIFEST_OID,'frozen manifest changed')
    manifest=prior.strict_json(raw)
    rows=manifest['articles']; blobs={}
    for r in rows:
        basename='preparedness/content/articles/'+r['slug']
        blobs[r['slug']]={'body':git_show(repo,r['branch_sha']+':'+basename+'.body.html'),
                          'meta':git_show(repo,r['branch_sha']+':'+basename+'.meta.json')}
    base=repo/'preparedness/build'
    wp={r['slug']:(base/'wp'/(r['slug']+'.html')).read_bytes() for r in rows}
    previews={r['slug']:(base/'preview'/(r['slug']+'.html')).read_bytes() for r in rows}
    build_report=prior.strict_json((base/'build-report.json').read_bytes())
    foundation=prior.audit(manifest,blobs,wp,previews,build_report)
    check(foundation.get('state')==prior.HOLD,'R207 full text/footnote parity not established: '+
          str(foundation.get('errors'))[:250])
    materials={slug:{'body':record['body'].decode('utf-8'),
                     'meta':prior.strict_json(record['meta'])} for slug,record in blobs.items()}
    wp={slug:raw.decode('utf-8') for slug,raw in wp.items()}
    previews={slug:raw.decode('utf-8') for slug,raw in previews.items()}
    listing=subprocess.run(['git','ls-tree','-r','--name-only','HEAD',
                            'preparedness/sources/fragments'],cwd=repo,capture_output=True,
                            check=True,timeout=40).stdout.decode('utf-8').splitlines()
    paths=['preparedness/sources/register.json']+sorted(p for p in listing if p.endswith('.json'))
    records={}; conflicts=[]
    for path in paths:
        source_file=prior.strict_json(git_show(repo,'HEAD:'+path))
        for s in source_file['sources']:
            sid=s['id']; old=records.get(sid)
            if old is None:records[sid]=s
            elif old != s:
                if old.get('verified_on'):
                    conflicts.append({'id':sid,'path':path,'type':'verified_source_redefined'})
                else:records[sid]=s
    check(not conflicts,'unadjudicated competing source definitions: '+json.dumps(conflicts)[:300])
    return rows,materials,wp,previews,records

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--report',type=Path)
    args=p.parse_args(argv)
    out={'schema':SCHEMA,'issue':136,'state':INVALID,'publication_authorized':False,
         'independent_qd_pass':False,'errors':['not executed']}
    try:
        rows,materials,wp,previews,sources=gather(args.repo)
        out=audit(rows,materials,wp,previews,sources)
        if out['state']==HOLD:
            out['exceptions'].append({'type':'source_record_claim_support_requires_independent_human_review',
                                      'review_required':True})
    except (OSError,ImportError,subprocess.SubprocessError,ValueError,TypeError,KeyError,UnicodeError) as exc:
        out['errors']=[str(exc)[:350]]
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    else:print(json.dumps(out,indent=2,sort_keys=True))
    return 2 if out['state']==HOLD else 3

if __name__=='__main__':raise SystemExit(main())
