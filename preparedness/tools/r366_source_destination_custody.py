#!/usr/bin/env python3
"""R366: read-only Preparedness source-destination, link and CTA custody.

Preserves source identities across all eight inventories; inspects original/candidate
outbound destinations and HTML-form actions for silent retargeting or unsafe schemes.
A structural result is NEVER human link verification, medical/emergency approval,
commerce acceptance, permission to publish, or proof of paid conversions.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from html.parser import HTMLParser
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit, urlunsplit

SCHEMA = 'fv-preparedness-r366-destination-custody-v1'
ORIGINAL = '02d344d9c1a1e9f68a2bcd6c0ab03859acf78232'
SOURCE_FILES = ('register.json','fragments/food.json','fragments/health.json',
 'fragments/hist-field.json','fragments/hist-food.json','fragments/hist-home.json',
 'fragments/shelter.json','fragments/start.json')
CITE = re.compile(r'\{\{cite:([a-z][a-z0-9-]*)\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
COMMERCE = re.compile(r'(?:checkout|buy-now|add-to-cart|payhip|gumroad|stripe|paypal|/cart(?:/|\?|$)|/product(?:/|\?|$))', re.I)
HOLD = dict(qd_pass=False, may_publish=False, may_merge=False, source_verified=False,
  medical_safety_verified=False, link_human_verified=False, paid_sku_verified=False,
  confirmed_order_verified=False, realized_net_revenue_verified=False)


def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d: raise ValueError('DUPLICATE_JSON_KEY')
        d[k] = v
    return d


def decode_json(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs)


def digest(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def valid_url(raw):
    """Return (normalized destination, error). Never coalesce source reading scopes."""
    if not isinstance(raw,str) or not raw or len(raw)>2048:
        return None, 'INVALID_URL_TYPE_OR_SIZE'
    if raw != raw.strip() or re.search(r'[\x00-\x20\x7f\\]',raw):
        return None, 'CONTROL_OR_WHITESPACE_IN_URL'
    try: u = urlsplit(raw)
    except ValueError: return None, 'MALFORMED_URL'
    if u.scheme.lower() != 'https' or not u.netloc:
        return None, 'NON_HTTPS_DESTINATION'
    if u.username is not None or u.password is not None:
        return None, 'EMBEDDED_CREDENTIALS'
    try: port = u.port
    except ValueError: return None, 'INVALID_PORT'
    if port is not None: return None, 'UNAPPROVED_PORT'
    host = u.hostname
    if not host or host.endswith('.') or '%' in host or host.lower() in ('localhost','localhost.localdomain'):
        return None, 'INVALID_OR_LOCAL_HOST'
    try:
        ipaddress.ip_address(host)
        return None, 'DIRECT_IP_DESTINATION'
    except ValueError: pass
    if not re.fullmatch(r'[a-z0-9.-]+',host.lower()) or '.' not in host or '..' in host:
        return None, 'INVALID_HOSTNAME'
    if u.fragment and CITE.search(u.fragment): return None, 'CITATION_IN_FRAGMENT'
    # Keep case, encoded path, query, fragment and slash *as supplied* for scope custody.
    return urlunsplit(('https',host.lower(),u.path or '/',u.query,u.fragment)), None


class Destinations(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.actions=[]; self.ids=[]; self.errors=[]
        self.scripts=0

    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':
            if not isinstance(a.get('href'),str): self.errors.append('LINK_MISSING_HREF')
            else: self.links.append(a['href'])
        if tag=='form': self.actions.append(a.get('action',''))
        if tag=='script': self.scripts+=1
        if isinstance(a.get('id'),str): self.ids.append(a['id'])
        for k,v in attrs:
            if k.lower().startswith('on') and isinstance(v,str):
                self.errors.append('INLINE_EVENT_HANDLER')
            if k in ('src','href','action') and isinstance(v,str) and re.search(r'[\x00-\x1f\x7f]',v):
                self.errors.append('CONTROL_IN_DESTINATION')

    def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs)


def extract(html):
    if not isinstance(html,str) or len(html)>500_000:
        raise ValueError('INVALID_HTML_SIZE')
    obj=Destinations();obj.feed(html);obj.close()
    return obj


def classify_href(raw, *, ids=()):
    if not isinstance(raw,str):return None, 'INVALID_HREF'
    if not raw or raw.startswith('//') or raw.startswith('\\'):
        return None, 'PROTOCOL_RELATIVE_OR_EMPTY'
    if raw.startswith('#'):
        fragment=raw[1:]
        if not fragment or fragment not in ids:
            return None, 'BROKEN_INTERNAL_ANCHOR'
        return 'anchor:'+fragment, None
    if raw.startswith('/'):
        if raw.startswith('/\\') or re.search(r'[\x00-\x20\x7f\\]',raw):
            return None, 'UNSAFE_RELATIVE_URL'
        if raw.startswith('/preparedness/') or raw == '/preparedness':
            return 'relative:'+raw, None
        return 'relative:'+raw, 'OFF_ARCHIVE_RELATIVE_REVIEW'
    target,error=valid_url(raw)
    if error:return None,error
    return 'external:'+target,None


def source_inventory(fragments):
    errors=[]; reviewed=[]; by_id=defaultdict(list); by_url=defaultdict(list)
    if not isinstance(fragments,dict) or set(fragments) != set(SOURCE_FILES):
        return {}, {}, ['SOURCE_FRAGMENT_SET_INCOMPLETE'], []
    for fname in SOURCE_FILES:
        records=fragments[fname]
        if not isinstance(records,list):
            errors.append('BAD_FRAGMENT:'+fname);continue
        for n,rec in enumerate(records):
            if not isinstance(rec,dict) or not isinstance(rec.get('id'),str) or not SLUG.fullmatch(rec['id']):
                errors.append('INVALID_SOURCE_ID:'+fname+':'+str(n)); continue
            url,err=valid_url(rec.get('url'))
            if err:errors.append('INVALID_SOURCE_URL:'+fname+':'+str(n)+':'+err);continue
            if not isinstance(rec.get('supports'),str) or not rec['supports'].strip():
                errors.append('MISSING_READING_SCOPE:'+fname+':'+str(n));continue
            row=(fname,n,rec['id'],rec['url'],rec['supports'])
            by_id[rec['id']].append(row);by_url[url].append(row)
            if rec.get('human_link_check') is True:
                reviewed.append('HUMAN_LINK_CHECK_ASSERTION_REQUIRES_INDEPENDENT_PROOF:'+rec['id'])
    for sid,rows in by_id.items():
        if len({(r[3],r[4]) for r in rows})>1:
            reviewed.append('SHARED_ID_SCOPE_ADJUDICATION:'+sid)
    return by_id,by_url,sorted(set(errors)),sorted(set(reviewed))


def compare_link_custody(old_html,new_html,source_urls):
    """Compare literal occurrence identities, never infer links were opened or safe."""
    errors=[];review=[]
    try: old=extract(old_html);new=extract(new_html)
    except (ValueError,TypeError) as e:return ['INVALID_HTML:'+type(e).__name__],[],{}
    errors += ['NEW_'+x for x in new.errors]
    if new.scripts>old.scripts: errors.append('NEW_EXECUTABLE_SCRIPT')
    if len(new.actions)>len(old.actions):errors.append('NEW_FORM_ACTION')
    for action in new.actions:
        if action and action not in ('#',):errors.append('FORM_ACTION_REQUIRES_PRIVATE_REVIEW')
    oc=Counter(old.links);nc=Counter(new.links)
    for href,n in oc.items():
        if nc[href]<n:errors.append('ORIGINAL_LINK_OCCURRENCE_REMOVED:'+digest(href)[:12])
    for href,n in nc.items():
        d,err=classify_href(href,ids=new.ids)
        if err:
            if err.endswith('_REVIEW'):review.append(err+':'+digest(href)[:12])
            else: errors.append('UNSAFE_DESTINATION:'+err+':'+digest(href)[:12])
        if n>oc[href]:
            review.append('NEW_LINK_REQUIRES_REVIEW:'+digest(href)[:12])
        if d and d.startswith('external:') and d[9:] not in source_urls:
            review.append('OUTBOUND_NOT_IN_REGISTER:'+digest(href)[:12])
        if COMMERCE.search(href):
            errors.append('COMMERCE_DESTINATION_UNVERIFIED:'+digest(href)[:12])
    # Counts protect against swapping two URLs that appear multiple times.
    return sorted(set(errors)),sorted(set(review)),{'old_links':len(old.links),
      'new_links':len(new.links),'old_unique':len(oc),'new_unique':len(nc),
      'old_href_multiset_sha256':digest(json.dumps(sorted(oc.items()))),
      'new_href_multiset_sha256':digest(json.dumps(sorted(nc.items()))) }


def report(errors,review=(),dockets=(),evidence=None):
    return dict(schema=SCHEMA,status='INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
        errors=sorted(set(errors)),human_review=sorted(set(review)),dockets=list(dockets),
        evidence=evidence or {},**HOLD)


def git(root,*args):
    env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'}
    r=subprocess.run(['git','-C',str(root),*args],env=env,capture_output=True,timeout=35)
    if r.returncode or len(r.stdout)>3_000_000:raise ValueError('GIT_OBJECT_MISSING_OR_OVERSIZED')
    return r.stdout.decode('utf-8')


def audit(root,candidate_ref='HEAD'):
    root=Path(root)
    if root.is_symlink() or not (root/'.git').exists():return report(['AUTHENTIC_GIT_CHECKOUT_REQUIRED'])
    if not isinstance(candidate_ref,str) or not re.fullmatch(r'[a-zA-Z0-9_./-]{1,120}',candidate_ref) or candidate_ref.startswith(('-', '/')) or '..' in candidate_ref:
        return report(['INVALID_GIT_REF'])
    try:
        sha=git(root,'rev-parse','--verify',candidate_ref+'^{commit}').strip()
        if git(root,'rev-parse','--verify',ORIGINAL+'^{commit}').strip()!=ORIGINAL:
            return report(['PINNED_ORIGINAL_MISSING'])
        def read(ref,path):return git(root,'show',ref+':'+path)
        fragments={}
        for fn in SOURCE_FILES:
            path='preparedness/sources/'+fn
            a=read(ORIGINAL,path);b=read(sha,path)
            if a!=b:return report(['SOURCE_CORPUS_CHANGED_WITHOUT_QD:'+fn])
            fragments[fn]=decode_json(a)['sources']
        by_id,by_url,errors,review=source_inventory(fragments)
        paths=git(root,'ls-tree','-r','--name-only',ORIGINAL,'--','preparedness/content').splitlines()
        cpaths=git(root,'ls-tree','-r','--name-only',sha,'--','preparedness/content').splitlines()
        good=lambda ps,k:sorted(p for p in ps if p.startswith('preparedness/content/'+k+'/') and p.endswith('.meta.json'))
        ms=good(paths,'articles')+good(paths,'tools')
        if len(good(paths,'articles'))!=35 or len(good(paths,'tools'))!=6 or ms!=good(cpaths,'articles')+good(cpaths,'tools'):
            return report(errors+['41_DOCUMENT_SET_DRIFT'],review)
        evidence=[];cite_ids=set(); slugs=set()
        for path in ms:
            p=path[:-10]+'.body.html'
            om=decode_json(read(ORIGINAL,path));cm=decode_json(read(sha,path))
            old=read(ORIGINAL,p);new=read(sha,p)
            slug=om.get('slug')
            if slug in slugs or not isinstance(slug,str):errors.append('DUPLICATE_SLUG_OR_BAD_META')
            slugs.add(slug)
            if cm.get('slug')!=slug:errors.append('SLUG_REASSIGNMENT:'+str(slug))
            if cm.get('status',{}).get('publish')!='draft':errors.append('NOT_A_DRAFT:'+str(slug))
            ids=set(CITE.findall(new));cite_ids.update(ids)
            for sid in ids:
                if sid not in by_id:errors.append('UNREGISTERED_CITATION_ID:'+sid)
            e,r,d=compare_link_custody(old,new,by_url)
            errors += [str(slug)+':'+x for x in e]
            review += [str(slug)+':'+x for x in r]
            evidence.append(dict(slug=slug,citation_ids=len(ids),**d))
        # The independent source-review backlog cannot be silently marked complete.
        return report(errors,review,evidence,{'original_ref':ORIGINAL,'candidate_ref':sha,
           'article_count':35,'tool_count':6,'source_rows':sum(map(len,fragments.values())),
           'source_literal_targets':len(by_url),'unique_cited_source_ids':len(cite_ids),
           'human_source_verification_performed':False,'revenue_verification_performed':False})
    except (OSError,TypeError,ValueError,UnicodeError,KeyError,subprocess.TimeoutExpired) as exc:
        return report(['NATIVE_GIT_AUDIT_UNAVAILABLE:'+type(exc).__name__])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--candidate-ref',default='HEAD')
    args=parser.parse_args()
    print(json.dumps(audit(args.repo_root,args.candidate_ref),sort_keys=True,indent=2))
    raise SystemExit(2) # Always HARD HOLD: even valid structural evidence is not QD PASS.
