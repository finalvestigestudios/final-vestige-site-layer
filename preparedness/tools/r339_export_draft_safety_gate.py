#!/usr/bin/env python3
"""R339: independently scan private 50-pair outputs for draft-link exposure.

Runs ONLY after authenticated R338 source custody and R330 native export parity.
Neither a successful scan nor synthetic fixtures confer publication/QD/sales approval.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from preparedness.tools import r338_frozen_link_graph_hold as source

SCHEMA = 'fv-preparedness-r339-private-export-links-v1'
WP = re.compile(r'\A<!-- wp:html -->\n<style>.*?</style>\n(?P<inner>.*)\n<!-- /wp:html -->\n?\Z', re.S)
PRE = re.compile(r'<body><main>(?P<inner>.*)</main></body></html>\s*\Z', re.S)
HOSTS = ('payhip.com', 'gumroad.com', 'checkout.stripe.com', 'buy.stripe.com', 'paypal.com', 'amzn.to', 'amazon.com')

class Parsed(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=set(); self.duplicates=[]; self.anchors=[]; self.forms=[]; self.fields=[]
        self.scripts=[]; self.ld=[]; self.in_ld=False; self.chunks=[]; self.active=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if len(attrs)!=len(d): self.active.append('DUPLICATE_ATTRIBUTE')
        if d.get('id'):
            if d['id'] in self.ids: self.duplicates.append(d['id'])
            self.ids.add(d['id'])
        if tag=='a': self.anchors.append(d.get('href'))
        if tag=='form': self.forms.append(d)
        if tag in ('input','select','textarea') and d.get('name'): self.fields.append(d['name'])
        if tag in ('iframe','embed','object'): self.active.append('UNREVIEWED_EMBED')
        if tag=='script':
            if d.get('src'): self.active.append('UNREVIEWED_SCRIPT_SRC')
            if d.get('type')=='application/ld+json': self.in_ld=True; self.chunks=[]
    def handle_data(self, data):
        if self.in_ld:self.chunks.append(data)
    def handle_endtag(self, tag):
        if tag=='script' and self.in_ld:
            self.ld.append(''.join(self.chunks)); self.in_ld=False; self.chunks=[]

def result(errors, documents=0, anchors=0, held=0, jsonld=0):
    return {'schema':SCHEMA, 'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
      'errors':sorted(set(errors)), 'private_export_pairs_inspected':documents,
      'anchor_occurrences':anchors, 'links_to_unpublished_family_tools':held,
      'article_jsonld_identities_inspected':jsonld, 'native_build_verified':False,
      'qualified_qd_pass':False, 'medical_emergency_safety_approved':False,
      'source_claim_support_approved':False, 'public_release_authorized':False,
      'realized_net_revenue_verified':False, 'may_merge':False, 'may_publish':False}

def check(routes:dict, sections:set, files:dict):
    """Pure testable preflight. Its result always remains a draft safety hold."""
    if not isinstance(routes,dict) or len(routes)!=41 or not isinstance(sections,set) or len(sections)!=8:
        return result(['AUTHENTIC_41_ROUTES_AND_EIGHT_SECTIONS_REQUIRED'])
    destinations={urlsplit(v).path:s for s,v in routes.items() if isinstance(v,str) and v.startswith('https://finalvestige.com/preparedness/')}
    if len(destinations)!=41: return result(['SOURCE_ROUTE_COLLISION_OR_DRIFT'])
    destinations.update({f'/preparedness/{s}/':f'hub-{s}' for s in sections})
    destinations['/preparedness/']='landing'
    names=set(destinations.values()); expected={f'{x}/{s}.html' for x in ('wp','preview') for s in names}
    errors=[]; parsed={}; outbound=[]; nanchors=held=njson=0
    if not isinstance(files,dict) or set(files)!=expected:errors.append('EXACT_50_WP_AND_50_PREVIEW_OUTPUTS_REQUIRED')
    for slug in sorted(names):
        wb=files.get(f'wp/{slug}.html') if isinstance(files,dict) else None
        pb=files.get(f'preview/{slug}.html') if isinstance(files,dict) else None
        if not isinstance(wb,bytes) or not isinstance(pb,bytes):errors.append('MISSING_PAIR:'+slug);continue
        try: w=WP.fullmatch(wb.decode('utf-8'));p=PRE.search(pb.decode('utf-8'))
        except UnicodeError:errors.append('INVALID_UTF8:'+slug);continue
        if not w or not p or w.group('inner')!=p.group('inner'):
            errors.append('WORDPRESS_PREVIEW_PARITY_FAILED:'+slug);continue
        if b'<meta name="robots" content="noindex,nofollow">' not in pb:errors.append('PRIVATE_PREVIEW_NOINDEX_MISSING:'+slug)
        dom=Parsed()
        try:dom.feed(w.group('inner'));dom.close()
        except (ValueError,TypeError):errors.append('INVALID_HTML:'+slug);continue
        parsed[slug]=dom
        if dom.duplicates:errors.append('DUPLICATE_HTML_ID:'+slug)
        for x in dom.active:errors.append(x+':'+slug)
        if slug in routes:
            if f'data-slug="{slug}"' not in w.group('inner'):errors.append('BODY_SOURCE_IDENTITY_DRIFT:'+slug)
            for marker in ('Draft: not public','Independent safety/source and QD verification pending'):
                if marker not in w.group('inner'):errors.append('UNSAFE_PUBLIC_APPROVAL_LANGUAGE_OR_MISSING_HOLD:'+slug)
            article=[]
            for txt in dom.ld:
                try: j=json.loads(txt)
                except ValueError:errors.append('BROKEN_JSONLD:'+slug);continue
                if isinstance(j,dict):article.extend(v for v in j.get('@graph',[]) if isinstance(v,dict) and v.get('@type')=='Article')
            if len(article)!=1:errors.append('MISSING_OR_DUPLICATE_ARTICLE_JSONLD:'+slug)
            else:
                njson+=1; a=article[0]
                if a.get('mainEntityOfPage')!=routes[slug] or a.get('@id')!=routes[slug]+'#article':errors.append('JSONLD_CANONICAL_SOURCE_DRIFT:'+slug)
                if a.get('isAccessibleForFree') is not True or 'offers' in a or 'datePublished' in a:errors.append('DRAFT_MUST_BE_FREE_AND_UNPUBLISHED:'+slug)
        for f in dom.forms:
            if f.get('action') not in (None,'','#'):errors.append('UNREVIEWED_FORM_ACTION:'+slug)
            if f.get('method','get').lower()=='get' and dom.fields:errors.append('POTENTIAL_NAMED_FORM_GET_EXPOSURE:'+slug)
        for href in dom.anchors:
            nanchors+=1
            if not href or href!=href.strip() or '\\' in href or any(ord(c)<32 for c in href):errors.append('INVALID_HREF:'+slug);continue
            if href.startswith('//'):errors.append('PROTOCOL_RELATIVE_LINK:'+slug);continue
            try:u=urlsplit(href)
            except ValueError:errors.append('MALFORMED_URL:'+slug);continue
            if u.scheme not in ('','https','http'):
                errors.append('UNREVIEWED_LINK_SCHEME:'+slug);continue
            host=(u.hostname or '').lower()
            if any(host==x or host.endswith('.'+x) for x in HOSTS):errors.append('UNAPPROVED_MERCHANT_LINK:'+slug)
            if host and host!='finalvestige.com':continue
            if host and u.scheme!='https':errors.append('INSECURE_SAME_SITE_LINK:'+slug)
            if not u.path and u.fragment:outbound.append((slug,slug,u.fragment));continue
            if u.path.startswith('/preparedness/'):
                if '%' in u.path or u.query:errors.append('ENCODED_OR_TAGGED_PRIVATE_ROUTE:'+slug);continue
                target=destinations.get(u.path)
                if not target:errors.append('UNRESOLVED_RENDERED_DESTINATION:'+slug+':'+u.path);continue
                outbound.append((slug,target,u.fragment))
                if target in ('family-reunification-card','reunification-plan'):held+=1
            elif u.path and not u.path.startswith('/'):
                errors.append('RELATIVE_PATH_NOT_CANONICAL:'+slug)
    for origin,target,fragment in outbound:
        if fragment and target in parsed and fragment not in parsed[target].ids:errors.append('BROKEN_FRAGMENT:'+origin+':'+target)
    return result(errors,len(parsed),nanchors,held,njson)

def audit_native(root:Path):
    root=root.resolve()
    prior=source.audit(root/'preparedness')
    if prior['state']!='DRAFT_HARD_HOLD':return result(['R338_FROZEN_SOURCE_REQUIRED']+prior.get('errors',[]))
    try:
        from preparedness.tools import r330_native_export_parity_hold as native
        n=native.read_native(root)
        if n['state']!='DRAFT_HARD_HOLD':return result(['R330_NATIVE_EXPORT_PARITY_REQUIRED']+n.get('errors',[]))
        from preparedness.tools import r319_three_way_custody_hold as custody
        manifest=json.loads((root/'preparedness/audits/r319_three_way_custody_manifest.json').read_text('utf-8'))
        tax=json.loads((root/'preparedness/taxonomy.json').read_text('utf-8'))
        routes=native.expected_from_source(manifest,tax)
        files={}
        for group in ('wp','preview'):
            for p in (root/'preparedness/build'/group).glob('*.html'):
                if p.is_symlink():return result(['UNTRUSTED_SYMLINK_EXPORT'])
                files[f'{group}/{p.name}']=p.read_bytes()
        return check(routes,{s['slug'] for s in tax['sections']},files)
    except (OSError,ValueError,ImportError,KeyError,TypeError):
        return result(['FULL_AUTHENTIC_NATIVE_CHECKOUT_REQUIRED'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    r=audit_native(p.parse_args().repo_root);print(json.dumps(r,indent=2,sort_keys=True))
    return 2 if r['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
