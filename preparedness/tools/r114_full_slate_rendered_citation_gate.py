#!/usr/bin/env python3
"""R114: read-only 35-article render/citation audit. ALWAYS HOLD; never a safety approval.

The archive renderer replaces cite/link tokens with regex over raw HTML. This
independent preflight rejects tokens in hidden, nonreading or attribute contexts
and checks the article-scoped source resolver before any WordPress draft import.
Original content, author/source records, CMS and production site stay untouched.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|([^{}]*)\}\}')
ANY = re.compile(r'\{\{[^{}]*\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
NONREAD = frozenset('script style template noscript iframe object svg canvas'.split())
HIDE_CLASS = frozenset('hidden is-hidden d-none visually-hidden screen-reader-text sr-only'.split())
BLOCKED_SCHEMES = re.compile(r'^\s*(?:javascript|data|vbscript|file):', re.I)
SCHEMA = 'fv-preparedness-r114-full-slate-render-audit-HOLD-v1'

class PreflightError(ValueError):
    pass

def require(value, message):
    if not value:
        raise PreflightError(message)

class CitationParser(HTMLParser):
    """Conservative source-token preflight, not a browser/AT visibility claim."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.visible_citations = []
        self.visible_links = []
        self.violations = []
        self.visible_text_length = 0
        self.content_blocks = 0
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        values = [(str(k).lower(), v) for k, v in attrs]
        for key, value in values:
            if value and ('{{cite:' in value or '{{link:' in value):
                self.violations.append('TOKEN_IN_HTML_ATTRIBUTE')
            if key == 'href' and value and BLOCKED_SCHEMES.match(value):
                self.violations.append('ACTIVE_LINK_SCHEME')
        if tag in NONREAD:
            self.violations.append('NONREADING_ACTIVE_ELEMENT')
        if d.get('id'):
            if d['id'] in self.ids:
                self.violations.append('DUPLICATE_HTML_ID')
            self.ids.add(d['id'])
        style = re.sub(r'\s+', '', (d.get('style') or '').lower())
        hidden = (tag in NONREAD or 'hidden' in d or 'inert' in d or
                  (d.get('aria-hidden') or '').lower() == 'true' or
                  bool(HIDE_CLASS.intersection((d.get('class') or '').split())) or
                  any(v in style for v in ('display:none', 'visibility:hidden', 'opacity:0',
                                           'content-visibility:hidden')) or
                  bool(self.stack and self.stack[-1][1]))
        if tag in ('p','li','h1','h2','h3','blockquote') and not hidden:
            self.content_blocks += 1
        if tag not in VOID:
            self.stack.append((tag, hidden))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.violations.append('HTML_NESTING_MISMATCH')
        else:
            self.stack.pop()

    def handle_data(self, data):
        citations = CITE.findall(data)
        links = LINK.findall(data)
        if self.stack and self.stack[-1][1]:
            if citations or links or '{{cite:' in data or '{{link:' in data:
                self.violations.append('TOKEN_IN_NONREADING_CONTENT')
            return
        self.visible_citations.extend(citations)
        self.visible_links.extend(slug for slug, _ in links)
        self.visible_text_length += len(data)
        for token in ANY.findall(data):
            if not CITE.fullmatch(token) and not LINK.fullmatch(token):
                self.violations.append('UNKNOWN_OR_MALFORMED_TOKEN')
        if '{{cite:' in data and len(citations) != data.count('{{cite:'):
            self.violations.append('MALFORMED_CITE_TOKEN')
        if '{{link:' in data and len(links) != data.count('{{link:'):
            self.violations.append('MALFORMED_LINK_TOKEN')

    def handle_comment(self, data):
        if '{{cite:' in data or '{{link:' in data:
            self.violations.append('TOKEN_IN_HTML_COMMENT')

    def finish(self, body):
        self.feed(body)
        self.close()
        if self.stack:
            self.violations.append('UNCLOSED_HTML')
        if len(self.visible_citations) != len(CITE.findall(body)):
            self.violations.append('RAW_RENDERER_CITATION_SCOPE_MISMATCH')
        if len(self.visible_links) != len(LINK.findall(body)):
            self.violations.append('RAW_RENDERER_LINK_SCOPE_MISMATCH')
        return self

def audit_article(slug, meta, known_routes, source_for):
    """Return bounded decisions, not prose, URLs, facts or positive safety claims."""
    problems = []
    require(isinstance(meta, dict) and type(meta.get('_body')) is str,
            'MISSING_OR_INVALID_ARTICLE_BODY')
    body = meta['_body']
    parser = CitationParser().finish(body)
    problems.extend(parser.violations)
    if not SLUG.fullmatch(slug) or meta.get('slug') != slug:
        problems.append('ARTICLE_IDENTITY_MISMATCH')
    source_use = meta.get('source_use')
    if not isinstance(source_use, dict):
        problems.append('AUTHOR_SOURCE_USE_MISSING')
        source_use = {}
    cites = set(parser.visible_citations)
    if not cites:
        problems.append('NO_VISIBLE_CITATIONS')
    for sid in sorted(cites):
        if not isinstance(source_use.get(sid), str) or not source_use[sid].strip():
            problems.append('AUTHOR_SOURCE_SCOPE_MISSING')
        try:
            source = source_for(meta, sid)
        except (KeyError, ValueError, TypeError):
            problems.append('AUTHOR_SCOPED_SOURCE_UNRESOLVED')
            continue
        if not isinstance(source, dict) or source.get('id') != sid:
            problems.append('AUTHOR_SCOPED_SOURCE_ID_MISMATCH')
        elif not source.get('verified_on'):
            problems.append('SOURCE_REQUIRES_HUMAN_VERIFICATION')
    for target in parser.visible_links:
        if target not in known_routes:
            problems.append('UNREGISTERED_RELATED_ARTICLE_LINK')
        elif known_routes[target] is False:
            # Existing renderer degrades this target to plain text (not a dead URL).
            problems.append('RELATED_ARTICLE_NOT_YET_BUILDABLE')
    review = meta.get('safety_review')
    if not isinstance(review, dict) or not review.get('state'):
        problems.append('SAFETY_REVIEW_RECORD_MISSING')
    if not isinstance(review, dict) or review.get('state') != 'approved':
        problems.append('QUALIFIED_SAFETY_REVIEW_NOT_ESTABLISHED')
    if parser.visible_text_length < 3000 or parser.content_blocks < 12:
        problems.append('READING_DEPTH_REVIEW_REQUIRED')
    return {'slug':slug,'body_sha256_NOT_SIGNATURE':hashlib.sha256(body.encode()).hexdigest(),
            'visible_citation_occurrences':len(parser.visible_citations),
            'distinct_author_source_ids':len(cites),
            'content_blocks':parser.content_blocks,
            'safety_review_state_REPORTED_NOT_VERIFIED':review.get('state') if isinstance(review, dict) else None,
            'review_flags':sorted(set(problems)), 'may_publish':False,
            'author_support_verified':False}

def audit_slate(taxonomy, articles, resolver):
    """Census of all 35 article URLs, plus separate complete tool census."""
    require(isinstance(taxonomy,dict) and taxonomy.get('base_path') == '/preparedness/',
            'TAXONOMY_BASE_PATH_DRIFT')
    slate = taxonomy.get('slate')
    require(isinstance(slate,list) and len(slate) == 35 and
            all(isinstance(row,dict) for row in slate), 'EXPECTED_35_SLATE_ROWS')
    require({row.get('n') for row in slate} == set(range(1,36)),
            'SLATE_NUMBERS_MISSING_OR_DUPLICATED')
    routes = {}
    urlpaths = set()
    for row in slate:
        slug, section = row.get('slug'),row.get('section')
        require(isinstance(slug,str) and isinstance(section,str) and
                SLUG.fullmatch(slug) and SLUG.fullmatch(section),
                'UNSAFE_ROUTE_COMPONENT')
        url = f'/preparedness/{section}/{slug}/'
        require(slug not in routes and url not in urlpaths,
                'DUPLICATE_OR_COLLIDING_ARTICLE_URL')
        routes[slug] = slug in articles
        urlpaths.add(url)
    rows=[]
    for row in sorted(slate,key=lambda r:r['n']):
        slug=row['slug']
        meta=articles.get(slug)
        if meta is None:
            rows.append({'slug':slug,'review_flags':['MISSING_ARTICLE_DRAFT'],
                         'may_publish':False,'author_support_verified':False})
        elif not isinstance(meta,dict):
            rows.append({'slug':slug,'review_flags':['MALFORMED_ARTICLE_DRAFT'],
                         'may_publish':False,'author_support_verified':False})
        else:
            item=audit_article(slug,meta,routes,resolver)
            if meta.get('section') != row['section'] or meta.get('track') != row.get('track'):
                item['review_flags']=sorted(set(item['review_flags']+['TAXONOMY_METADATA_DRIFT']))
            rows.append(item)
    other=[key for key in articles if key not in routes]
    extra_tools=[key for key in other if articles[key].get('kind')=='tool']
    require(len(extra_tools) == 1 and len(other) == 1, 'EXPECTED_ONE_COMPLETE_TOOL_AND_35_ARTICLES')
    output={'schema':SCHEMA,'source_issue':136,'business_issues':[818,820],
            'slate_count':len(slate),'article_drafts_found':sum(bool(routes[k]) for k in routes),
            'complete_tool_count':len(extra_tools),
            'rows_NOT_APPROVED':rows,
            'unresolved_article_count':sum(bool(row['review_flags']) for row in rows),
            'source_or_safety_review_verified':False,'independent_QD_PASS':False,
            'release_state':'HOLD','may_publish':False,'may_merge':False,
            'wordpress_changed':False,'merchant_verified':False,
            'actual_commercial_conversion':'NOT_OBSERVED'}
    output['sha256_NOT_SIGNATURE']=hashlib.sha256(json.dumps(
        output,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    return output

def check_checkout(repo_root):
    from importlib import util
    path=Path(repo_root)/'preparedness/tools/build.py'
    require(path.is_file(),'REPOSITORY_BUILD_MODULE_UNAVAILABLE')
    spec=util.spec_from_file_location('r114_private_build',path)
    build=util.module_from_spec(spec)
    spec.loader.exec_module(build)
    lib=build.Library(Path(repo_root)/'preparedness')
    return audit_slate(lib.taxonomy,lib.articles,lib.source_for)

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--repo-root',default='.')
    args=p.parse_args()
    try:
        print(json.dumps(check_checkout(args.repo_root),sort_keys=True,indent=2))
        return 0  # Audit completed, NOT safety or release approval.
    except (PreflightError,ValueError,KeyError,FileNotFoundError,TypeError) as exc:
        print(json.dumps({'schema':SCHEMA,'release_state':'HOLD',
                          'integrity':'FAILED_CLOSED','reason':str(exc),
                          'may_publish':False},sort_keys=True))
        return 2

if __name__=='__main__':
    raise SystemExit(main())
