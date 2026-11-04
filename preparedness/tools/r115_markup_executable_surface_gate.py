#!/usr/bin/env python3
"""R115: read-only executable-markup and hidden-citation preflight for all 35 drafts.

A structural warning is never a claim that a source, health recommendation or
WordPress page is approved. No network, CMS, merchant or file writes occur.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r115-markup-surface-HOLD-v1'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|([^{}]*)\}\}')
BAD_SCHEME = re.compile(r'^\s*(?:javascript|vbscript|data|file|blob):', re.I)
ANY_SCHEME = re.compile(r'^\s*([a-z][a-z0-9+.-]*):', re.I)
URL_ATTRS = {'href', 'src', 'srcset', 'poster', 'action', 'formaction', 'xlink:href'}
ACTIVE = {'script','style','iframe','object','embed','form','base','meta','link','svg',
          'math','applet','frame','frameset','portal'}
NONREAD = ACTIVE | {'textarea','select','option','title','head','template','noscript',
                    'canvas','audio','video','picture','datalist'}
INTERACTIVE = {'a','button','select','textarea','option','label'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param',
        'source','track','wbr'}
VALID_STATUS = {'drafted','reviewed'}
VALID_SAFETY = {'pending','not-required','approved'}

class Blocked(ValueError):
    pass

class Surface(HTMLParser):
    """Pessimistic source-marker context audit, not a CSS/browser visibility test."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.flags = set()
        self.visible_sources = []
        self.visible_links = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        names = [str(k).lower() for k,_ in attrs]
        if len(set(names)) != len(names):
            self.flags.add('REPEATED_HTML_ATTRIBUTE')
        d = dict(attrs)
        if tag in ACTIVE:
            self.flags.add('EXECUTABLE_OR_EMBEDDED_ELEMENT')
        if tag in {'textarea','select','option','title','head','template','noscript'}:
            self.flags.add('NONREADING_HTML_ELEMENT')
        for key,value in attrs:
            key = key.lower()
            if key.startswith('on') and len(key)>2:
                self.flags.add('EVENT_HANDLER_ATTRIBUTE')
            if key in {'srcdoc','formaction','http-equiv','autofocus'}:
                self.flags.add('HIGH_RISK_HTML_ATTRIBUTE')
            if key == 'style' and value and any(x in value.lower() for x in
                       ('url(', 'expression(', '@import', '-moz-binding')):
                self.flags.add('ACTIVE_INLINE_STYLE')
            if value and ('{{cite:' in value or '{{link:' in value):
                self.flags.add('SOURCE_TOKEN_IN_ATTRIBUTE')
            if key in URL_ATTRS and value:
                if BAD_SCHEME.match(value):
                    self.flags.add('UNSAFE_LINK_SCHEME')
                elif ANY_SCHEME.match(value) and not re.match(r'^\s*(https?|mailto|tel):',value,re.I):
                    self.flags.add('UNAPPROVED_LINK_SCHEME')
                if key in {'src','srcset','action','formaction','poster'} and value.lstrip().startswith('//'):
                    self.flags.add('PROTOCOL_RELATIVE_FETCH')
        if tag == 'a' and any(t[0]=='a' for t in self.stack):
            self.flags.add('NESTED_ANCHOR')
        if d.get('id'):
            if d['id'] in self.ids: self.flags.add('REPEATED_HTML_ID')
            self.ids.add(d['id'])
        style = re.sub(r'\s+','',(d.get('style') or '').lower())
        classes = (d.get('class') or '').lower().split()
        hidden = (tag in NONREAD or 'hidden' in d or 'inert' in d or
                  (d.get('aria-hidden') or '').strip().lower()=='true' or
                  bool({'hidden','sr-only','visually-hidden','screen-reader-text',
                        'd-none','is-hidden'}.intersection(classes)) or
                  any(x in style for x in ('display:none','visibility:hidden','opacity:0',
                                            'content-visibility:hidden')) or
                  bool(self.stack and self.stack[-1][1]))
        if tag not in VOID: self.stack.append((tag,hidden))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID: self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag in VOID:return
        if not self.stack or self.stack[-1][0]!=tag:
            self.flags.add('MALFORMED_HTML_NESTING')
            return
        self.stack.pop()
    def handle_data(self,data):
        cites = CITE.findall(data)
        links = LINK.findall(data)
        hidden = bool(self.stack and self.stack[-1][1])
        interactive = any(tag in INTERACTIVE for tag,_ in self.stack)
        if hidden and ('{{cite:' in data or '{{link:' in data):
            self.flags.add('SOURCE_TOKEN_IN_NONREADING_CONTEXT')
        if interactive and ('{{cite:' in data or '{{link:' in data):
            self.flags.add('SOURCE_TOKEN_IN_INTERACTIVE_CONTEXT')
        if not hidden and not interactive:
            self.visible_sources.extend(cites)
            self.visible_links.extend(x[0] for x in links)
        if '{{cite:' in data and len(cites)!=data.count('{{cite:'):
            self.flags.add('MALFORMED_CITATION_TOKEN')
        if '{{link:' in data and len(links)!=data.count('{{link:'):
            self.flags.add('MALFORMED_INTERNAL_LINK_TOKEN')
    def handle_comment(self,data):
        if '{{cite:' in data or '{{link:' in data:
            self.flags.add('SOURCE_TOKEN_IN_COMMENT')
    def result(self,body):
        self.feed(body);self.close()
        if self.stack:self.flags.add('UNCLOSED_HTML')
        if len(self.visible_sources)!=len(CITE.findall(body)):
            self.flags.add('RAW_RENDERER_CITATION_DISAGREEMENT')
        if len(self.visible_links)!=len(LINK.findall(body)):
            self.flags.add('RAW_RENDERER_LINK_DISAGREEMENT')
        return self

def inspect(meta, taxonomy_row, *, minimal_text=False):
    """Classified, bounded findings, never raw source URLs or prose."""
    if not isinstance(meta,dict) or not isinstance(taxonomy_row,dict):
        raise Blocked('MISSING_ARTICLE_OR_TAXONOMY')
    body=meta.get('_body')
    if not isinstance(body,str):
        raise Blocked('MISSING_BODY')
    p=Surface().result(body)
    status=meta.get('status')
    if type(status) is not dict or status.get('publish')!='draft' or status.get('editorial') not in VALID_STATUS:
        p.flags.add('CONTENT_PUBLICATION_STATE_DRIFT')
    safety=meta.get('safety_review')
    if type(safety) is not dict or safety.get('state') not in VALID_SAFETY:
        p.flags.add('SAFETY_REVIEW_STATE_DRIFT')
    if taxonomy_row.get('gate') is not True:
        p.flags.add('TAXONOMY_GATE_NOT_TRUE')
    if meta.get('slug')!=taxonomy_row.get('slug') or meta.get('section')!=taxonomy_row.get('section'):
        p.flags.add('SOURCE_ARTICLE_TAXONOMY_DRIFT')
    if meta.get('track')!=taxonomy_row.get('track'):
        p.flags.add('SOURCE_TRACK_TAXONOMY_DRIFT')
    if not p.visible_sources:
        p.flags.add('NO_READING_CONTEXT_SOURCE_TOKENS')
    return {'slug':taxonomy_row.get('slug'),
            'body_sha256_NOT_SIGNATURE':hashlib.sha256(body.encode()).hexdigest(),
            'readable_citation_occurrences':len(p.visible_sources),
            'source_ids':len(set(p.visible_sources)),
            'flags':sorted(p.flags),
            'human_claim_review':'NOT_REVIEWED','qualified_safety_review':'NOT_REVIEWED',
            'may_publish':False}

def scan(root):
    """Read existing build library and R114 report; no writes, no source approvals."""
    from importlib import util
    path=Path(root)/'preparedness/tools/build.py'
    if not path.is_file():raise Blocked('TRUSTED_BUILD_NOT_FOUND')
    spec=util.spec_from_file_location('r115_private_build',path)
    build=util.module_from_spec(spec);spec.loader.exec_module(build)
    lib=build.Library(Path(root)/'preparedness')
    slate=lib.taxonomy.get('slate')
    if not isinstance(slate,list) or len(slate)!=35 or {x.get('n') for x in slate}!=set(range(1,36)):
        raise Blocked('SLATE_CENSUS_DRIFT')
    entries=[]
    for row in sorted(slate,key=lambda x:x['n']):
        meta=lib.articles.get(row['slug'])
        if meta is None:raise Blocked('MISSING_ARTICLE_'+row['slug'])
        entries.append(inspect(meta,row))
    r114path=Path(root)/'preparedness/tools/r114_full_slate_rendered_citation_gate.py'
    s=util.spec_from_file_location('r114_gate',r114path)
    r114=util.module_from_spec(s);s.loader.exec_module(r114)
    prior=r114.audit_slate(lib.taxonomy,lib.articles,lib.source_for)
    if prior.get('slate_count')!=35 or prior.get('release_state')!='HOLD' or prior.get('may_publish') is not False:
        raise Blocked('R114_CUSTODY_FAILED_CLOSED')
    if [e['slug'] for e in entries]!=[e['slug'] for e in prior['rows_NOT_APPROVED']]:
        raise Blocked('R114_R115_ARTICLE_ROSTER_DRIFT')
    return {'schema':SCHEMA,'issue':136,'conversion_issue':820,'slate_count':35,
            'rows_NOT_APPROVED':entries,
            'new_risk_article_count':sum(bool(e['flags']) for e in entries),
            'r114_source_or_safety_verified':False,'independent_QD_PASS':False,
            'unreviewed_source_collision_groups':30,
            'release_state':'HOLD','may_merge':False,'may_publish':False,
            'cms_writes':False,'verified_paid_conversions':'UNOBSERVABLE'}

def main():
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--repo-root',default='.')
    args=a.parse_args()
    try:
        print(json.dumps(scan(args.repo_root),sort_keys=True,indent=2))
        return 0  # audit-only execution, not release PASS
    except (Blocked,ValueError,KeyError,TypeError,FileNotFoundError,AttributeError) as exc:
        print(json.dumps({'schema':SCHEMA,'release_state':'HOLD','may_publish':False,
                          'integrity':'FAILED_CLOSED','reason':str(exc)},sort_keys=True))
        return 2

if __name__=='__main__':raise SystemExit(main())
